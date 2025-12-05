# Security Guide for Autonomous Agent Execution

## Overview

This guide describes the security framework for autonomous agent execution in the AI_agents system. Based on Anthropic's defense-in-depth recommendations, it implements three layers of security to protect against accidental or malicious operations.

## Three-Layer Defense

### Layer 1: Command Allowlist

Only approved commands can execute in autonomous mode.

**Allowed Commands** (`security_validator.py`):
- File inspection: `cat`, `ls`, `grep`, `find`, `tree`
- Development: `npm`, `node`, `python`, `pytest`, `git`
- Build tools: `make`, `docker`, `cargo`
- Process management: `ps`, `kill` (limited)

**Not Allowed**:
- System modification: `sudo`, `chmod 777`, `chown`
- Destructive operations: `rm -rf`, `dd`, `mkfs`
- Network exposure: `nc -l`, arbitrary HTTP servers

### Layer 2: Destructive Pattern Detection

Dangerous patterns are blocked even if command is allowed.

**Blocked Patterns**:
```bash
# Filesystem destruction
rm -rf /
rm -r /
dd if=/dev/zero of=/dev/sda

# Download and execute
curl | bash
wget | sh

# Force git operations
git push --force
git reset --hard HEAD~10
```

### Layer 3: Filesystem Scope Restrictions

All operations must be within the project directory.

**Allowed**:
```bash
# Within project
cd /Users/username/project/src
git status
npm test
```

**Blocked**:
```bash
# Outside project
cd /etc
rm /var/log/*
touch /usr/bin/malicious
```

## Using the Security Validator

### Python API

```python
from scripts.security_validator import CommandValidator, SecurityLevel

# Initialize validator
validator = CommandValidator("/path/to/project")

# Validate command
result = validator.validate("git status", "/path/to/project")

if result.allowed:
    # Execute command
    subprocess.run(["git", "status"])
else:
    print(f"BLOCKED: {result.reason}")
    print(f"Suggestion: {result.suggestion}")
```

### Command Line

```bash
# Validate a command
python scripts/security_validator.py /path/to/project "git status"

# Output:
# ✅ ALLOWED: Command passed security checks

# Block dangerous command
python scripts/security_validator.py /path/to/project "rm -rf /"

# Output:
# ❌ BLOCKED: Destructive pattern detected: rm\s+-rf\s+/
# 💡 This operation is too dangerous for autonomous execution
```

## Security Policy Configuration

Create `.ai-agents/security-policy.json` to customize security settings:

```json
{
  "project_root": "/path/to/project",
  "enforcement_level": "strict",
  "allowed_commands": ["git", "npm", "python", "pytest"],
  "blocked_patterns": [
    {
      "pattern": "rm\\s+-rf",
      "reason": "Prevent accidental deletion",
      "severity": "critical"
    }
  ],
  "filesystem_restrictions": {
    "allowed_paths": ["src", "tests", "docs"],
    "read_only_paths": ["package.json", ".env.example"]
  }
}
```

See `schemas/security-policy.json` for full schema.

## Enforcement Levels

### Strict (Recommended for Autonomous)

- All three layers enforced
- No exceptions without explicit approval
- All commands logged
- Blocks on any security violation

### Moderate (Development)

- Allowlist enforced
- Warnings for suspicious patterns
- Destructive patterns still blocked
- User can override with confirmation

### Audit Only (Testing)

- All commands allowed
- Everything logged for review
- No blocking, only warnings
- Use for testing security policies

## Best Practices

### For Autonomous Agent Development

1. **Always use security validator** in autonomous execution
2. **Test with strict mode** before deploying
3. **Review audit logs** regularly
4. **Start with minimal allowlist** and expand as needed
5. **Never disable security** in production

### For Adding New Commands

If you need to allow a new command:

1. **Evaluate necessity**: Is this command truly needed?
2. **Check destructive potential**: Can it cause harm?
3. **Add to allowlist**: Update `ALLOWED_COMMANDS`
4. **Add safeguards**: Create blocking patterns if needed
5. **Test thoroughly**: Verify security still works

### For Project-Specific Exceptions

Use security policy exceptions for one-off needs:

```json
{
  "exceptions": [
    {
      "command": "chmod +x scripts/deploy.sh",
      "reason": "Deployment script needs execution permission",
      "approved_by": "tech-lead@company.com",
      "expires_at": "2025-12-31T23:59:59Z"
    }
  ]
}
```

## Common Scenarios

### Scenario 1: Agent Needs to Create File

```python
# BLOCKED: absolute path outside project
result = validator.validate("touch /tmp/file.txt", working_dir)

# ALLOWED: within project
result = validator.validate("touch temp/file.txt", working_dir)
```

### Scenario 2: Agent Needs to Install Dependencies

```python
# ALLOWED: npm is in allowlist
result = validator.validate("npm install", working_dir)

# ALLOWED: pip is in allowlist
result = validator.validate("pip install -r requirements.txt", working_dir)

# BLOCKED: curl piped to bash
result = validator.validate("curl install.sh | bash", working_dir)
```

### Scenario 3: Agent Needs to Clean Build Artifacts

```python
# ALLOWED: specific file deletion
result = validator.validate("rm dist/bundle.js", working_dir)

# ALLOWED: safe wildcard in project
result = validator.validate("rm -rf dist/*", working_dir)

# BLOCKED: dangerous wildcard at root
result = validator.validate("rm -rf /", working_dir)
```

## Audit Logging

All security events are logged to `.ai-agents/logs/security-audit.log`:

```
2024-01-15T10:30:00Z [ALLOWED] git status (working_dir: /project)
2024-01-15T10:30:15Z [WARNING] rm dist/* (pattern: wildcards with rm)
2024-01-15T10:30:30Z [BLOCKED] rm -rf / (pattern: filesystem destruction)
```

Review logs regularly to:
- Identify suspicious patterns
- Find commands that need allowlisting
- Detect potential security issues
- Audit autonomous agent behavior

## Integrating with Orchestration

```python
from scripts.security_validator import CommandValidator

class SecureOrchestrator:
    def __init__(self, project_root):
        self.validator = CommandValidator(project_root)

    def execute_agent_command(self, agent, command):
        # Validate before executing
        result = self.validator.validate(
            command,
            agent.working_dir
        )

        if not result.allowed:
            return {
                "status": "blocked",
                "reason": result.reason,
                "suggestion": result.suggestion
            }

        # Execute command
        return agent.execute(command)
```

## Testing Security

Test your security configuration:

```bash
# Test allowlist
python scripts/security_validator.py . "unknown-command"
# Should block

# Test destructive patterns
python scripts/security_validator.py . "rm -rf /"
# Should block

# Test filesystem scope
python scripts/security_validator.py . "touch /etc/file"
# Should block

# Test allowed command
python scripts/security_validator.py . "git status"
# Should allow
```

## Troubleshooting

### Command Blocked Incorrectly

If a legitimate command is blocked:

1. Check if command is in allowlist
2. Review blocked patterns for false positive
3. Add exception to security policy
4. Consider if command is truly necessary

### Too Many Warnings

If getting excessive warnings:

1. Review warning patterns
2. Adjust enforcement level
3. Add exceptions for known-safe commands
4. Consider if warnings indicate real issues

### Need to Allow Dangerous Command

If you must allow a risky command:

1. Document why it's necessary
2. Add specific exception (not blanket allowance)
3. Set expiration date
4. Require approval from tech lead
5. Add extra validation

## Related Documentation

- Security validator: `scripts/security_validator.py`
- Security policy schema: `schemas/security-policy.json`
- Autonomous agent patterns: `docs/guides/LONG_RUNNING_AGENTS.md`
