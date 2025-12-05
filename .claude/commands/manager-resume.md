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
   - README update status (check if previous session updated it)

5. **Verify README is current** (optional):
   ```
   Read README.md
   ```
   Check that it reflects recent progress mentioned in handoff.

6. **Continue work** from where previous manager left off

7. **Delete handoff** after context transfer:
   ```bash
   rm .ai-agents/state/manager-handoff.md
   ```

Proceed with resume process now.
