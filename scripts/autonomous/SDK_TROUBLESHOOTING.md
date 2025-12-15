# Claude Code SDK Troubleshooting

This guide covers common issues when using the SDK-based autonomous runner.

## Write Tool Not Creating Files

**Symptoms:**
- Claude attempts Write operations (visible in logs)
- Logs show: `→ Writing to: /path/to/file.py (XXXXX chars)`
- Files are NOT created on disk
- No error messages

**Root Cause:**
Missing `allowed_tools` parameter in `ClaudeCodeOptions` configuration.

**Fix:**
Explicitly configure allowed tools in `runner_sdk.py`:

```python
options = ClaudeCodeOptions(
    model=model,
    system_prompt=system_prompt,
    cwd=project_dir,
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash", "TodoWrite"],  # ← Required!
    mcp_servers=mcp_servers
)
```

**Verification:**
Check logs for:
```
SDK configured with tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash', 'TodoWrite']
```

If this line is missing or `allowed_tools` is empty, the Write tool will fail silently.

---

## Turn Limit Not Enforced

**Symptoms:**
- Tasks running beyond `max_turns_per_task` setting
- Expected: task stops after N turns
- Actual: continues indefinitely

**Investigation Steps:**

1. **Add turn count logging** to verify actual turns used:
```python
self.logger.info(f"Turn {turns}/{self.config.max_turns_per_task}")
```

2. **Check if completion marker is being detected:**
```python
if self._is_task_complete(full_text):
    self.logger.info("✓ Completion marker detected")
    success = True
    break
else:
    self.logger.debug("Completion marker not found")
```

**Typical Issue:**
Claude finishing work without explicit "TASK COMPLETE" marker.

**Fix:**
Update system prompt to require explicit completion marker (see "Update System Prompt" section below).

---

## Missing Completion Marker Detection

**Symptoms:**
- Task completes work successfully
- Claude doesn't include "TASK COMPLETE" in response
- Runner marks task as failed with `error=None`

**Root Cause:**
Completion detection relies on explicit markers like "task complete" or "successfully completed".

**Fix:**
The SDK runner includes completion marker detection:

```python
# After try-except block in _execute_task
if not success and error is None:
    error = "Task did not complete - no completion marker found in response. Claude may have finished work without explicitly stating 'TASK COMPLETE'."
    self.logger.warning(error)
```

**Workaround:**
1. Update task prompt to remind Claude to use marker:
```python
prompt_parts.extend([
    "",
    "**CRITICAL**: You MUST explicitly state \"TASK COMPLETE\" in your final message when you finish.",
])
```

2. Update system prompt template (see below).

---

## OAuth Token Issues

**Symptoms:**
- `No OAuth token found` errors
- SDK fails to authenticate

**Resolution:**

### Option 1: Set Environment Variable
```bash
export CLAUDE_CODE_OAUTH_TOKEN=your_token
```

### Option 2: Use Claude CLI Credentials
The SDK automatically uses Claude CLI credentials. Ensure Claude CLI is authenticated:

```bash
# Check authentication
claude whoami

# If not logged in
claude setup-token
```

**Verification:**
```python
# SDK automatically detects credentials from:
# 1. CLAUDE_CODE_OAUTH_TOKEN environment variable
# 2. ~/.claude.json (Claude CLI config)
```

---

## Initialization Timeout (First Task)

**Symptoms:**
- First task in session fails with: `Control request timeout: initialize`
- Subsequent tasks work fine
- Timeout occurs around 60 seconds

**Root Cause:**
First task may timeout during SDK initialization (especially on slower connections or cold starts).

**Fix:**
The SDK runner includes automatic retry logic:

```python
max_retries = 1

for attempt in range(max_retries + 1):
    try:
        async with self.sdk_client:
            await self.sdk_client.query(prompt)
            # ... streaming ...
            break  # Success

    except Exception as e:
        error_msg = str(e)

        # Retry on initialization timeout
        if "Control request timeout: initialize" in error_msg and attempt < max_retries:
            self.logger.warning(f"Initialization timeout, retrying...")
            if self.provider:
                self.provider.update_task(task.id, {"status": TaskStatus.TODO})
            continue

        # Other errors - fail
        return TaskResult(task_id=task.id, success=False, error=str(e))
```

**Expected Behavior:**
- First task: May timeout once (60s), then retry and succeed
- Subsequent tasks: Work normally
- After first success: Connection stable

---

## Runner Continues After Task Failure

**Problem:**
Runner proceeds to next task even when previous task fails, causing dependent tasks to fail.

**Context:**
- Task dependencies (e.g., `[PROJECT-1.2]` creates callback, `[PROJECT-1.3]` adds metrics to it)
- If `[PROJECT-1.2]` fails but `[PROJECT-1.3]` runs anyway, `[PROJECT-1.3]` will also fail
- Creates cascading failures and wastes resources

**Fix:**
The SDK runner implements stop-on-failure pattern:

```python
if result.success:
    tasks_completed += 1
    self.logger.info(f"Task {task.id} completed successfully")
else:
    # CRITICAL FIX: Stop on failure
    self.logger.error(f"Task {task.id} failed: {result.error}")
    self.logger.error("Stopping runner - cannot proceed with failed task")
    self.state = RunnerState.ERROR
    break  # Exit loop immediately
```

**Why This Fix Is Critical:**
- Prevents dependent tasks from running with missing prerequisites
- Ensures data integrity (don't add metrics to non-existent callback)
- Stops wasting compute resources on doomed tasks
- Forces manual intervention to fix failed tasks before proceeding

---

## Linear MCP Integration Issues

**Symptoms:**
- SDK runner can't access Linear API
- Linear tasks not updating
- MCP server errors in logs

**Fix:**
Ensure Linear API key is configured:

```bash
export LINEAR_API_KEY='lin_api_...'
```

Verify MCP configuration in runner:
```python
linear_api_key = os.getenv(self.config.linear_api_key_env)

if linear_api_key:
    mcp_servers["linear"] = {
        "type": "http",
        "url": "https://mcp.linear.app/mcp",
        "headers": {"Authorization": f"Bearer {linear_api_key}"}
    }
```

**Verification:**
Check logs for:
```
Configured Linear MCP server
```

---

## Progress Updates Not Posting

**Symptoms:**
- Claude generates progress updates
- Updates not appearing in Linear
- `[PROGRESS]` markers in logs but no Linear comments

**Root Cause:**
1. Progress update extraction not working
2. Linear provider not configured
3. MCP integration issue

**Debug Steps:**

1. **Check for `[PROGRESS]` markers in response:**
```python
self.logger.debug(f"Full response: {text}")
```

2. **Verify extraction pattern:**
```python
progress_lines = re.findall(r'^\[PROGRESS\]\s*(.+)', text, re.MULTILINE)
if progress_lines:
    self.logger.info(f"Found {len(progress_lines)} progress updates")
```

3. **Verify Linear provider is active:**
```python
if self.provider:
    self.logger.info(f"Provider: {type(self.provider).__name__}")
else:
    self.logger.warning("No provider configured!")
```

---

## Async/Await Errors

**Symptoms:**
- `RuntimeError: coroutine was never awaited`
- `TypeError: object async_generator can't be used in 'await' expression`

**Common Mistakes:**

### 1. Not using `await` with async functions
```python
# ✗ Wrong
result = self._execute_task(task)

# ✓ Correct
result = await self._execute_task(task)
```

### 2. Not using `async def` for coroutines
```python
# ✗ Wrong
def _execute_task(self, task):
    await self.sdk_client.query(prompt)

# ✓ Correct
async def _execute_task(self, task):
    await self.sdk_client.query(prompt)
```

### 3. Not using `asyncio.run()` in main
```python
# ✗ Wrong
if __name__ == "__main__":
    runner.start()

# ✓ Correct
if __name__ == "__main__":
    asyncio.run(runner.start())
```

---

## Performance Issues

### Task Taking Too Long

**Investigation:**
1. Check turn count - is it hitting max_turns limit?
2. Review task complexity - does it need more turns?
3. Check if Claude is stuck in a loop

**Fix:**
Increase `max_turns_per_task` in config:
```yaml
autonomous:
  max_turns_per_task: 150  # Increased from 50
```

### High Memory Usage

**Symptoms:**
- Python process using excessive RAM
- System slowdown during execution

**Investigation:**
1. Check if full_response_parts is growing too large
2. Review logging verbosity

**Fix:**
1. Limit response storage:
```python
# Only keep last N response parts
if len(full_response_parts) > 100:
    full_response_parts = full_response_parts[-50:]
```

2. Reduce logging:
```yaml
autonomous:
  log_level: "INFO"  # Change from DEBUG
```

---

## Reference Implementation

See working example in production projects:
- [Linear-Coding-Agent-Harness](https://github.com/coleam00/Linear-Coding-Agent-Harness)
- [Claude SDK Migration Guide](../../.ai-agents/library/guides/claude-sdk-migration.md)

---

## Getting Help

If you encounter issues not covered here:

1. **Check logs** at `.ai-agents/logs/autonomous.log`
2. **Enable debug logging:**
   ```yaml
   autonomous:
     log_level: "DEBUG"
   ```
3. **Review SDK documentation:** https://github.com/anthropics/claude-code-sdk
4. **File an issue:** https://github.com/anthropics/claude-code/issues

---

**Last Updated:** 2025-12-15
**SDK Version:** claude-code-sdk>=0.0.25
