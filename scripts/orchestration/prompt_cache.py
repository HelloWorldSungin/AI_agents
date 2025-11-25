#!/usr/bin/env python3
"""
Prompt Caching Utility for Multi-Agent Orchestration

Implements Anthropic's prompt caching for cost reduction (up to 90%) on repeated
agent calls. Based on: https://www.anthropic.com/engineering/advanced-tool-use

Features:
- Automatic cache control headers for stable content
- Separation of stable vs dynamic context
- Cache statistics and monitoring
- Integration with deferred skill loading

Usage:
    from prompt_cache import CachedAnthropicClient

    client = CachedAnthropicClient()
    response = client.call_with_cache(
        system_prompt=base_prompt,
        messages=[{"role": "user", "content": "..."}],
        cache_config={"stable_tokens": 5000}
    )

Requirements:
    - anthropic>=0.25.0 (with prompt caching support)
    - ANTHROPIC_API_KEY environment variable
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class CacheStats:
    """Track prompt caching statistics"""
    total_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    tokens_saved: int = 0
    cost_savings_estimate: float = 0.0  # In dollars
    last_updated: str = ""

    def update(self, hit: bool, tokens: int = 0):
        self.total_calls += 1
        if hit:
            self.cache_hits += 1
            self.tokens_saved += tokens
            # Rough estimate: $0.003 per 1K tokens saved
            self.cost_savings_estimate += (tokens / 1000) * 0.003
        else:
            self.cache_misses += 1
        self.last_updated = datetime.now().isoformat()

    @property
    def hit_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.cache_hits / self.total_calls

    def to_dict(self) -> Dict:
        return {
            "total_calls": self.total_calls,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "tokens_saved": self.tokens_saved,
            "cost_savings_estimate": f"${self.cost_savings_estimate:.4f}",
            "last_updated": self.last_updated
        }


@dataclass
class AgentPromptConfig:
    """Configuration for an agent's prompt structure with caching"""
    agent_id: str
    stable_system_prompt: str  # Base prompt + platforms (rarely changes)
    stable_skills: List[str] = field(default_factory=list)  # always_loaded skills
    deferred_skills: List[Dict] = field(default_factory=list)  # Skill manifest
    dynamic_context: str = ""  # Current task context (changes often)

    def get_cache_key(self) -> str:
        """Generate cache key from stable content"""
        stable_content = self.stable_system_prompt + "".join(self.stable_skills)
        return hashlib.md5(stable_content.encode()).hexdigest()[:16]


class CachedAnthropicClient:
    """
    Anthropic client wrapper with prompt caching support.

    Implements the cache_control block pattern for stable system prompts,
    allowing up to 90% cost reduction on repeated API calls.
    """

    def __init__(self, api_key: Optional[str] = None):
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.stats = CacheStats()
        self._prompt_configs: Dict[str, AgentPromptConfig] = {}

    def register_agent(self, config: AgentPromptConfig):
        """Register an agent's prompt configuration for caching"""
        self._prompt_configs[config.agent_id] = config

    def _build_system_with_cache(
        self,
        stable_content: str,
        dynamic_content: Optional[str] = None
    ) -> List[Dict]:
        """
        Build system prompt with cache control blocks.

        Structure:
        [
            {"type": "text", "text": stable_content, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dynamic_content}  # No cache control - changes
        ]
        """
        system_blocks = []

        # Stable content with cache control
        if stable_content:
            system_blocks.append({
                "type": "text",
                "text": stable_content,
                "cache_control": {"type": "ephemeral"}
            })

        # Dynamic content without cache control
        if dynamic_content:
            system_blocks.append({
                "type": "text",
                "text": dynamic_content
            })

        return system_blocks

    def call_with_cache(
        self,
        agent_id: str,
        messages: List[Dict],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8000,
        dynamic_context: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, Dict]:
        """
        Call the API with prompt caching for registered agents.

        Args:
            agent_id: Registered agent ID
            messages: Conversation messages
            model: Model to use
            max_tokens: Maximum response tokens
            dynamic_context: Optional current task context
            **kwargs: Additional API parameters

        Returns:
            Tuple of (response_text, cache_info)
        """
        if agent_id not in self._prompt_configs:
            raise ValueError(f"Agent {agent_id} not registered. Call register_agent first.")

        config = self._prompt_configs[agent_id]

        # Build stable content (base prompt + always_loaded skills)
        stable_parts = [config.stable_system_prompt]
        stable_parts.extend(config.stable_skills)
        stable_content = "\n\n".join(stable_parts)

        # Build dynamic content
        dynamic_parts = []
        if config.deferred_skills:
            # Add skill manifest (lightweight reference to available skills)
            manifest = self._build_skill_manifest(config.deferred_skills)
            dynamic_parts.append(manifest)
        if dynamic_context:
            dynamic_parts.append(dynamic_context)
        elif config.dynamic_context:
            dynamic_parts.append(config.dynamic_context)

        dynamic_content = "\n\n".join(dynamic_parts) if dynamic_parts else None

        # Build system with cache control
        system = self._build_system_with_cache(stable_content, dynamic_content)

        # Make API call
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                **kwargs
            )

            # Extract cache info from response
            cache_info = self._extract_cache_info(response)

            # Update stats
            cache_hit = cache_info.get("cache_read_input_tokens", 0) > 0
            self.stats.update(hit=cache_hit, tokens=cache_info.get("cache_read_input_tokens", 0))

            return response.content[0].text, cache_info

        except Exception as e:
            self.stats.update(hit=False)
            raise

    def call_simple(
        self,
        system_prompt: str,
        messages: List[Dict],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8000,
        enable_cache: bool = True,
        **kwargs
    ) -> Tuple[str, Dict]:
        """
        Simple API call with optional caching for one-off prompts.

        Args:
            system_prompt: Full system prompt
            messages: Conversation messages
            model: Model to use
            max_tokens: Maximum response tokens
            enable_cache: Whether to enable prompt caching
            **kwargs: Additional API parameters

        Returns:
            Tuple of (response_text, cache_info)
        """
        if enable_cache:
            system = [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }]
        else:
            system = system_prompt

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                **kwargs
            )

            cache_info = self._extract_cache_info(response)
            cache_hit = cache_info.get("cache_read_input_tokens", 0) > 0
            self.stats.update(hit=cache_hit, tokens=cache_info.get("cache_read_input_tokens", 0))

            return response.content[0].text, cache_info

        except Exception as e:
            self.stats.update(hit=False)
            raise

    def _build_skill_manifest(self, deferred_skills: List[Dict]) -> str:
        """Build lightweight skill manifest for context"""
        lines = [
            "## Available On-Demand Skills",
            "",
            "Request these skills when needed:",
            ""
        ]

        for skill in deferred_skills:
            name = skill.get('name', skill.get('path', '').split('/')[-1])
            description = skill.get('description', 'No description')
            triggers = ', '.join(skill.get('triggers', []))
            lines.append(f"- **{name}**: {description}")
            if triggers:
                lines.append(f"  Keywords: {triggers}")

        return "\n".join(lines)

    def _extract_cache_info(self, response) -> Dict:
        """Extract cache information from API response"""
        cache_info = {
            "input_tokens": getattr(response.usage, 'input_tokens', 0),
            "output_tokens": getattr(response.usage, 'output_tokens', 0),
            "cache_creation_input_tokens": getattr(response.usage, 'cache_creation_input_tokens', 0),
            "cache_read_input_tokens": getattr(response.usage, 'cache_read_input_tokens', 0),
        }

        # Calculate effective cost
        total_input = cache_info["input_tokens"]
        cached = cache_info["cache_read_input_tokens"]
        if total_input > 0:
            cache_info["cache_hit_rate"] = cached / total_input
        else:
            cache_info["cache_hit_rate"] = 0

        return cache_info

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return self.stats.to_dict()

    def reset_stats(self):
        """Reset cache statistics"""
        self.stats = CacheStats()


class PromptCacheManager:
    """
    High-level manager for multi-agent prompt caching.

    Handles:
    - Loading agent configurations from composed files
    - Managing prompt cache across multiple agents
    - Loading deferred skills on demand
    """

    def __init__(self, project_dir: str, api_key: Optional[str] = None):
        self.project_dir = Path(project_dir)
        self.client = CachedAnthropicClient(api_key)
        self._loaded_skills: Dict[str, str] = {}  # Cache of loaded deferred skills

    def load_agent_from_composed(
        self,
        agent_name: str,
        composed_dir: str = ".ai-agents/composed"
    ) -> AgentPromptConfig:
        """
        Load agent configuration from composed files.

        Args:
            agent_name: Name of the agent
            composed_dir: Directory with composed agent files

        Returns:
            AgentPromptConfig ready for caching
        """
        composed_path = self.project_dir / composed_dir

        # Load main prompt
        prompt_file = composed_path / f"{agent_name}.md"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Composed agent not found: {prompt_file}")

        with open(prompt_file, 'r') as f:
            prompt_content = f.read()

        # Load deferred skills manifest if exists
        manifest_file = composed_path / f"{agent_name}-deferred-skills.json"
        deferred_skills = []
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                deferred_skills = manifest.get('deferred_skills', [])

        # Create config
        config = AgentPromptConfig(
            agent_id=agent_name,
            stable_system_prompt=prompt_content,
            deferred_skills=deferred_skills
        )

        # Register with client
        self.client.register_agent(config)

        return config

    def load_deferred_skill(self, agent_name: str, skill_name: str) -> Optional[str]:
        """
        Load a deferred skill into context.

        Args:
            agent_name: Agent requesting the skill
            skill_name: Name or path of the skill

        Returns:
            Skill content or None if not found
        """
        cache_key = f"{agent_name}:{skill_name}"

        # Check cache
        if cache_key in self._loaded_skills:
            return self._loaded_skills[cache_key]

        # Find skill in manifest
        if agent_name not in self.client._prompt_configs:
            return None

        config = self.client._prompt_configs[agent_name]

        for skill in config.deferred_skills:
            if skill.get('name') == skill_name or skill.get('path', '').endswith(skill_name):
                skill_path = skill.get('path', '')

                # Try to load from skills directory
                full_path = self.project_dir / "skills" / f"{skill_path}.md"
                if not full_path.exists():
                    full_path = self.project_dir / ".ai-agents" / "skills" / f"{skill_path}.md"

                if full_path.exists():
                    with open(full_path, 'r') as f:
                        content = f.read()
                    self._loaded_skills[cache_key] = content
                    return content

        return None

    def call_agent(
        self,
        agent_name: str,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        include_skills: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[str, Dict]:
        """
        Call an agent with prompt caching.

        Args:
            agent_name: Name of registered agent
            prompt: User prompt
            conversation_history: Previous messages
            include_skills: Deferred skills to include in this call
            **kwargs: Additional API parameters

        Returns:
            Tuple of (response_text, cache_info)
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": prompt})

        # Build dynamic context with requested skills
        dynamic_parts = []
        if include_skills:
            for skill_name in include_skills:
                skill_content = self.load_deferred_skill(agent_name, skill_name)
                if skill_content:
                    dynamic_parts.append(f"## Loaded Skill: {skill_name}\n\n{skill_content}")

        dynamic_context = "\n\n".join(dynamic_parts) if dynamic_parts else None

        return self.client.call_with_cache(
            agent_id=agent_name,
            messages=messages,
            dynamic_context=dynamic_context,
            **kwargs
        )

    def get_cache_stats(self) -> Dict:
        """Get overall cache statistics"""
        return self.client.get_stats()


# Convenience function for simple caching
def create_cached_client(api_key: Optional[str] = None) -> CachedAnthropicClient:
    """Create a cached Anthropic client"""
    return CachedAnthropicClient(api_key)


if __name__ == "__main__":
    # Demo usage
    print("Prompt Cache Utility")
    print("=" * 50)
    print()
    print("Usage:")
    print("  from prompt_cache import CachedAnthropicClient, PromptCacheManager")
    print()
    print("Simple caching:")
    print('  client = CachedAnthropicClient()')
    print('  response, info = client.call_simple(system_prompt, messages)')
    print()
    print("Multi-agent caching:")
    print('  manager = PromptCacheManager("/path/to/project")')
    print('  manager.load_agent_from_composed("frontend_developer")')
    print('  response, info = manager.call_agent("frontend_developer", "Build a form")')
    print()
    print("Cache statistics:")
    print('  stats = manager.get_cache_stats()')
    print('  print(f"Hit rate: {stats[\'hit_rate\']}, Tokens saved: {stats[\'tokens_saved\']}")')
