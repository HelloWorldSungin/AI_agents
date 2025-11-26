# AI_agents Restructuring Roadmap

## Milestone: v1.0 - Clean Structure

### Phase 01: Documentation Consolidation
**Objective:** Move all root-level documentation into `docs/` with proper categorization.

**Scope:**
- Create `docs/guides/`, `docs/reference/`, `docs/archive/` directories
- Move 12 root .md files (except README.md) to appropriate subdirs
- Update any internal links between documents
- Keep README.md at root (update to reference new locations)

**Files affected:** 12 markdown files at root
**Risk:** Low - just file moves
**Status:** Not started

---

### Phase 02: Skills Deduplication
**Objective:** Remove duplicate skills, establish single source of truth.

**Scope:**
- Analyze `skills/taches-cc/` vs `taches-cc-resources/skills/` for duplicates
- Remove `skills/taches-cc/` if it's a duplicate
- Move `skills/*.md` docs into `docs/reference/skills/`
- Keep only `skills/custom/` and `skills/examples/` for local skills

**Files affected:** skills/ directory restructure
**Risk:** Medium - need to verify no unique content in duplicates
**Status:** Not started

---

### Phase 03: Submodule Reorganization
**Objective:** Move git submodules to `external/` for clarity.

**Scope:**
- Create `external/` directory
- Move `skills/anthropic/` → `external/anthropic-skills/`
- Move `taches-cc-resources/` → `external/taches-cc-resources/`
- Update `.gitmodules` paths
- Update `setup-commands.py` to use new paths

**Files affected:** .gitmodules, setup-commands.py, submodule locations
**Risk:** Medium - submodule path changes require careful handling
**Status:** Not started

---

### Phase 04: Claude Code Integration Fix
**Objective:** Ensure `.claude/skills/` properly discovers skills.

**Scope:**
- Update `setup-commands.py` to handle new external/ paths
- Create proper symlinks in `.claude/skills/`
- Test skill invocation works
- Update `.claude/commands/` wrappers if needed

**Files affected:** scripts/setup-commands.py, .claude/skills/, .claude/commands/
**Risk:** Medium - must maintain functionality
**Status:** Not started

---

### Phase 05: Prompts Consolidation
**Objective:** Organize prompt-related files.

**Scope:**
- Move `base/` contents → `prompts/roles/`
- Evaluate `templates/` - populate or remove empty dirs
- Consolidate any scattered prompt files

**Files affected:** base/, templates/, prompts/
**Risk:** Low - organizational change
**Status:** Not started

---

### Phase 06: Cleanup Empty Directories
**Objective:** Remove or repurpose empty directories.

**Scope:**
- Remove `workflows/` if truly unused
- Remove empty `templates/*/` subdirs or populate them
- Verify `memory/`, `platforms/`, `examples/` have content or remove
- Update README.md with final structure

**Files affected:** Various empty directories
**Risk:** Low - cleanup only
**Status:** Not started

---

## Phase Summary

| Phase | Name | Risk | Dependencies |
|-------|------|------|--------------|
| 01 | Documentation Consolidation | Low | None |
| 02 | Skills Deduplication | Medium | None |
| 03 | Submodule Reorganization | Medium | Phase 02 |
| 04 | Claude Code Integration Fix | Medium | Phase 03 |
| 05 | Prompts Consolidation | Low | None |
| 06 | Cleanup Empty Directories | Low | All previous |

## Execution Notes

- Phases 01, 02, 05 can run in parallel (no dependencies)
- Phase 03 depends on Phase 02 (need to know what's in skills/)
- Phase 04 depends on Phase 03 (paths must be finalized)
- Phase 06 is final cleanup after everything else

## Commit Strategy

Each phase = one commit with descriptive message:
- `refactor: consolidate documentation into docs/`
- `refactor: deduplicate skills directory`
- `refactor: move submodules to external/`
- `fix: update Claude Code skill discovery paths`
- `refactor: consolidate prompts and roles`
- `chore: remove empty directories`
