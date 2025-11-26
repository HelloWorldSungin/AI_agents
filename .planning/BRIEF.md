# AI_agents Repository Restructuring

## Vision
Transform the AI_agents repository from its current cluttered state into a clean, well-organized resource hub for Claude Code tools, skills, and prompts.

## Current State

### Problems Identified

**1. Root-level clutter**
- 12 large markdown files (700-2400 lines each) at repo root
- Makes it hard to find the README and understand repo purpose
- Mix of guides, reports, and reference docs with no clear organization

**2. Skills organization chaos**
- `skills/anthropic/` - Git submodule (external)
- `skills/taches-cc/` - Appears to duplicate `taches-cc-resources/skills/`
- `skills/custom/` - Custom skills
- `skills/core/`, `design/`, `documents/`, `communication/` - Category dirs
- `taches-cc-resources/` - Git submodule (external)
- `.claude/skills/` - Where Claude Code expects skills
- 6 documentation .md files inside `skills/` directory

**3. Documentation scattered everywhere**
- `docs/` - Only 1 file (underused)
- `skills/*.md` - 6 guide files
- Root `*.md` - 12 guide files
- `taches-cc-resources/docs/` - More docs

**4. Empty/underused directories**
- `workflows/` - Empty
- `templates/*/` - Empty subdirectories

### Current Structure
```
AI_agents/
├── .ai-agents/
├── .claude/              # Commands, agents, settings
│   ├── commands/
│   ├── agents/
│   └── skills/           # Copies for Claude Code discovery
├── base/                 # Role prompts (architect, manager, etc.)
├── docs/                 # Nearly empty (1 file)
├── examples/
├── memory/
├── platforms/
├── prompts/
├── schemas/
├── scripts/
├── skills/               # Multiple skill sources + docs
│   ├── anthropic/        # Submodule
│   ├── taches-cc/        # Duplicate?
│   ├── custom/
│   └── [6 .md files]
├── starter-templates/
├── taches-cc-resources/  # Submodule
├── templates/            # Empty subdirs
├── tests/
├── tools/
├── workflows/            # Empty
└── [12 large .md files]  # Cluttered root
```

## Target State

### Design Principles
1. **Clear entry point** - README.md is the only large file at root
2. **Obvious organization** - Directory names explain contents
3. **Single source of truth** - No duplicated skills
4. **Claude Code compatible** - `.claude/` properly configured
5. **Submodules as imports** - External repos clearly marked

### Proposed Structure
```
AI_agents/
├── .claude/                    # Claude Code configuration
│   ├── commands/               # Slash commands (wrappers + local)
│   ├── agents/                 # Subagent definitions
│   ├── skills/                 # Symlinks to skills for discovery
│   └── settings.local.json
├── .planning/                  # Planning artifacts (this project)
├── docs/                       # ALL documentation lives here
│   ├── guides/                 # How-to guides
│   │   ├── architecture.md
│   │   ├── skills-guide.md
│   │   ├── parallel-execution.md
│   │   └── ...
│   ├── reference/              # Reference documentation
│   │   ├── faq.md
│   │   ├── cheat-sheet.md
│   │   └── ...
│   └── archive/                # Historical/completed docs
│       ├── migration-guide.md
│       ├── phase2-summary.md
│       └── ...
├── external/                   # Git submodules (renamed for clarity)
│   ├── anthropic-skills/       # Was: skills/anthropic
│   └── taches-cc-resources/    # Was: taches-cc-resources
├── prompts/                    # Prompt templates and roles
│   ├── roles/                  # Was: base/
│   └── templates/              # Was: templates/ (if useful)
├── scripts/                    # Setup and utility scripts
├── skills/                     # LOCAL skills only (no submodules)
│   ├── custom/                 # User-created skills
│   └── examples/               # Example skill implementations
├── schemas/                    # JSON schemas
├── tests/                      # Test files
└── README.md                   # Single root documentation file
```

## Success Criteria
- [ ] Root directory has only README.md and directories
- [ ] All documentation consolidated in `docs/`
- [ ] No duplicate skills across directories
- [ ] `.claude/skills/` properly symlinks for Claude Code discovery
- [ ] Empty directories either populated or removed
- [ ] Submodules clearly identified in `external/`
- [ ] Git history preserved (moves, not delete+create)

## Constraints
- Must preserve git submodules (anthropic-skills, taches-cc-resources)
- Must maintain compatibility with `setup-commands.py` script
- Cannot break existing `.claude/commands/` references
