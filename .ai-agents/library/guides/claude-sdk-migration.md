# Migrating Autonomous Agents to Claude Code SDK

**Status:** Production-Ready
**Version:** 1.0
**Last Updated:** 2025-12-15

## Overview

This guide covers migrating autonomous agents from the Claude Code CLI subprocess approach to the Claude Agent SDK. The SDK provides real-time streaming, better error handling, and direct MCP server integration.

## Benefits

| Feature | CLI Approach | SDK Approach |
|---------|--------------|--------------|
| **Streaming** | ❌ Blocking subprocess | ✅ Real-time async streaming |
| **Progress Updates** | ❌ Batch at end | ✅ Posted as they happen |
| **Tool Visibility** | ❌ Silent execution | ✅ Real-time tool use logs |
| **Error Messages** | ❌ Cryptic stderr | ✅ Detailed stack traces |
| **Linear Integration** | ❌ Separate API calls | ✅ Direct MCP access |
| **Performance** | ❌ 30min timeout risk | ✅ No blocking wait |
| **Debugging** | ❌ Post-mortem only | ✅ Real-time visibility |

## Architecture Comparison

### CLI-Based (Old)

```python
# scripts/autonomous/runner.py
def _call_claude_code(self, prompt: str) -> str:
    """Blocking subprocess call"""
    cmd = ["/usr/local/bin/claude", "-p", "--output-format", "text"]
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=1800
    )
    return result.stdout.strip()
```

**Problems:**
- Blocking subprocess - no streaming
- Progress updates only at end
- Silent tool execution
- Poor error messages
- 30-minute timeout limit

### SDK-Based (New)

```python
# scripts/autonomous/runner_sdk.py
from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import AssistantMessage, TextBlock, ToolUseBlock

async def _execute_task(self, task: Task) -> TaskResult:
    """Non-blocking async streaming"""
    self.sdk_client = self._create_sdk_client()

    async with self.sdk_client:
        await self.sdk_client.query(initial_prompt)

        async for msg in self.sdk_client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        # Post progress updates in real-time
                        await self._post_progress_updates(task.id, block.text)

                    elif isinstance(block, ToolUseBlock):
                        # Log tool use immediately
                        self.provider.add_task_comment(
                            task.id,
                            f"🔧 **Tool Used:** `{block.name}`"
                        )
```

**Benefits:**
- Async streaming - responses arrive in real-time
- Progress updates posted immediately
- Tool use visibility
- Detailed error messages
- Proper cleanup with context managers

## Installation

```bash
pip install claude-code-sdk>=0.0.25
```

Verify installation:
```bash
python -c "from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient; print('✓ SDK installed')"
```

## Implementation Guide

### 1. SDK Client Configuration

```python
def _create_sdk_client(self) -> ClaudeSDKClient:
    """Create SDK client with MCP configuration"""
    # SDK automatically uses Claude CLI credentials
    # No need to manually extract OAuth token

    linear_api_key = os.getenv("LINEAR_API_KEY")

    # Configure MCP servers
    mcp_servers = {}
    if linear_api_key:
        mcp_servers["linear"] = {
            "type": "http",
            "url": "https://mcp.linear.app/mcp",
            "headers": {"Authorization": f"Bearer {linear_api_key}"}
        }

    # Create client options
    options = ClaudeCodeOptions(
        model=self.config.model,
        cwd=self.config.project_dir,  # Use 'cwd', not 'project_dir'
        mcp_servers=mcp_servers
    )

    return ClaudeSDKClient(options)
```

**Key Points:**
- SDK automatically uses Claude CLI credentials
- Use `cwd` parameter, not `project_dir`
- Configure Linear MCP for direct API access
- MCP enables Claude to directly query/update Linear

### 2. Async Task Execution

```python
async def _execute_task(self, task: Task) -> TaskResult:
    """Execute task with async streaming"""
    # Mark task as in progress
    if self.provider:
        self.provider.update_task(task.id, {"status": TaskStatus.IN_PROGRESS})

    # Create SDK client
    self.sdk_client = self._create_sdk_client()

    turns = 0
    full_response_parts = []
    success = False
    error = None

    try:
        async with self.sdk_client:
            # Send initial prompt
            await self.sdk_client.query(initial_prompt)

            # Stream responses
            async for msg in self.sdk_client.receive_response():
                if isinstance(msg, AssistantMessage):
                    turns += 1

                    # Process message content
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text = block.text
                            full_response_parts.append(text)

                            # Post progress updates in real-time
                            await self._post_progress_updates(task.id, text)

                        elif isinstance(block, ToolUseBlock):
                            # Log tool use
                            if self.provider:
                                self.provider.add_task_comment(
                                    task.id,
                                    f"🔧 **Tool Used:** `{block.name}`"
                                )

                    # Check completion after each message
                    full_text = "\n".join(full_response_parts)
                    if self._is_task_complete(full_text):
                        success = True
                        break

    except Exception as e:
        self.logger.error(f"SDK execution error: {type(e).__name__}: {e}")
        error = str(e)

    return TaskResult(
        task_id=task.id,
        success=success,
        turns_used=turns,
        output="\n\n---\n\n".join(full_response_parts),
        error=error
    )
```

### 3. Real-Time Progress Updates

```python
async def _post_progress_updates(self, task_id: str, text: str):
    """Extract and post progress updates to Linear"""
    import re

    # Find [PROGRESS] markers
    progress_lines = re.findall(r'^\[PROGRESS\]\s*(.+)', text, re.MULTILINE)

    if progress_lines and self.provider:
        for update in progress_lines:
            comment = f"🤖 **Progress Update:**\n{update}"
            self.provider.add_task_comment(task.id, comment)
            self.logger.info(f"Posted progress: {update}")
```

### 4. Main Runner Loop

```python
async def start(self):
    """Start autonomous execution loop"""
    self.state = RunnerState.RUNNING
    tasks_completed = 0

    while (self.state == RunnerState.RUNNING and
           tasks_completed < self.config.max_tasks_per_session):

        # Get next task
        task = self._get_next_task()
        if not task:
            break

        # Execute task (async)
        result = await self._execute_task(task)

        # Update status
        self._update_task_status(task, result)

        if result.success:
            tasks_completed += 1

        # Pause between tasks
        if self.state == RunnerState.RUNNING:
            await asyncio.sleep(self.config.pause_between_tasks)
```

### 5. Entry Point

```python
async def main():
    """Async main entry point"""
    config = RunnerConfig.from_yaml(".ai-agents/config.yml")
    runner = AutonomousRunnerSDK(config)

    try:
        await runner.start()
    except KeyboardInterrupt:
        runner.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Issues and Solutions

### Issue 1: OAuth Token Not Found

**Error:** `Missing CLAUDE_CODE_OAUTH_TOKEN environment variable`

**Solution:** SDK automatically uses Claude CLI credentials. Ensure CLI is authenticated:
```bash
claude whoami  # Should show logged in user
```

### Issue 2: Wrong Parameter Names

**Error:** `ClaudeCodeOptions.__init__() got an unexpected keyword argument 'project_dir'`

**Solution:** Use `cwd` instead of `project_dir`:
```python
options = ClaudeCodeOptions(
    cwd=project_dir,  # ✓ Correct
    # project_dir=project_dir,  # ✗ Wrong
)
```

### Issue 3: Initialization Timeout (First Task)

**Error:** `Control request timeout: initialize`

**Cause:** First task in a session may timeout (60s) during initialization.

**Solution:** Implement automatic retry:
```python
async def _execute_task(self, task: Task) -> TaskResult:
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
- First task: May timeout during initialization (60s)
- Subsequent tasks: Work normally
- After first success: Connection stable

### Issue 4: Task Prompt Building Errors

**Error:** `TypeError: sequence item X: expected str instance, list found`

**Solution:** Format lists properly:
```python
if task.acceptance_criteria:
    prompt_parts.extend([
        "",
        "## Acceptance Criteria",
        *[f"- [ ] {criterion}" for criterion in task.acceptance_criteria]
    ])

if task.test_steps:
    prompt_parts.extend([
        "",
        "## Test Steps",
        *[f"{i+1}. {step}" for i, step in enumerate(task.test_steps)]
    ])
```

## Migration Checklist

### Files to Create

- [ ] `scripts/autonomous/runner_sdk.py` - New SDK-based runner
- [ ] `tests/test_runner_sdk.py` - SDK runner tests

### Code Changes

1. **Add imports:**
```python
from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import AssistantMessage, UserMessage, TextBlock, ToolUseBlock
```

2. **Make methods async:**
```python
async def start(self) -> None
async def _execute_task(self, task: Task) -> TaskResult
async def _post_progress_updates(self, task_id: str, text: str) -> None
```

3. **Update entry point:**
```python
async def main():
    runner = AutonomousRunnerSDK(config)
    await runner.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration Updates

1. **Add SDK dependency:**
```txt
# requirements.txt
claude-code-sdk>=0.0.25
```

2. **Update config.yml:**
```yaml
autonomous:
  # New SDK backend option
  backend: "claude-sdk"  # or "claude-code" for CLI
  model: "opus"
  max_tokens: 8192
```

### Testing

1. **Install SDK:**
```bash
pip install claude-code-sdk>=0.0.25
```

2. **Verify imports:**
```bash
python -c "from claude_code_sdk import ClaudeCodeOptions; print('✓ SDK ready')"
```

3. **Test with single task:**
```python
config = RunnerConfig(
    max_tasks_per_session=1,  # Test 1 task first
    log_level="DEBUG"
)
```

4. **Monitor logs for:**
- ✓ "Creating Claude SDK client (using CLI credentials)"
- ✓ "Configured Linear MCP server"
- ✓ "Tool use: ToolName"
- ✓ "Received text block: X chars"
- ✓ "Posted progress: ..."

## When to Use SDK vs CLI

### Use SDK When:
- Need real-time progress updates
- Want tool use visibility
- Debugging complex tasks
- Using Linear MCP integration
- Running long-running tasks (>30min)
- Need detailed error messages

### Use CLI When:
- Simple one-off tasks
- No need for real-time updates
- Prefer simpler subprocess model
- Testing/development
- Backward compatibility needed

## Best Practices

1. **Always use async/await:**
```python
# ✓ Correct
async def main():
    await runner.start()

# ✗ Wrong
def main():
    runner.start()  # Won't work - not async
```

2. **Use context managers:**
```python
# ✓ Correct
async with self.sdk_client:
    await self.sdk_client.query(prompt)

# ✗ Wrong
await self.sdk_client.query(prompt)
# Doesn't properly cleanup
```

3. **Handle initialization timeouts:**
```python
# ✓ Correct - retry once
for attempt in range(2):
    try:
        async with self.sdk_client:
            ...
            break
    except Exception as e:
        if "initialize" in str(e) and attempt < 1:
            continue
        raise
```

4. **Post progress updates:**
```python
# ✓ Correct - extract and post in real-time
async for msg in self.sdk_client.receive_response():
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                await self._post_progress_updates(task.id, block.text)
```

## Next Steps

1. **Create SDK runner template** in `scripts/autonomous/runner_sdk.py`
2. **Update documentation** to reference SDK option
3. **Add example project** using SDK pattern
4. **Create migration script** to convert CLI → SDK
5. **Update CHEAT_SHEET** with SDK commands

## Reference Implementation

See working example in production projects:
- `projects/trading-signal-ai/scripts/autonomous/runner_sdk.py`

This implementation includes:
- Async streaming architecture
- Real-time progress updates
- Linear MCP integration
- Comprehensive error handling
- Debug logging
- Task dependency management

## Questions?

- **SDK vs CLI?** SDK for production, CLI for simple testing
- **Backward compatibility?** Keep both, let users choose
- **MCP configuration?** Linear is most common, add others as needed
- **Migration timeline?** Gradual - SDK is optional, not required

---

**Generated:** 2025-12-15
**Tested On:** trading-signal-ai project
**SDK Version:** claude-code-sdk>=0.0.25
