# Regression-First Pattern

**Version:** 1.0.0
**Category:** Quality Pattern
**Purpose:** Prevent cascading bugs through systematic regression verification

---

## Overview

The Regression-First Pattern ensures that existing functionality remains intact before adding new features. By verifying prior work at the start of each session and before each new task, agents catch regressions early when they're cheapest to fix.

### Key Insight

> The cost of fixing a bug increases exponentially with time.
> Catching a regression in 5 minutes costs 5 minutes.
> Catching it after 5 more features costs hours of debugging.

---

## Problem Statement

Without systematic regression testing:

1. **Silent Breakage**: Features that worked yesterday fail today
2. **Cascading Failures**: Bugs in shared code break multiple features
3. **Lost Confidence**: Team loses trust in the codebase
4. **Debug Spirals**: Hours spent finding which change broke what
5. **Integration Hell**: Merging becomes painful and risky

---

## Solution: Regression-First Workflow

### Modified Task Flow

```
Traditional:  Select Task → Implement → Test → Complete
Regression:   VERIFY PRIOR → Select Task → Implement → Test → Complete
                   ↑                                        │
                   └────────── On Failure ←─────────────────┘
```

### Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                 Regression-First Workflow                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Session Start                                              │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                       │
│  │ Run Regression  │──FAIL──► Fix Regression              │
│  │ Tests           │           (Priority 1)                │
│  └────────┬────────┘                │                      │
│           │ PASS                    ▼                      │
│           ▼                   Create Bug Task              │
│  ┌─────────────────┐                │                      │
│  │ Update META     │◄───────────────┘                      │
│  │ Status: PASSING │                                       │
│  └────────┬────────┘                                       │
│           │                                                │
│           ▼                                                │
│  ┌─────────────────┐                                       │
│  │ Select Next     │                                       │
│  │ Task            │                                       │
│  └────────┬────────┘                                       │
│           │                                                │
│           ▼                                                │
│  ┌─────────────────┐                                       │
│  │ Implement       │                                       │
│  │ Feature         │                                       │
│  └────────┬────────┘                                       │
│           │                                                │
│           ▼                                                │
│  ┌─────────────────┐                                       │
│  │ Run Tests       │──FAIL──► Fix Before Continue         │
│  │ (Unit + Regr)   │                │                      │
│  └────────┬────────┘                │                      │
│           │ PASS                    │                      │
│           ▼                         │                      │
│  ┌─────────────────┐                │                      │
│  │ Mark Task       │◄───────────────┘                      │
│  │ Complete        │                                       │
│  └────────┬────────┘                                       │
│           │                                                │
│           ▼                                                │
│      Next Task                                             │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Run Regression Tests

### Mandatory Regression Points

| Trigger | Action |
|---------|--------|
| Session Start | Full regression suite |
| Before New Task | Quick smoke tests |
| After Implementation | Full regression suite |
| Before Commit | Affected test files |
| Before Push | Full regression suite |
| After Merge | Full regression suite |

### Regression Test Tiers

```yaml
tiers:
  smoke:
    description: "Critical path only"
    duration: "< 30 seconds"
    when: ["before_new_task"]
    tests:
      - "core functionality"
      - "auth flows"
      - "critical APIs"

  standard:
    description: "All unit + integration"
    duration: "< 5 minutes"
    when: ["session_start", "after_implementation", "before_push"]
    tests:
      - "all unit tests"
      - "integration tests"
      - "API contract tests"

  comprehensive:
    description: "Full suite including E2E"
    duration: "< 30 minutes"
    when: ["before_release", "after_major_change"]
    tests:
      - "all standard tests"
      - "E2E browser tests"
      - "performance benchmarks"
```

---

## Handling Regression Failures

### Priority Override

When regression tests fail:

1. **Immediate Priority**: Fix regression becomes P1
2. **Block New Work**: No new features until green
3. **Root Cause Analysis**: Identify which change caused it
4. **Prevent Recurrence**: Add targeted test if needed

### Failure Response Protocol

```python
def handle_regression_failure(failure):
    # Step 1: Log failure
    log_failure_to_meta(failure)

    # Step 2: Identify cause
    recent_changes = get_recent_changes()
    likely_cause = bisect_failure(recent_changes)

    # Step 3: Create fix task
    fix_task = create_task({
        "title": f"FIX: Regression in {failure.test_name}",
        "priority": 1,  # Urgent
        "category": "bugfix",
        "description": f"""
## Regression Detected

**Test**: {failure.test_name}
**Error**: {failure.error_message}
**Likely Cause**: {likely_cause}

## Previous State
This test was passing as of {failure.last_passed}

## Stack Trace
```
{failure.stack_trace}
```
        """,
        "labels": ["regression", "urgent"]
    })

    # Step 4: Update META
    update_meta({
        "regression_status": "failing",
        "regression_details": {
            "test": failure.test_name,
            "since": datetime.now().isoformat(),
            "fix_task": fix_task.id
        }
    })

    # Step 5: Notify
    send_regression_alert(failure, fix_task)
```

### Bisection for Root Cause

When a regression is detected but cause is unclear:

```bash
# Find which commit introduced the failure
git bisect start
git bisect bad HEAD
git bisect good <last_known_good_commit>

# For each bisect step:
npm test -- --grep "failing_test"
# Mark result and continue until cause found
```

---

## Regression Status Tracking

### META Issue Status

```markdown
## Regression Status

**Status**: PASSING ✓
**Last Run**: 2024-01-15T14:00:00Z
**Tests**: 156 passing, 0 failing
**Duration**: 4m 32s

### History
- 2024-01-15 14:00: PASSING (156 tests)
- 2024-01-15 10:00: PASSING (155 tests)
- 2024-01-14 16:00: FAILING → Fixed in TASK-015
```

### Session Start Check

```python
def session_start_regression_check():
    meta = provider.get_meta()

    if meta.regression_status == "failing":
        print("⚠️  REGRESSION TESTS FAILING")
        print(f"Failing since: {meta.regression_details['since']}")
        print(f"Fix task: {meta.regression_details['fix_task']}")
        print("\nPriority: Fix regression before new features")
        return False

    if meta.regression_status == "unknown":
        print("⚠️  Regression status unknown")
        print("Running regression suite...")
        run_regression_tests()

    return True
```

---

## Integration with Agents

### Software Developer Prompt Addition

Add to `prompts/roles/software-developer.md`:

```markdown
### Regression-First Protocol

Before starting any new task:

1. **Check Regression Status**
   - If META shows FAILING, prioritize fix
   - If UNKNOWN, run regression suite

2. **Run Smoke Tests**
   - Quick verification of critical paths
   - Block on failure

3. **After Implementation**
   - Run full regression suite
   - Do not mark task complete until green

4. **On Regression Failure**
   - Stop new feature work immediately
   - Create bug fix task (P1)
   - Fix before continuing
```

### Manager Enforcement

Add to manager workflow:

```markdown
### Regression Gate

Before assigning new tasks:

1. Check META.regression_status
2. If FAILING:
   - Assign regression fix as P1
   - Block all feature work
3. If UNKNOWN:
   - Request regression run first
4. If PASSING:
   - Proceed with task assignment
```

---

## Configuration

```yaml
session:
  regression_testing: "required"  # "required", "recommended", "disabled"

regression:
  # When to run
  on_session_start: true
  before_new_task: "smoke"  # "smoke", "standard", "full", "none"
  after_implementation: "standard"
  before_push: "full"

  # Test commands
  commands:
    smoke: "npm test -- --grep '@smoke'"
    standard: "npm test"
    full: "npm run test:all"

  # Failure handling
  on_failure:
    priority: 1  # P1 - urgent
    block_new_work: true
    notify:
      - slack
      - linear_comment

  # Timeouts
  timeouts:
    smoke: 30  # seconds
    standard: 300  # 5 minutes
    full: 1800  # 30 minutes
```

---

## Best Practices

### DO:

1. **Always run smoke tests** before starting new work
2. **Never skip regression** to "save time" - it costs more later
3. **Fix immediately** - regressions are priority 1
4. **Track in META** - regression status visible to all sessions
5. **Add coverage** - new bugs deserve new tests

### DON'T:

1. **Don't ignore flaky tests** - fix or quarantine them
2. **Don't mark tasks complete** with failing tests
3. **Don't blame others** - focus on fix, not fault
4. **Don't pile on features** when regressions exist
5. **Don't skip slow tests** - run them before push

---

## Troubleshooting

### Flaky Tests

```
Problem: Test sometimes passes, sometimes fails
Solution:
  1. Identify flaky test
  2. Quarantine (move to separate suite)
  3. Fix root cause (timing, state, randomness)
  4. Restore to main suite
```

### Slow Test Suite

```
Problem: Regression takes too long
Solution:
  1. Parallelize tests
  2. Create smoke/standard/full tiers
  3. Run smoke frequently, full before push
  4. Consider test infrastructure (faster CI)
```

### Too Many Regressions

```
Problem: Constant regression failures
Solution:
  1. Review test quality (are tests too brittle?)
  2. Improve code architecture (better isolation)
  3. Add integration tests (catch issues earlier)
  4. Review development practices
```

---

## Metrics

Track these for regression health:

| Metric | Target | Alert If |
|--------|--------|----------|
| Regression rate | < 1/week | > 3/week |
| Time to fix | < 2 hours | > 1 day |
| Test coverage | > 80% | < 60% |
| Flaky test count | 0 | > 5 |
| Suite duration | < 5 min | > 15 min |

---

## Version History

- **1.0.0** (2024-01-15): Initial regression-first pattern
