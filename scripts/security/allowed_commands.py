"""
Configurable Command Allowlist for AI_agents

Provides configurable allowlists and blocklists that can be customized
per project. Extends the base security_validator.py with YAML configuration.

Usage:
    from scripts.security.allowed_commands import ConfigurableCommandValidator

    validator = ConfigurableCommandValidator(project_root)
    result = validator.validate("npm install express", "/project/dir")

Configuration in .ai-agents/config.yml:
    security:
      allowed_commands:
        - "git"
        - "npm"
        - "node"
      blocked_commands:
        - "rm -rf /"
        - "sudo"
      blocked_patterns:
        - "curl.*|.*bash"
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field

# Import base validator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from security_validator import (
    CommandValidator,
    SecurityLevel,
    ValidationResult
)


@dataclass
class SecurityConfig:
    """Security configuration loaded from YAML"""
    allowed_commands: Set[str] = field(default_factory=set)
    blocked_commands: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    warning_patterns: List[str] = field(default_factory=list)
    allow_network: bool = False
    strict_mode: bool = False
    log_blocked: bool = True
    log_warnings: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityConfig':
        """Create config from dictionary (YAML parsed data)"""
        return cls(
            allowed_commands=set(data.get('allowed_commands', [])),
            blocked_commands=data.get('blocked_commands', []),
            blocked_patterns=data.get('blocked_patterns', []),
            warning_patterns=data.get('warning_patterns', []),
            allow_network=data.get('allow_network', False),
            strict_mode=data.get('strict_mode', False),
            log_blocked=data.get('log_blocked', True),
            log_warnings=data.get('log_warnings', True)
        )


class ConfigurableCommandValidator(CommandValidator):
    """
    Command validator with configurable allowlists.

    Extends the base CommandValidator with:
    - YAML configuration support
    - Per-project allowlists
    - Per-project blocklists
    - Configurable patterns
    """

    def __init__(
        self,
        project_root: str,
        config_path: Optional[str] = None,
        config: Optional[SecurityConfig] = None
    ):
        """
        Initialize configurable validator.

        Args:
            project_root: Root directory of the project
            config_path: Path to config file (defaults to .ai-agents/config.yml)
            config: Pre-loaded SecurityConfig (optional)
        """
        super().__init__(project_root)

        self.config = config or self._load_config(config_path)
        self._apply_config()

    def _load_config(self, config_path: Optional[str] = None) -> SecurityConfig:
        """Load security configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join(self.project_root, '.ai-agents', 'config.yml')

        if not os.path.exists(config_path):
            return SecurityConfig()

        try:
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f) or {}

            security_config = full_config.get('security', {})
            return SecurityConfig.from_dict(security_config)

        except (yaml.YAMLError, IOError) as e:
            print(f"Warning: Could not load security config: {e}")
            return SecurityConfig()

    def _apply_config(self):
        """Apply loaded configuration to validator."""
        # Extend allowed commands if configured
        if self.config.allowed_commands:
            # In strict mode, replace. Otherwise, extend.
            if self.config.strict_mode:
                self.ALLOWED_COMMANDS = self.config.allowed_commands.copy()
            else:
                self.ALLOWED_COMMANDS = self.ALLOWED_COMMANDS.union(
                    self.config.allowed_commands
                )

        # Add blocked patterns
        if self.config.blocked_patterns:
            self.BLOCKED_PATTERNS = self.BLOCKED_PATTERNS + self.config.blocked_patterns

        # Add warning patterns
        if self.config.warning_patterns:
            self.WARNING_PATTERNS = self.WARNING_PATTERNS + self.config.warning_patterns

        # Update network setting
        self.allow_network = self.config.allow_network

    def validate(self, command: str, working_dir: str) -> ValidationResult:
        """
        Validate command with configuration.

        Adds explicit blocked command checking.
        """
        command = command.strip()

        # Check explicit blocklist first
        result = self._check_blocked_commands(command)
        if not result.allowed:
            if self.config.log_blocked:
                self._log_blocked(command, result)
            return result

        # Run base validation
        result = super().validate(command, working_dir)

        # Log if configured
        if not result.allowed and self.config.log_blocked:
            self._log_blocked(command, result)
        elif result.level == SecurityLevel.WARNING and self.config.log_warnings:
            self._log_warning(command, result)

        return result

    def _check_blocked_commands(self, command: str) -> ValidationResult:
        """Check against explicit blocklist."""
        for blocked in self.config.blocked_commands:
            if blocked in command:
                return ValidationResult(
                    SecurityLevel.BLOCKED,
                    f"Command matches blocklist: {blocked}",
                    "This command has been explicitly blocked in security config"
                )

        return ValidationResult(SecurityLevel.ALLOWED)

    def _log_blocked(self, command: str, result: ValidationResult):
        """Log blocked command to security log."""
        log_dir = Path(self.project_root) / '.ai-agents' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'security.log'

        from datetime import datetime
        entry = (
            f"[{datetime.now().isoformat()}] BLOCKED: {command}\n"
            f"  Reason: {result.reason}\n"
            f"  Suggestion: {result.suggestion}\n\n"
        )

        with open(log_file, 'a') as f:
            f.write(entry)

    def _log_warning(self, command: str, result: ValidationResult):
        """Log warning to security log."""
        log_dir = Path(self.project_root) / '.ai-agents' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'security.log'

        from datetime import datetime
        entry = (
            f"[{datetime.now().isoformat()}] WARNING: {command}\n"
            f"  Reason: {result.reason}\n\n"
        )

        with open(log_file, 'a') as f:
            f.write(entry)


# Preset configurations for common scenarios

PRESETS = {
    'minimal': SecurityConfig(
        allowed_commands={'git', 'ls', 'cat', 'grep', 'pwd'},
        strict_mode=True,
        allow_network=False
    ),

    'development': SecurityConfig(
        allowed_commands={
            'git', 'npm', 'node', 'npx', 'yarn',
            'python', 'python3', 'pip', 'pip3',
            'ls', 'cat', 'grep', 'find', 'head', 'tail',
            'mkdir', 'cp', 'mv', 'touch', 'rm'
        },
        blocked_commands=['rm -rf', 'sudo'],
        allow_network=True
    ),

    'ci_cd': SecurityConfig(
        allowed_commands={
            'git', 'npm', 'node', 'yarn',
            'docker', 'docker-compose',
            'kubectl', 'helm',
            'ls', 'cat', 'grep'
        },
        blocked_commands=['git push --force', 'rm -rf /'],
        strict_mode=True,
        allow_network=True
    ),

    'paranoid': SecurityConfig(
        allowed_commands={'ls', 'cat', 'pwd', 'git status'},
        blocked_patterns=[
            r'rm\s+',
            r'mv\s+',
            r'>\s*',  # Any redirection
            r'\|\s*'  # Any pipe
        ],
        strict_mode=True,
        allow_network=False
    )
}


def get_preset(name: str) -> SecurityConfig:
    """Get a preset security configuration."""
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
    return PRESETS[name]


def create_validator(
    project_root: str,
    preset: Optional[str] = None,
    config_path: Optional[str] = None
) -> ConfigurableCommandValidator:
    """
    Create a validator with optional preset.

    Args:
        project_root: Project root directory
        preset: Preset name (minimal, development, ci_cd, paranoid)
        config_path: Custom config path

    Returns:
        ConfigurableCommandValidator instance
    """
    config = None
    if preset:
        config = get_preset(preset)

    return ConfigurableCommandValidator(
        project_root,
        config_path=config_path,
        config=config
    )


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python allowed_commands.py <project_root> <command> [--preset NAME]")
        print("\nPresets: minimal, development, ci_cd, paranoid")
        print("\nExample:")
        print("  python allowed_commands.py /project 'npm install' --preset development")
        sys.exit(1)

    project_root = sys.argv[1]
    command = sys.argv[2]

    # Check for preset flag
    preset = None
    if '--preset' in sys.argv:
        preset_idx = sys.argv.index('--preset')
        if preset_idx + 1 < len(sys.argv):
            preset = sys.argv[preset_idx + 1]

    validator = create_validator(project_root, preset=preset)
    result = validator.validate(command, project_root)

    if result.allowed:
        if result.level == SecurityLevel.WARNING:
            print(f"⚠️  WARNING: {result.reason}")
        print(f"✅ ALLOWED")
    else:
        print(f"❌ BLOCKED: {result.reason}")
        if result.suggestion:
            print(f"💡 {result.suggestion}")
        sys.exit(1)
