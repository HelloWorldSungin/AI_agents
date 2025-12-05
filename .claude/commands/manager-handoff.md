---
description: Create manager session handoff with README update
argument-hint:
---

You are creating a manager handoff to transfer context to the next session.

## Handoff Creation Protocol

### Step 1: Run Cleanup
```bash
python3 scripts/cleanup-team-communication.py
```

Verify the file size was reduced:
```bash
wc -c .ai-agents/state/team-communication.json | awk '{print "~" int($1/4) " tokens"}'
```

### Step 2: Read Current State
```bash
Read .ai-agents/state/team-communication.json
```

Review:
- Active tasks and their status
- Completed tasks this session
- Recent decisions made
- Any blockers

### Step 3: Update README.md

Read the current README:
```bash
Read README.md
```

Update the README.md to reflect:
- **Recent Progress**: What was accomplished this session
- **Current Status**: Active work and what's in progress
- **Next Steps**: What should happen next
- **Version**: Update version if significant features completed

Focus on high-level project status, not implementation details.

### Step 4: Create Handoff Document

Copy the template:
```bash
Read .ai-agents/templates/manager-handoff.md
```

Create handoff at `.ai-agents/state/manager-handoff.md` with:
- Session summary (feature, duration, accomplishments)
- ALL file locations (especially team-communication.json path)
- Active tasks status
- Completed tasks summary
- Decisions made this session
- Next actions for incoming manager
- Cleanup status (archive path, new file size)
- README update summary

### Step 5: Commit Everything

Stage all changes:
```bash
git add .ai-agents/state/ README.md
```

Create commit:
```bash
git commit -m "chore: manager handoff - [feature-name]

Session summary:
- Tasks completed: [X]
- Tasks active: [Y]
- Communication file: ~[Z] tokens (cleaned)
- README updated with current status

Next session: [immediate action needed]"
```

### Step 6: Inform User

Report to user:
```
Manager handoff created:
- Handoff: .ai-agents/state/manager-handoff.md
- Communication file: .ai-agents/state/team-communication.json (~[X] tokens)
- Cleanup archive: [archive-path]
- README.md updated with session progress

To resume: Start new manager session and run /manager-resume
```

Proceed with handoff creation now.
