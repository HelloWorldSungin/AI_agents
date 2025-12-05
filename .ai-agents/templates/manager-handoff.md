---
handoff_type: manager_session
created: [ISO timestamp]
session_id: [unique-id]
---

# Manager Session Handoff

## Session Summary

**Feature/Epic**: [Current feature being worked on]
**Started**: [ISO timestamp]
**Handed Off**: [ISO timestamp]
**Session Duration**: [hours/minutes]

## File Locations (CRITICAL)

### Team Communication
- **Path**: `.ai-agents/state/team-communication.json`
- **Last Updated**: [timestamp]
- **Size**: ~[X] tokens
- **Status**: [active/cleaned/archived]

### Project Context Files
- Architecture: `.ai-agents/context/architecture.md`
- API Contracts: `.ai-agents/context/api-contracts.md`
- Infrastructure: `.ai-agents/infrastructure-setup.md`

## Current State

### Active Tasks
[List from team-communication.json manager_instructions.active_tasks]

### Completed This Session
[List recently completed tasks]

### Blocked Tasks
[List any blockers with details]

## Decisions Made This Session

[List important decisions from manager_instructions.decisions]

## Next Manager Should Know

### Immediate Actions
1. [Priority action 1]
2. [Priority action 2]

### Pending Decisions
- [Decision that needs to be made]

### Known Issues
- [Issue 1]
- [Issue 2]

## Agent Status

### Recently Active Agents
- **[agent-id]**: [Last task, status, branch]
- **[agent-id]**: [Last task, status, branch]

### Waiting for Work
- [List of agents ready for tasks]

## Cleanup Status

- [ ] Communication file cleaned (if > 20k tokens)
- [ ] Old updates archived to: [archive path]
- [ ] File size now: ~[X] tokens

## Resume Instructions

To resume as manager:

1. **Read communication file**:
   ```bash
   Read .ai-agents/state/team-communication.json
   ```

2. **Review this handoff**:
   ```bash
   Read .ai-agents/state/manager-handoff.md
   ```

3. **Check active tasks** and continue coordination

4. **Delete this handoff** once context is transferred
