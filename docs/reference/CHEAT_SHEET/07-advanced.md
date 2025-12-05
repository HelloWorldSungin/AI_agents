# Advanced Features

Advanced optimization patterns for token reduction and cost efficiency.

---

## Overview

Three optimization patterns from Anthropic's research on [Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use):

| Pattern | Token Savings | Use Case |
|---------|---------------|----------|
| Deferred Skill Loading | 85% reduction | Large skill libraries (10+ skills) |
| Prompt Caching | API cost savings | Repeated operations with stable prompts |
| Programmatic Tool Calling | 37% reduction | Multi-step workflows with many tool calls |

**New in:** v1.2.0

---

## 1. Deferred Skill Loading

**Token Savings:** 85% reduction in initial prompt size

### Problem

Loading all skills upfront consumes massive token budget:
- 10 skills × 3,500 tokens = 35,000 tokens
- Leaves little room for actual work

### Solution

Load skills on-demand via trigger words:
- Initial prompt: Only skill names (~1,500 tokens)
- Trigger word detected: Load specific skill dynamically
- Result: 85% reduction in at-rest tokens

### Configuration

**config.yml format:**
```yaml
agents:
  developer:
    skills:
      always_loaded:
        - "core/skill-creator"        # Always in context
      deferred:
        - path: "testing/webapp-testing"
          triggers: ["test", "QA", "coverage", "playwright", "e2e"]
        - path: "design/frontend-design"
          triggers: ["design", "UI", "component", "style"]
        - path: "documents/pdf"
          triggers: ["pdf", "report", "document"]
```

### How It Works

1. **Agent starts:** Only skill names loaded (~50 tokens per skill)
2. **User mentions "test":** `webapp-testing` skill loads dynamically (~4,000 tokens)
3. **Agent completes:** Skill remains for session
4. **Next session:** Back to minimal load

### Example

**Without Deferred Loading:**
```
Initial context: 35,000 tokens (10 skills loaded)
Remaining budget: 15,000 tokens for work
```

**With Deferred Loading:**
```
Initial context: 1,500 tokens (10 skill names)
User: "Write tests for login"
↓ "test" trigger detected
Context: 5,500 tokens (names + webapp-testing)
Remaining budget: 44,500 tokens for work
```

### Tool

**Location:** `tools/skill-search.md`

**Usage:**
- Integrated into agent composition
- Automatic trigger detection
- Manual override: "Load the webapp-testing skill"

### Best For

- Large skill libraries (10+ skills)
- Agents that might need various skills
- Keeping initial context lean
- Maximizing working memory

---

## 2. Prompt Caching

**Savings:** Reduced API costs for repeated operations

### Problem

Sending same prompt components repeatedly wastes cost and latency:
- System prompt: Same for all requests
- Base agent prompt: Rarely changes
- Context files: Stable between sessions

### Solution

Cache stable prompt components for 5 minutes:
- First request: Full cost
- Cached requests: Only fresh content charged
- Result: 50-90% cost reduction for repeated ops

### Implementation

**Using prompt_cache.py:**
```python
from scripts.orchestration.prompt_cache import CachedAnthropicClient

# Initialize client
client = CachedAnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])

# Call with caching
response, cache_info = client.call_with_cache(
    system_prompt=system_prompt,  # Cached (stable)
    messages=messages             # Fresh (dynamic)
)

# Check cache status
print(f"Cache hit: {cache_info['hit']}")
print(f"Tokens cached: {cache_info['tokens']}")
```

### What to Cache

**Good candidates:**
- System prompts
- Base agent prompts
- Context files (architecture, API contracts)
- Skill definitions
- Examples and references

**Bad candidates:**
- User messages (always fresh)
- Agent responses (always fresh)
- State files (change frequently)

### Cost Comparison

**Without Caching:**
```
Request 1: 20,000 tokens × $3/MTok = $0.06
Request 2: 20,000 tokens × $3/MTok = $0.06
Request 3: 20,000 tokens × $3/MTok = $0.06
Total: $0.18
```

**With Caching (15K cached, 5K fresh):**
```
Request 1: 20,000 tokens × $3/MTok = $0.06
Request 2: 5,000 tokens × $3/MTok = $0.015 (cached: $0.003)
Request 3: 5,000 tokens × $3/MTok = $0.015 (cached: $0.003)
Total: $0.096 (47% savings)
```

### Script

**Location:** `scripts/orchestration/prompt_cache.py`

**Usage:**
```bash
# Test prompt caching
python3 scripts/orchestration/prompt_cache.py
```

### Best For

- Repeated operations (code review, testing)
- Batch processing
- Multi-turn conversations
- CI/CD pipelines

---

## 3. Programmatic Tool Calling

**Token Savings:** 37% reduction per workflow

### Problem

Traditional tool calling is verbose:
- N tool calls = N inference passes
- Each result added to context
- Context grows rapidly

**Example:**
```
Turn 1: "Read file A" → result (1,000 tokens)
Turn 2: "Search in file A" → result (500 tokens)
Turn 3: "Read file B" → result (1,200 tokens)
Turn 4: "Compare A and B" → result (800 tokens)
Total context: 3,500 tokens + overhead
```

### Solution

Claude generates Python code that executes multiple tools in one pass:
- 1 inference pass: Generate code
- Sandbox executes: All tool calls run
- 1 summary result: Compact findings
- Result: 37% token reduction

**Example:**
```python
Turn 1: "Compare files A and B"
↓ Claude generates code:

# Generated by Claude
file_a = read_file("src/auth.ts")
matches_a = search_in_file(file_a, "password")
file_b = read_file("src/login.ts")
matches_b = search_in_file(file_b, "password")

differences = compare(matches_a, matches_b)
summary = {
    "only_in_a": [...],
    "only_in_b": [...],
    "common": [...]
}

↓ Sandbox executes, returns:
{
  "only_in_a": ["password hashing in auth"],
  "only_in_b": ["password validation in login"],
  "common": ["password length check"]
}

Total context: ~500 tokens (just summary)
```

### How It Works

1. **User requests complex operation**
2. **Claude generates Python code** that calls tools
3. **Sandbox executes code** with tool access
4. **Code generates summary** of findings
5. **Only summary returned** to Claude
6. **Claude uses summary** to answer user

### Implementation

**Using sandbox_executor.py:**
```python
from scripts.orchestration.sandbox_executor import SandboxExecutor

# Initialize executor
executor = SandboxExecutor(
    allowed_tools=["read_file", "search", "grep"],
    workspace_dir="/path/to/project"
)

# Execute code
result = executor.execute_code(
    code=claude_generated_code,
    timeout=30
)

print(result["summary"])
```

### Comparison

| Approach | Inference Passes | Context Growth | Token Cost |
|----------|------------------|----------------|------------|
| Traditional | N (one per tool call) | Linear (all results) | 100% |
| Programmatic | 1 (code generation) | Constant (summary only) | 63% |

### Script

**Location:** `scripts/orchestration/sandbox_executor.py`

**Usage:**
```bash
# Test programmatic tool calling
python3 scripts/orchestration/sandbox_executor.py
```

### Security

- Sandboxed execution environment
- Restricted tool access (allowlist)
- Filesystem scope limits
- Timeout protection (default: 30s)

**See:** `docs/guides/SECURITY.md` for security details

### Best For

- Multi-step workflows
- File analysis (grep, search across many files)
- Data processing pipelines
- Batch operations

### Documentation

**Complete Guide:** `docs/PROGRAMMATIC_TOOL_CALLING.md`

---

## Advanced Orchestration

Combining all three patterns for maximum efficiency.

### Example: Large-Scale Code Review

**Scenario:** Review 50 files for security issues

**Traditional Approach:**
```
1. Read file 1 → 1,000 tokens
2. Analyze file 1 → 500 tokens
3. Read file 2 → 1,200 tokens
4. Analyze file 2 → 600 tokens
... (repeat 48 more times)
Total: ~85,000 tokens
```

**Optimized Approach:**
```
Setup:
- Deferred loading: Only load security skill when "security" mentioned
- Prompt caching: Cache system prompt, coding standards
- Programmatic tools: Generate code to process all files

Execution:
1. Load security skill (triggered by "security") → 4,000 tokens
2. Generate code to scan all files → 1 inference
3. Sandbox executes, returns summary → 2,000 tokens
4. Claude reviews summary → 1 inference

Total: ~15,000 tokens (82% reduction)
Cost: ~70% savings (prompt caching)
```

### Combined Pattern Script

**Location:** `scripts/orchestration/programmatic_orchestrator.py`

**Usage:**
```python
from scripts.orchestration.programmatic_orchestrator import ProgrammaticOrchestrator

orchestrator = ProgrammaticOrchestrator(
    use_caching=True,           # Enable prompt caching
    deferred_skills=True,       # Enable deferred loading
    programmatic_tools=True     # Enable code generation
)

result = orchestrator.execute_workflow(
    task="Review all files for security issues",
    files=file_list
)
```

---

## Best Practices

### When to Use Each Pattern

**Deferred Loading:**
- ✅ Large skill libraries (10+ skills)
- ✅ Agents with varied responsibilities
- ❌ Agents using same 1-2 skills always

**Prompt Caching:**
- ✅ Repeated operations
- ✅ Batch processing
- ✅ CI/CD pipelines
- ❌ One-off tasks
- ❌ Rapidly changing prompts

**Programmatic Tools:**
- ✅ Multi-step workflows (5+ tool calls)
- ✅ Batch operations
- ✅ File analysis
- ❌ Single tool calls
- ❌ Interactive workflows

### Combining Patterns

1. **Start with deferred loading** - Always useful for 5+ skills
2. **Add caching for repeated ops** - CI/CD, batch processing
3. **Use programmatic tools for workflows** - Multi-step, file analysis

### Monitoring

Track effectiveness:
- Token usage before/after
- API costs before/after
- Latency changes
- Accuracy maintained

---

## Orchestration Scripts

All scripts located in `scripts/orchestration/`:

| Script | Purpose |
|--------|---------|
| `simple_orchestrator.py` | Basic multi-agent orchestration |
| `prompt_cache.py` | Prompt caching implementation |
| `sandbox_executor.py` | Programmatic tool calling |
| `programmatic_orchestrator.py` | Combined patterns |
| `file_based_orchestrator.py` | File-based coordination |
| `custom_orchestrator_example.py` | Custom patterns |

**Complete Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`

---

## See Also

- **Orchestration Guide:** `scripts/orchestration/COMPLETE_GUIDE.md`
- **Programmatic Tools:** `docs/PROGRAMMATIC_TOOL_CALLING.md`
- **Security:** `docs/guides/SECURITY.md`
- **Skills Assignment:** [03-skills.md](03-skills.md)

---

[← Back to Index](index.md) | [Previous: Scripts & Tools](06-scripts-tools.md) | [Next: Schemas →](08-schemas.md)
