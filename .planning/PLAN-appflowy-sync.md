# AppFlowy Integration Plan: Documentation & Project Management Sync

## Objective
Test and use the `@skills/custom/appflowy-integration/` skill to sync AI_agents repository content to AppFlowy in the "AI Agents" workspace:
- **General → Documentation**: Essential repo documentation with hierarchical folders
- **General → Project Management**: Task tracking with Kanban board view

**AppFlowy URL**: `https://appflowy.ark-node.com/` (SSL enabled)

---

## Phase 1: Environment Setup & Validation

### Task 1.1: Validate Existing Credentials with New URL
**Actions:**
1. Check existing environment variables (`APPFLOWY_API_TOKEN`, `APPFLOWY_WORKSPACE_ID`)
2. Test connection to new HTTPS URL: `https://appflowy.ark-node.com/`
3. If token expired or fails, re-authenticate to get new JWT token
4. Validate workspace access with existing workspace ID

**Verify:** API responds successfully to `GET /api/workspace` with 200 status

### Task 1.2: Update AppFlowy Configuration
**Files to modify:**
- `skills/custom/appflowy-integration/SKILL.md` - Update URL from `http://appflowy.arknode-ai.home` to `https://appflowy.ark-node.com/`

**Actions:**
1. Update `APPFLOWY_API_URL` in SKILL.md quick_start section
2. Update any hardcoded URLs in scripts
3. Document new SSL-enabled endpoint

**Verify:** Skill documentation reflects correct URL

### Task 1.3: Verify AppFlowy UI Setup (Manual Checkpoint)
**Required manual steps (cannot be automated via API):**
1. Navigate to "AI Agents" workspace in AppFlowy UI
2. Create "Documentation" folder under General (if not exists)
3. Create "Project Management" folder under General (if not exists)
4. Create required databases with views:
   - Documentation database with Grid view
   - Tasks database with Kanban board view

**Verify:** Folders and databases visible in UI with proper views

---

## Phase 2: Documentation Space Organization

### Proposed Structure
```
AI Agents (Workspace)
└── General
    └── Documentation/
        ├── Getting Started/
        │   ├── README (main repo overview)
        │   └── Quick Start Guide
        ├── Guides/
        │   ├── Architecture
        │   ├── Context Engineering
        │   ├── Skills Guide
        │   └── Practical Workflow
        ├── Reference/
        │   ├── Cheat Sheet Index
        │   ├── FAQ
        │   └── State Files
        └── Examples/
            ├── Web App Team
            └── Mobile App Team
```

### Task 2.1: Create Documentation Sync Script
**File to create:** `skills/custom/appflowy-integration/scripts/sync_docs.py`

**Essential files to sync (~15 files):**
1. `/README.md` → Getting Started/README
2. `/docs/guides/ARCHITECTURE.md` → Guides/Architecture
3. `/docs/guides/Context_Engineering.md` → Guides/Context Engineering
4. `/docs/guides/SKILLS_GUIDE.md` → Guides/Skills Guide
5. `/docs/guides/PRACTICAL_WORKFLOW_GUIDE.md` → Guides/Practical Workflow
6. `/docs/reference/CHEAT_SHEET.md` → Reference/Cheat Sheet Index
7. `/docs/reference/FAQ.md` → Reference/FAQ
8. `/docs/reference/CHEAT_SHEET/01-state-files.md` → Reference/State Files
9. `/docs/reference/CHEAT_SHEET/00-quick-start.md` → Getting Started/Quick Start
10. `/examples/web-app-team/README.md` → Examples/Web App Team
11. `/examples/mobile-app-team/README.md` → Examples/Mobile App Team
12. `/docs/guides/E2E_TESTING.md` → Guides/E2E Testing
13. `/docs/guides/LONG_RUNNING_AGENTS.md` → Guides/Long Running Agents
14. `/docs/guides/SECURITY.md` → Guides/Security
15. `/starter-templates/README.md` → Getting Started/Starter Templates

**Script features:**
- Read markdown files from repo
- Convert to AppFlowy page format
- Create hierarchical folder structure
- Track sync status for incremental updates

**Verify:** All 15 documents appear in AppFlowy Documentation folder

---

## Phase 3: Project Management Space Organization

### Proposed Kanban Structure
```
AI Agents (Workspace)
└── General
    └── Project Management/
        └── Tasks Database (Kanban View)
            ├── Column: Backlog
            ├── Column: Todo
            ├── Column: In Progress
            ├── Column: Review
            ├── Column: Done
            └── Column: Blocked
```

### Database Schema
| Field | Type | Options |
|-------|------|---------|
| Title | Text | Primary field |
| Status | Select | Backlog, Todo, In Progress, Review, Done, Blocked |
| Priority | Select | Critical, High, Medium, Low |
| Category | Select | Feature, Bug, Documentation, Infrastructure, Research |
| Source | Text | File path or reference |
| Created | Date | Auto |
| Updated | Date | Auto |
| Notes | Text | Long text for details |

### Task 3.1: Create Task Sync Script
**File to create:** `skills/custom/appflowy-integration/scripts/sync_tasks.py`

**Data sources to sync:**
1. `.ai-agents/state/team-communication.json` - Active task coordination
2. `.ai-agents/state/feature-tracking.json` - Feature status
3. `.planning/ROADMAP.md` - Planned phases
4. `whats-next.md` - Session handoffs and pending items

**Current tasks to import:**
- Manager Workflow Enhancement (Phase 4-6 pending)
- Repository Restructuring (6 phases not started)
- Feature tracking items (17 not-started)

**Verify:** Tasks appear in Kanban with correct status columns

---

## Phase 4: Automation & Ongoing Sync

### Task 4.1: Create Git-to-AppFlowy Sync Workflow
**File to create:** `skills/custom/appflowy-integration/workflows/git-sync.md`

**Sync triggers:**
- Manual: Run `python sync_docs.py` or `python sync_tasks.py`
- Git hook (optional): Post-commit hook to sync changed files
- Scheduled: Cron job for periodic sync

**Sync logic:**
1. Check file modification times vs last sync
2. Only sync changed files (incremental)
3. Log sync results to `.ai-agents/appflowy-sync-log.json`
4. Handle conflicts (repo wins - one-way sync)

### Task 4.2: Update Skill Documentation
**File to modify:** `skills/custom/appflowy-integration/SKILL.md`

Add new workflows:
- `workflows/sync-documentation.md` - How to sync docs
- `workflows/sync-tasks.md` - How to sync project tasks
- Update quick_start section with new URL

**Verify:** Skill documentation reflects new sync capabilities

---

## Critical Files Summary

**To Modify:**
- `skills/custom/appflowy-integration/SKILL.md` - Update URL, add sync workflows

**To Create:**
- `skills/custom/appflowy-integration/scripts/sync_docs.py` - Documentation sync script
- `skills/custom/appflowy-integration/scripts/sync_tasks.py` - Task sync script
- `skills/custom/appflowy-integration/workflows/sync-documentation.md` - Sync workflow doc
- `skills/custom/appflowy-integration/workflows/sync-tasks.md` - Task sync workflow doc

**Manual UI Setup Required:**
- Create "Documentation" and "Project Management" folders in AppFlowy UI
- Create databases with appropriate views (Grid for docs, Kanban for tasks)
- This is required due to AppFlowy API limitation (cannot create views via API)

---

## Success Criteria

1. AppFlowy API responds successfully with new HTTPS URL
2. 15 essential documentation files visible in Documentation folder hierarchy
3. Active tasks visible in Kanban board with correct status
4. Sync scripts work for incremental updates
5. No authentication errors or API failures

---

## Execution Order

1. **Phase 1**: Environment setup (requires credential verification)
2. **Manual checkpoint**: Create folders/databases in AppFlowy UI
3. **Phase 2**: Create and run documentation sync script
4. **Phase 3**: Create and run task sync script
5. **Phase 4**: Add automation and update skill documentation
