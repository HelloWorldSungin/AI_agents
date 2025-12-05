# Long-Running Agent Patterns

## Overview

This guide integrates Anthropic's research on long-running agents with the AI_agents system. It addresses the "shift-change problem" where agents waste time rediscovering project state between sessions, and establishes patterns for sustained, multi-session development.

Based on: [Anthropic's "Effective Harnesses for Long-Running Agents"](https://www.anthropic.com/research/building-effective-agents)

## The Shift-Change Problem

### Problem

When an agent starts a fresh session on an existing project:
- Spends 10-30 minutes rediscovering what was already done
- Re-reads files it analyzed before
- Re-plans work that was already planned
- Risks marking incomplete work as "done"
- Wastes time and tokens

### Solution

Structured session continuity through:
1. Progress tracking files
2. Feature status management
3. Git as state history
4. Clear resumption protocols

## Core Patterns

### Pattern 1: Two-Agent Architecture

**Anthropic's Pattern**:
- Initializer Agent (first session): Sets up project, creates feature list
- Coding Agent (all sessions): Implements features, updates progress

**AI_agents Mapping**:
- Manager Agent ≈ Initializer (planning, feature breakdown)
- Task Agents ≈ Coding Agent (implementation)
- Plus: Senior Engineer (review), QA Tester (verification)

### Pattern 2: Session Progress Tracking

**State File**: `.ai-agents/state/session-progress.json`

Tracks:
- Last session timestamp
- Current phase of development
- Completed vs. active tasks
- Blockers
- Next priorities
- Git baseline

**Benefits**:
- 50% reduction in session startup time
- No redundant discovery
- Clear continuation point

### Pattern 3: Feature Status Management

**State File**: `.ai-agents/state/feature-tracking.json`

Each feature has:
- Unique ID (e.g., AUTH-001)
- Clear description
- Status: not_started → in_progress → passing/failing
- Test file and command
- Verification criteria

**Benefits**:
- Prevents premature "done" declarations
- Forces explicit E2E testing
- Clear progress visibility
- Easy prioritization

### Pattern 4: Mandatory E2E Testing

**Problem**: Agents report features "complete" based on unit tests, missing user-facing bugs.

**Solution**: Features CANNOT be "passing" without E2E tests.

**Workflow**:
1. Developer implements feature + unit tests
2. QA writes E2E tests (webapp-testing skill)
3. Senior Engineer verifies E2E tests pass
4. Only then: feature marked "passing"

### Pattern 5: Environment Automation

**init.sh Pattern**: Automated setup script

**Benefits**:
- New agents onboard in minutes
- Consistent environment across sessions
- Documents setup as executable code
- Reduces "works for me" issues

### Pattern 6: Security Framework

**Defense-in-Depth** (3 layers):
1. Command allowlist
2. Destructive pattern detection
3. Filesystem scope restrictions

**When Needed**: Autonomous execution mode

## Implementation in AI_agents

### First Session (New Project)

**Manager Agent Responsibilities**:

```markdown
1. Create feature list (.ai-agents/state/feature-tracking.json)
   - Break project into 20-50 features
   - Assign unique IDs
   - Define acceptance criteria

2. Initialize progress tracker (.ai-agents/state/session-progress.json)
   - Set project name and phase
   - Record git baseline
   - List initial priorities

3. Delegate infrastructure setup (IT Specialist)
   - Run 8 infrastructure checks
   - Generate init.sh script
   - Document environment

4. Begin feature implementation
   - Assign features to task agents
   - Update feature status to "in_progress"
   - Track in real-time
```

### Resuming Session (Existing Project)

**Manager Agent Resumption Protocol**:

```markdown
ALWAYS start by reading (in this order):

1. session-progress.json
   - When was last session?
   - What phase are we in?
   - What's completed vs. active?
   - Any blockers?

2. feature-tracking.json
   - How many passing/failing?
   - What's in progress?
   - What's blocked?

3. team-communication.json
   - Recent agent updates
   - Coordination needs

4. Git log since last session
   - git log --since="<last_session_timestamp>"
   - Verify baseline is current

Then:
1. Prioritize work (failing > blocked > in_progress > not_started)
2. Delegate to appropriate agents
3. Update progress tracker
```

### Feature Completion Criteria

A feature is ONLY "passing" when ALL criteria met:

- ✅ Code implemented and committed
- ✅ Unit tests written and passing
- ✅ E2E tests written and passing
- ✅ Code reviewed by Senior Engineer
- ✅ Feature marked "passing" in feature-tracking.json
- ✅ All acceptance criteria verified

**Anti-Pattern**: Marking "passing" without E2E tests.

### Progress Update Protocol

After each feature completion:

```json
// Update feature-tracking.json
{
  "id": "AUTH-001",
  "status": "passing",
  "git_commit": "abc123",
  "verified_by": "qa_tester",
  "completed_date": "2024-01-15T16:00:00Z",
  "test_file": "tests/auth/register.spec.ts"
}

// Update session-progress.json
{
  "completed_tasks": [..., "AUTH-001"],
  "git_baseline": "abc123",
  "metrics": {
    "features_completed": 3
  }
}
```

## Practical Examples

### Example 1: 3-Session Project

**Session 1** (2 hours):
- Manager creates 12 features (AUTH-001 to AUTH-012)
- IT Specialist validates infrastructure
- Backend Developer implements AUTH-001, AUTH-002
- Features: 2 passing, 10 not_started
- Session progress saved

**Session 2** (2 hours):
- Manager reads progress: "2/12 done, continuing auth"
- No re-planning needed (saves 20 minutes)
- Frontend Developer implements AUTH-003, AUTH-004
- QA Tester writes E2E tests
- Features: 4 passing, 8 not_started

**Session 3** (90 minutes):
- Manager reads progress: "4/12 done"
- Identifies AUTH-005 is blocked (dependency issue)
- Prioritizes unblocking, then continues
- Features: 6 passing, 1 failing, 5 not_started
- Project 50% complete

**Time Saved**: ~40 minutes across 3 sessions (no redundant discovery)

### Example 2: Catching Premature "Done"

**Without E2E Testing**:
```
Developer: "Login feature complete"
Unit tests: ✅ All passing
Reality: Error message div not rendering
User experience: Broken
```

**With E2E Testing**:
```
Developer: "Login feature complete"
Unit tests: ✅ All passing
QA Tester: "Writing E2E tests..."
E2E tests: ❌ Error message not visible
Status: "failing" (not "passing")
Feature sent back for fix
User experience: Fixed before release
```

## Metrics to Track

Monitor these in `session-progress.json`:

- **Session startup time**: Should decrease after session 1
- **Feature completion rate**: Features passing vs. failing
- **Test coverage**: % with E2E tests
- **Blocker resolution time**: How quickly blockers cleared
- **Rework rate**: Features going passing → failing → passing

**Success Indicators**:
- Session 2+ startup < 5 minutes
- <10% of features marked passing then failing
- 100% of user-facing features have E2E tests
- Blockers resolved within 1 session

## Common Pitfalls

### Pitfall 1: Ignoring State Files

❌ **Wrong**:
```
Manager: "Let me analyze what's been done..."
[Spends 15 minutes reading files]
[Re-discovers completed features]
```

✅ **Right**:
```
Manager: "Reading session-progress.json..."
[Sees 8/20 features complete]
[Immediately knows next priorities]
[Starts work in 2 minutes]
```

### Pitfall 2: Skipping E2E Tests

❌ **Wrong**:
```
Feature status: "passing" (unit tests only)
Reality: UI doesn't work
Discovery: In production
```

✅ **Right**:
```
Feature status: "in_progress" (unit tests pass)
QA: "Writing E2E tests..."
E2E tests: Find UI bug
Bug fixed before marking "passing"
```

### Pitfall 3: Stale Progress Files

❌ **Wrong**:
```
[Complete feature AUTH-003]
[Don't update feature-tracking.json]
[Next session: confusion about what's done]
```

✅ **Right**:
```
[Complete feature AUTH-003]
[Immediately update feature-tracking.json]
[Update session-progress.json]
[Commit state files]
[Next session: clear continuation]
```

## Integration with Existing Workflows

### Human-Coordinated Mode

- Manager maintains progress files
- Human reviews feature status
- Manual approval for "passing"
- Progress files aid human understanding

### Task Tool Delegation Mode

- Manager reads progress before delegating
- Sub-agents update feature status
- Integration agent verifies against features
- Automatic progress tracking

### Future: Fully Autonomous Mode

- Security validator enables safe automation
- Progress tracking supports long-running jobs
- Feature lists provide clear completion criteria
- No human in loop (with safety guardrails)

## Tools and Files

### State Files

- `.ai-agents/state/session-progress.json` - Cross-session state
- `.ai-agents/state/feature-tracking.json` - Feature statuses
- `.ai-agents/state/team-communication.json` - Agent coordination

### Schemas

- `schemas/session-progress.json` - Progress file schema
- `schemas/feature-tracking.json` - Feature list schema
- `schemas/security-policy.json` - Security configuration

### Scripts

- `scripts/security_validator.py` - Command validation
- `templates/init-scripts/*.sh` - Setup automation

### Documentation

- `docs/guides/E2E_TESTING.md` - Testing workflow
- `docs/guides/SECURITY.md` - Security framework
- `examples/session-continuity/` - Working example

## Next Steps

### Getting Started

1. **Read the Plan**: `.planning/PLAN-autonomous-agent-integration.md`
2. **Review Examples**: `examples/session-continuity/`
3. **Try It**: Start a new project with session tracking
4. **Monitor**: Track session startup times and rework rates
5. **Iterate**: Adjust feature granularity based on results

### Advanced Usage

1. **Custom Security Policies**: Tailor command allowlist
2. **Project-Specific Metrics**: Track domain-specific KPIs
3. **Multi-Agent Coordination**: Complex feature dependencies
4. **Long-Running Jobs**: 10+ session projects

### Community

- Share your long-running project experiences
- Contribute new init.sh templates
- Report security edge cases
- Suggest improvements to tracking schemas

## References

- Anthropic Research: "Building Effective Agents"
- Anthropic GitHub: `anthropics/anthropic-quickstarts`
- AI_agents Implementation Plan: `.planning/PLAN-autonomous-agent-integration.md`
