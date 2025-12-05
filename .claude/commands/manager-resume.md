---
description: Resume manager session from handoff document
argument-hint:
---

You are resuming a manager session from a previous context.

## Resume Protocol

1. **Read the handoff document**:
   ```
   Read .ai-agents/state/manager-handoff.md
   ```

2. **Read current communication file**:
   ```
   Read .ai-agents/state/team-communication.json
   ```

3. **Verify file locations** from handoff are correct

4. **Review**:
   - Active tasks and their status
   - Recent decisions
   - Blocked tasks
   - Next actions

5. **Continue work** from where previous manager left off

6. **Delete handoff** after context transfer:
   ```bash
   rm .ai-agents/state/manager-handoff.md
   ```

Proceed with resume process now.
