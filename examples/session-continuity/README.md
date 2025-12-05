# Session Continuity Example

This example demonstrates how the AI_agents system maintains state across multiple sessions for long-running projects, preventing the "shift-change problem" where agents waste time rediscovering project state.

## Scenario

Building a simple task management API with user authentication across 3 agent sessions:
- **Session 1**: Initial setup and database schema
- **Session 2**: Authentication implementation
- **Session 3**: Task CRUD operations and integration

## Files in This Example

- `session-01-progress.json` - State after first session
- `session-01-features.json` - Feature tracking after first session
- `session-02-progress.json` - State after second session
- `session-02-features.json` - Feature tracking after second session
- `session-03-progress.json` - Final state
- `session-03-features.json` - Final feature tracking
- `manager-session-01.md` - Manager's actions in session 1
- `manager-session-02.md` - Manager's actions in session 2 (resuming)
- `manager-session-03.md` - Manager's actions in session 3 (resuming)

## Key Patterns Demonstrated

### 1. Session Resumption

**Session 2 Start:**
```
Manager reads:
1. session-01-progress.json → Last session completed DB setup
2. session-01-features.json → 2 features passing, 3 not started
3. Git log → 3 commits since baseline
4. Team communication → No blockers

Manager immediately knows:
- What's done (DB schema, infrastructure)
- What's next (Authentication features)
- Current state (2/5 features complete)
- No need to re-discover or re-plan
```

### 2. Feature Status Tracking

Features flow through states with clear verification:
```
AUTH-001: not_started → in_progress → passing ✓
AUTH-002: not_started → in_progress → failing → in_progress → passing ✓
```

### 3. E2E Testing Requirement

Notice in the feature tracking files that features are only marked "passing" after:
- Unit tests pass
- E2E tests pass (using webapp-testing skill)
- Senior Engineer code review

### 4. Blocker Management

Session 2 encounters a blocker (missing JWT library). See how it's:
- Documented in session-02-progress.json
- Reflected in feature-tracking.json (AUTH-003 status: blocked)
- Resolved in session 3

## Usage

1. Review `manager-session-01.md` to see initial project setup
2. Compare `session-01-progress.json` with `session-02-progress.json` to see state evolution
3. Notice how session 2 and 3 start by reading state files (no redundant discovery)
4. Observe feature status changes in feature-tracking files

## Benefits Demonstrated

- **50% reduction in startup time**: Sessions 2 and 3 skip planning phase
- **Clear completion criteria**: Features only "passing" when fully verified
- **Blocker visibility**: Session 3 immediately sees AUTH-003 blocker
- **Progress visibility**: Summary statistics show 2/5 → 4/5 → 5/5 completion

## Applying to Your Project

1. **First Session**: Manager creates feature-tracking.json and session-progress.json
2. **Each Feature Completion**: Update both files with status and notes
3. **Session End**: Add session history entry, set next_priorities
4. **Resume Session**: Read state files first before any planning
5. **Commit State**: Always commit state files to git

This pattern scales from small projects (5-10 features) to large projects (100+ features) by providing structured continuity across unlimited sessions.
