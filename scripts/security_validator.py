"""
Security validation for autonomous agent execution.

Implements three-layer defense-in-depth strategy:
1. Command allowlist - Only permitted commands can execute
2. Filesystem restrictions - Operations must be within project scope
3. Destructive operation detection - Block dangerous patterns

Based on Anthropic's recommendations for long-running agents.
"""

import os
import re
from pathlib import Path
from typing import Tuple, Optional, List, Dict
from enum import Enum


class SecurityLevel(Enum):
    """Security check result levels"""
    ALLOWED = "allowed"
    WARNING = "warning"  # Log but allow
    BLOCKED = "blocked"  # Prevent execution


class ValidationResult:
    """Result of security validation"""

    def __init__(
        self,
        level: SecurityLevel,
        reason: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        self.level = level
        self.reason = reason
        self.suggestion = suggestion

    @property
    def allowed(self) -> bool:
        """Whether command is allowed to execute"""
        return self.level != SecurityLevel.BLOCKED

    def __repr__(self) -> str:
        if self.level == SecurityLevel.ALLOWED:
            return f"ValidationResult(ALLOWED)"
        return f"ValidationResult({self.level.value.upper()}: {self.reason})"


class CommandValidator:
    """
    Validates commands for security before autonomous execution.

    Usage:
        validator = CommandValidator("/path/to/project")
        result = validator.validate("rm file.txt", "/path/to/project/src")

        if result.allowed:
            # Execute command
            pass
        else:
            print(f"BLOCKED: {result.reason}")
            print(f"Suggestion: {result.suggestion}")
    """

    # Layer 1: Command Allowlist
    # Only these commands are permitted in autonomous mode
    ALLOWED_COMMANDS = {
        # File inspection (read-only operations)
        'cat', 'ls', 'head', 'tail', 'find', 'grep', 'rg', 'tree', 'file',
        'wc', 'diff', 'less', 'more',

        # Development tools
        'npm', 'node', 'npx', 'yarn', 'pnpm',
        'python', 'python3', 'pip', 'pip3', 'pytest',
        'git',
        'cargo', 'rustc',
        'go',
        'ruby', 'gem',
        'java', 'javac', 'maven', 'gradle',

        # Build tools
        'make', 'cmake',
        'docker', 'docker-compose',

        # Process management (limited)
        'ps', 'kill', 'pkill',

        # Text processing
        'sed', 'awk', 'cut', 'sort', 'uniq', 'jq',

        # Testing frameworks
        'vitest', 'jest', 'mocha', 'playwright',

        # Utilities
        'pwd', 'which', 'whereis', 'date', 'echo', 'printf',
        'touch', 'mkdir', 'cp', 'mv',
    }

    # Layer 2: Destructive Patterns
    # These patterns are never allowed, even if command is in allowlist
    BLOCKED_PATTERNS = [
        # Filesystem destruction
        r'rm\s+-rf\s+/',
        r'rm\s+-r\s+/',
        r'rm\s+-rf\s+\.',
        r'rm\s+--recursive\s+--force',

        # Data destruction
        r'dd\s+if=',
        r'mkfs',
        r'>\s*/dev/sd',
        r':\s*>\s*/dev/sd',

        # Download and execute
        r'curl.*\|\s*bash',
        r'curl.*\|\s*sh',
        r'wget.*\|\s*bash',
        r'wget.*\|\s*sh',

        # Privilege escalation
        r'sudo\s+su',
        r'sudo\s+-i',

        # System modification
        r'chmod\s+777',
        r'chown\s+-R\s+root',

        # Network exposure
        r'nc\s+-l',  # netcat listening
        r'python.*-m\s+http\.server',  # HTTP server on all interfaces

        # Force git operations
        r'git\s+push\s+--force',
        r'git\s+push\s+-f',
        r'git\s+reset\s+--hard\s+HEAD~',
    ]

    # Suspicious patterns that warrant warnings
    WARNING_PATTERNS = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'subprocess\.call',
        r'os\.system',
        r'rm\s+.*\*',  # Wildcards with rm
        r'chmod\s+[0-7]{3}',  # Permission changes
    ]

    def __init__(self, project_root: str, allow_network: bool = False):
        """
        Initialize validator.

        Args:
            project_root: Root directory of the project (operations restricted to this)
            allow_network: Whether to allow network operations (default: False)
        """
        self.project_root = Path(project_root).resolve()
        self.allow_network = allow_network

        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

    def validate(self, command: str, working_dir: str) -> ValidationResult:
        """
        Validate a command for security.

        Args:
            command: The command to validate
            working_dir: Directory where command will execute

        Returns:
            ValidationResult indicating whether command is allowed
        """
        command = command.strip()

        # Layer 1: Check command allowlist
        result = self._check_allowlist(command)
        if not result.allowed:
            return result

        # Layer 2: Check for destructive patterns
        result = self._check_destructive_patterns(command)
        if not result.allowed:
            return result

        # Layer 3: Check filesystem scope
        result = self._check_filesystem_scope(command, working_dir)
        if not result.allowed:
            return result

        # Check for warning patterns
        result = self._check_warning_patterns(command)
        if result.level == SecurityLevel.WARNING:
            return result

        # All checks passed
        return ValidationResult(SecurityLevel.ALLOWED)

    def _check_allowlist(self, command: str) -> ValidationResult:
        """Check if command is in allowlist"""
        # Extract command name (first word)
        cmd_name = command.split()[0] if command else ""

        # Handle paths (./script.sh, /usr/bin/node)
        if '/' in cmd_name:
            cmd_name = os.path.basename(cmd_name)

        if cmd_name not in self.ALLOWED_COMMANDS:
            return ValidationResult(
                SecurityLevel.BLOCKED,
                f"Command '{cmd_name}' not in allowlist",
                "Only approved development commands are permitted. "
                "See SECURITY.md for full list of allowed commands."
            )

        return ValidationResult(SecurityLevel.ALLOWED)

    def _check_destructive_patterns(self, command: str) -> ValidationResult:
        """Check for known destructive patterns"""
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return ValidationResult(
                    SecurityLevel.BLOCKED,
                    f"Destructive pattern detected: {pattern}",
                    "This operation is too dangerous for autonomous execution. "
                    "Modify the command to be more specific and safe."
                )

        return ValidationResult(SecurityLevel.ALLOWED)

    def _check_warning_patterns(self, command: str) -> ValidationResult:
        """Check for suspicious patterns (non-blocking warnings)"""
        for pattern in self.WARNING_PATTERNS:
            if re.search(pattern, command):
                return ValidationResult(
                    SecurityLevel.WARNING,
                    f"Suspicious pattern detected: {pattern}",
                    "This command will execute but has been flagged for review."
                )

        return ValidationResult(SecurityLevel.ALLOWED)

    def _check_filesystem_scope(
        self,
        command: str,
        working_dir: str
    ) -> ValidationResult:
        """
        Check if command operations are within project scope.

        This is a simplified check - full implementation would need
        to parse command arguments and check all file paths.
        """
        try:
            wd_path = Path(working_dir).resolve()

            # Verify working directory is within project
            if not self._is_within_project(wd_path):
                return ValidationResult(
                    SecurityLevel.BLOCKED,
                    f"Working directory outside project: {working_dir}",
                    f"Operations must be within: {self.project_root}"
                )

            # Check for absolute paths in command
            # This is a basic check - could be more sophisticated
            if re.search(r'\s/(?!tmp|var/tmp)', command):
                # Found absolute path (not /tmp or /var/tmp)
                return ValidationResult(
                    SecurityLevel.WARNING,
                    "Command contains absolute path outside project",
                    "Use relative paths or paths within project directory"
                )

            return ValidationResult(SecurityLevel.ALLOWED)

        except Exception as e:
            return ValidationResult(
                SecurityLevel.BLOCKED,
                f"Error validating filesystem scope: {str(e)}",
                "Verify paths are valid and within project"
            )

    def _is_within_project(self, path: Path) -> bool:
        """Check if path is within project root"""
        try:
            path.resolve().relative_to(self.project_root)
            return True
        except ValueError:
            return False


# Convenience functions for common use cases

def validate_command(
    command: str,
    project_root: str,
    working_dir: str
) -> Tuple[bool, Optional[str]]:
    """
    Simple validation function.

    Returns:
        (allowed: bool, reason: Optional[str])
    """
    validator = CommandValidator(project_root)
    result = validator.validate(command, working_dir)
    return result.allowed, result.reason


def validate_with_details(
    command: str,
    project_root: str,
    working_dir: str
) -> Dict:
    """
    Validation with detailed response.

    Returns:
        Dictionary with validation details
    """
    validator = CommandValidator(project_root)
    result = validator.validate(command, working_dir)

    return {
        "allowed": result.allowed,
        "level": result.level.value,
        "reason": result.reason,
        "suggestion": result.suggestion,
        "command": command
    }


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python security_validator.py <project_root> <command>")
        print("\nExample:")
        print("  python security_validator.py /path/to/project 'git status'")
        sys.exit(1)

    project_root = sys.argv[1]
    command = sys.argv[2]
    working_dir = project_root

    validator = CommandValidator(project_root)
    result = validator.validate(command, working_dir)

    if result.allowed:
        if result.level == SecurityLevel.WARNING:
            print(f"⚠️  WARNING: {result.reason}")
            print(f"💡 {result.suggestion}")
            print(f"✅ Command will execute anyway")
        else:
            print(f"✅ ALLOWED: Command passed security checks")
    else:
        print(f"❌ BLOCKED: {result.reason}")
        print(f"💡 {result.suggestion}")
        sys.exit(1)
