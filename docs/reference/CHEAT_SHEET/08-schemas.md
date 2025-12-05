# Schemas & Protocols

JSON schemas for structured communication and state management.

---

## Overview

| Schema Category | Count | Purpose |
|-----------------|-------|---------|
| Communication | 2 | Inter-agent messaging |
| State Management | 3 | Project and session state |
| Configuration | 2 | Agent and project config |

**Total Schemas:** 7

**Location:** `schemas/`

---

## Communication Schemas

Schemas for inter-agent messaging and coordination.

### communication-protocol.json

**Purpose:** Inter-agent messaging format

**Location:** `schemas/communication-protocol.json`

**Message Types:**
- Task assignments (Manager → Agent)
- Status updates (Agent → Manager)
- Blocker reports (Agent → Manager)
- Dependency requests (Agent → Agent via Manager)
- Code reviews (Manager → Agent)

**Example Message:**
```json
{
  "type": "task_assignment",
  "from": "manager",
  "to": "backend_developer",
  "task_id": "AUTH-001",
  "description": "Implement user registration endpoint",
  "priority": "high",
  "dependencies": [],
  "branch": "feature/user-registration",
  "timestamp": "2025-12-04T10:00:00Z"
}
```

**Status Update:**
```json
{
  "type": "status_update",
  "from": "backend_developer",
  "to": "manager",
  "task_id": "AUTH-001",
  "status": "completed",
  "summary": "Registration endpoint implemented with validation",
  "files_changed": ["src/auth/register.ts", "tests/auth/register.test.ts"],
  "next_steps": "Ready for code review",
  "timestamp": "2025-12-04T14:30:00Z"
}
```

**Blocker Report:**
```json
{
  "type": "blocker",
  "from": "frontend_developer",
  "to": "manager",
  "task_id": "AUTH-003",
  "blocker": "Need registration API endpoint before implementing UI",
  "blocked_by": "AUTH-001",
  "timestamp": "2025-12-04T11:00:00Z"
}
```

### communication-protocol-examples.json

**Purpose:** Tool use examples for improved accuracy

**Location:** `schemas/communication-protocol-examples.json`

**Impact:** Improved agent accuracy from 72% → 90% by providing concrete examples

**Contains:**
- 10+ message examples
- Common patterns
- Error cases
- Best practices

**Usage:**
- Reference in agent prompts
- Training examples
- Validation templates

---

## State Management Schemas

Schemas for project state and session continuity.

### state-management.json

**Purpose:** Project state format (legacy)

**Location:** `schemas/state-management.json`

**Note:** Superseded by three-file system (team-communication, session-progress, feature-tracking) but maintained for backward compatibility.

**Structure:**
```json
{
  "project": {
    "name": "MyApp",
    "phase": "development",
    "git_branch": "main"
  },
  "tasks": [
    {
      "id": "AUTH-001",
      "status": "completed",
      "assigned_to": "backend_developer"
    }
  ],
  "blockers": []
}
```

### session-progress.json

**Purpose:** Cross-session continuity tracking

**New in:** Autonomous agent integration (v1.2.0)

**Location:** `schemas/session-progress.json`

**Used by:** `.ai-agents/state/session-progress.json`

**Structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["last_session", "current_phase", "completed_tasks", "active_tasks"],
  "properties": {
    "last_session": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO 8601 timestamp of last session end"
    },
    "current_phase": {
      "type": "string",
      "description": "Current project phase (e.g., 'authentication-implementation')"
    },
    "completed_tasks": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of completed task IDs"
    },
    "active_tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "description", "status"],
        "properties": {
          "id": {"type": "string"},
          "description": {"type": "string"},
          "agent": {"type": "string"},
          "status": {
            "type": "string",
            "enum": ["not_started", "in_progress", "blocked"]
          },
          "blockers": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "blockers": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["task_id", "description"],
        "properties": {
          "task_id": {"type": "string"},
          "description": {"type": "string"},
          "blocked_by": {"type": "string"}
        }
      }
    },
    "next_priorities": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Ordered list of task IDs for next session"
    },
    "git_baseline": {
      "type": ["string", "null"],
      "description": "Git commit hash at session start"
    },
    "notes": {
      "type": "string",
      "description": "Free-form notes for next session"
    }
  }
}
```

**Benefits:**
- 50% faster session startup
- No need to rediscover state
- Clear priorities for next session
- Blocker tracking

**See:** [01-state-files.md](01-state-files.md#2-session-progress)

### feature-tracking.json

**Purpose:** Feature verification and pass/fail status

**New in:** Autonomous agent integration (v1.2.0)

**Location:** `schemas/feature-tracking.json`

**Used by:** `.ai-agents/state/feature-tracking.json`

**Structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["features", "summary"],
  "properties": {
    "features": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "description", "status"],
        "properties": {
          "id": {"type": "string"},
          "description": {"type": "string"},
          "status": {
            "type": "string",
            "enum": ["not_started", "in_progress", "passing", "failing"]
          },
          "implementation": {
            "type": "object",
            "properties": {
              "files": {
                "type": "array",
                "items": {"type": "string"}
              },
              "completed_by": {"type": ["string", "null"]},
              "completed_at": {
                "type": ["string", "null"],
                "format": "date-time"
              }
            }
          },
          "testing": {
            "type": "object",
            "required": ["test_status"],
            "properties": {
              "unit_tests": {"type": ["string", "null"]},
              "e2e_tests": {"type": ["string", "null"]},
              "test_status": {
                "type": "string",
                "enum": ["pending", "passing", "failing"]
              }
            }
          },
          "verified_by": {"type": ["string", "null"]},
          "verified_at": {
            "type": ["string", "null"],
            "format": "date-time"
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["total", "passing", "in_progress", "failing", "not_started"],
      "properties": {
        "total": {"type": "integer", "minimum": 0},
        "passing": {"type": "integer", "minimum": 0},
        "in_progress": {"type": "integer", "minimum": 0},
        "failing": {"type": "integer", "minimum": 0},
        "not_started": {"type": "integer", "minimum": 0}
      }
    }
  }
}
```

**Feature Completion Criteria:**
Features can ONLY be marked "passing" when ALL of these are met:
1. ✅ Code implemented
2. ✅ Unit tests written and passing
3. ✅ E2E tests written and passing (MANDATORY)
4. ✅ Code reviewed by Senior Engineer
5. ✅ Integration verified

**Benefits:**
- Prevents premature "done" declarations
- Enforces E2E testing
- Progress metrics (6/8 features passing)
- Code review verification

**See:** [01-state-files.md](01-state-files.md#3-feature-tracking)

### security-policy.json

**Purpose:** Security framework configuration for autonomous execution

**New in:** Autonomous agent integration (v1.2.0)

**Location:** `schemas/security-policy.json`

**Used by:** `scripts/security_validator.py`

**Structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["command_allowlist", "destructive_patterns", "filesystem_scope"],
  "properties": {
    "command_allowlist": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Commands allowed in autonomous mode"
    },
    "destructive_patterns": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Regex patterns to block (e.g., 'rm -rf /')"
    },
    "filesystem_scope": {
      "type": "object",
      "properties": {
        "allowed_paths": {
          "type": "array",
          "items": {"type": "string"}
        },
        "blocked_paths": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "require_approval": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Commands requiring human approval"
    }
  }
}
```

**Example Configuration:**
```json
{
  "command_allowlist": [
    "git",
    "npm",
    "python",
    "pytest",
    "node",
    "mkdir",
    "cp",
    "mv"
  ],
  "destructive_patterns": [
    "rm -rf /",
    "DROP TABLE",
    "DELETE FROM .* WHERE 1=1",
    "sudo rm"
  ],
  "filesystem_scope": {
    "allowed_paths": ["/project"],
    "blocked_paths": ["/", "/etc", "/usr", "/System"]
  },
  "require_approval": [
    "git push --force",
    "npm publish",
    "rm -rf"
  ]
}
```

**Security Layers:**
1. **Allowlist:** Only approved commands execute
2. **Destructive Patterns:** Block dangerous commands
3. **Filesystem Scope:** Restrict to project directory

**See:** `docs/guides/SECURITY.md` for complete guide

---

## Configuration Schemas

Schemas for agent and project configuration.

### agent-schema.json

**Purpose:** Agent configuration v2.0 with deferred loading support

**Location:** `schemas/agent-schema.json`

**Structure:**
```json
{
  "agent_id": "backend_developer",
  "base": "software-developer",
  "platform": "web/backend",
  "skills": {
    "always_loaded": ["mcp-builder"],
    "deferred": [
      {
        "path": "testing/webapp-testing",
        "triggers": ["test", "QA", "coverage"]
      }
    ]
  },
  "context": [
    "architecture.md",
    "api-contracts.md"
  ],
  "tools": ["read", "write", "bash"],
  "output_directory": ".ai-agents/composed/"
}
```

**New in v2.0:**
- Deferred skill loading
- Trigger word configuration
- Tool restrictions

**See:** [07-advanced.md](07-advanced.md#1-deferred-skill-loading)

### project-config.json

**Purpose:** Project configuration format

**Location:** `schemas/project-config.json`

**Structure:**
```json
{
  "project": {
    "name": "MyApp",
    "type": "web-app",
    "tech_stack": ["React", "Node.js", "PostgreSQL"]
  },
  "agents": {
    "manager": {...},
    "backend_dev": {...},
    "frontend_dev": {...}
  },
  "workflows": {
    "mode": "complex",
    "coordination": "task_tool"
  },
  "state_files": {
    "team_communication": ".ai-agents/state/team-communication.json",
    "session_progress": ".ai-agents/state/session-progress.json",
    "feature_tracking": ".ai-agents/state/feature-tracking.json"
  }
}
```

**Used by:** `compose-agent.py`, `generate-template.py`

---

## Schema Validation

### Using Schemas

**Python Example:**
```python
import json
import jsonschema

# Load schema
with open('schemas/session-progress.json') as f:
    schema = json.load(f)

# Load data
with open('.ai-agents/state/session-progress.json') as f:
    data = json.load(f)

# Validate
try:
    jsonschema.validate(instance=data, schema=schema)
    print("Valid!")
except jsonschema.ValidationError as e:
    print(f"Invalid: {e.message}")
```

**JavaScript Example:**
```javascript
const Ajv = require('ajv');
const ajv = new Ajv();

const schema = require('./schemas/feature-tracking.json');
const data = require('./.ai-agents/state/feature-tracking.json');

const validate = ajv.compile(schema);
const valid = validate(data);

if (!valid) {
  console.log(validate.errors);
}
```

### Validation Tools

| Tool | Language | Command |
|------|----------|---------|
| jsonschema | Python | `pip install jsonschema` |
| ajv | JavaScript | `npm install ajv` |
| json-schema-validator | CLI | `npm install -g json-schema-validator` |

---

## Best Practices

### Schema Usage

1. **Validate early** - Check state files before agent execution
2. **Version schemas** - Track changes with git
3. **Document examples** - Include sample data
4. **Test validators** - Ensure schemas catch errors

### State Files

5. **Back up regularly** - Especially feature-tracking.json
6. **Version control** - Commit state files for Complex Mode
7. **Validate before commit** - Ensure valid JSON
8. **Review manually** - Check feature completion criteria

### Security

9. **Review security-policy.json** - Adjust for project needs
10. **Test allowlist** - Verify commands work
11. **Block destructive patterns** - Add project-specific patterns
12. **Restrict filesystem** - Limit to project directory

---

## See Also

- **State Files:** [01-state-files.md](01-state-files.md)
- **Security:** `docs/guides/SECURITY.md`
- **Long-Running Agents:** `docs/guides/LONG_RUNNING_AGENTS.md`
- **Advanced Features:** [07-advanced.md](07-advanced.md)

---

[← Back to Index](index.md) | [Previous: Advanced Features](07-advanced.md) | [Next: Best Practices →](09-best-practices.md)
