#!/usr/bin/env python3
"""
Tests for compose-agent.py

Tests the advanced tool use features:
- Deferred skill loading
- Skills parsing (legacy and new formats)
- Skill search manifest generation
- Token budget analysis

Run with:
  python -m pytest tests/test_compose_agent.py -v
  OR
  python tests/test_compose_agent.py
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Try to import pytest, fall back to unittest
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Create dummy pytest fixtures decorator
    class pytest:
        @staticmethod
        def fixture(func):
            return func

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from compose_agent import AgentComposer


class TestSkillsParsing:
    """Test skills configuration parsing"""

    @pytest.fixture
    def composer(self, tmp_path):
        """Create a composer instance with temp directories"""
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"
        library_path.mkdir()
        project_path.mkdir()

        # Create skills directory
        (library_path / "skills" / "core").mkdir(parents=True)
        (library_path / "skills" / "design").mkdir(parents=True)

        return AgentComposer(library_path, project_path)

    def test_parse_legacy_format(self, composer):
        """Test parsing legacy array format"""
        skills_config = [
            "core/web-artifacts-builder",
            "core/webapp-testing",
            "design/theme-factory"
        ]

        result = composer.parse_skills_config(skills_config)

        assert result['always_loaded'] == skills_config
        assert result['deferred'] == []

    def test_parse_new_format_simple(self, composer):
        """Test parsing new object format with simple deferred skills"""
        skills_config = {
            "always_loaded": ["core/web-artifacts-builder"],
            "deferred": ["documents/pdf", "documents/xlsx"]
        }

        result = composer.parse_skills_config(skills_config)

        assert result['always_loaded'] == ["core/web-artifacts-builder"]
        assert result['deferred'] == ["documents/pdf", "documents/xlsx"]

    def test_parse_new_format_detailed_deferred(self, composer):
        """Test parsing new format with detailed deferred skill objects"""
        skills_config = {
            "always_loaded": ["core/web-artifacts-builder"],
            "deferred": [
                {
                    "path": "design/theme-factory",
                    "description": "Create UI themes",
                    "triggers": ["theme", "dark mode", "styling"]
                },
                "documents/pdf"  # Mixed: object and string
            ]
        }

        result = composer.parse_skills_config(skills_config)

        assert len(result['deferred']) == 2
        assert result['deferred'][0]['path'] == "design/theme-factory"
        assert result['deferred'][1] == "documents/pdf"

    def test_parse_none_config(self, composer):
        """Test parsing None config returns empty lists"""
        result = composer.parse_skills_config(None)

        assert result['always_loaded'] == []
        assert result['deferred'] == []

    def test_parse_empty_arrays(self, composer):
        """Test parsing empty arrays"""
        skills_config = {
            "always_loaded": [],
            "deferred": []
        }

        result = composer.parse_skills_config(skills_config)

        assert result['always_loaded'] == []
        assert result['deferred'] == []


class TestDeferredSkillParsing:
    """Test deferred skill entry parsing"""

    @pytest.fixture
    def composer(self, tmp_path):
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"
        library_path.mkdir()
        project_path.mkdir()
        return AgentComposer(library_path, project_path)

    def test_parse_string_skill(self, composer):
        """Test parsing simple string skill reference"""
        result = composer.parse_deferred_skill("documents/pdf")

        assert result['path'] == "documents/pdf"
        assert result['description'] == "Skill: pdf"
        assert result['triggers'] == []

    def test_parse_object_skill_full(self, composer):
        """Test parsing object skill with all fields"""
        skill = {
            "path": "design/theme-factory",
            "description": "Create professional UI themes",
            "triggers": ["theme", "dark mode", "colors"]
        }

        result = composer.parse_deferred_skill(skill)

        assert result['path'] == "design/theme-factory"
        assert result['description'] == "Create professional UI themes"
        assert result['triggers'] == ["theme", "dark mode", "colors"]

    def test_parse_object_skill_minimal(self, composer):
        """Test parsing object skill with only path"""
        skill = {"path": "core/webapp-testing"}

        result = composer.parse_deferred_skill(skill)

        assert result['path'] == "core/webapp-testing"
        assert result['description'] == "Skill: webapp-testing"
        assert result['triggers'] == []


class TestSkillSearchManifest:
    """Test skill search manifest generation"""

    @pytest.fixture
    def composer(self, tmp_path):
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"
        library_path.mkdir()
        project_path.mkdir()
        return AgentComposer(library_path, project_path)

    def test_generate_manifest_empty(self, composer):
        """Test generating manifest with no deferred skills"""
        result = composer.generate_skill_search_manifest([])

        assert result == ""
        assert composer.deferred_skills_manifest == []

    def test_generate_manifest_single_skill(self, composer):
        """Test generating manifest with one skill"""
        deferred = [
            {
                "path": "documents/pdf",
                "description": "Generate PDF reports",
                "triggers": ["pdf", "report"]
            }
        ]

        result = composer.generate_skill_search_manifest(deferred)

        assert "Available On-Demand Skills" in result
        assert "pdf" in result
        assert "Generate PDF reports" in result
        assert "pdf, report" in result  # Triggers joined
        assert len(composer.deferred_skills_manifest) == 1

    def test_generate_manifest_multiple_skills(self, composer):
        """Test generating manifest with multiple skills"""
        deferred = [
            {"path": "documents/pdf", "description": "PDF generation", "triggers": ["pdf"]},
            {"path": "documents/xlsx", "description": "Excel files", "triggers": ["excel", "spreadsheet"]},
            "design/theme-factory"  # String format
        ]

        result = composer.generate_skill_search_manifest(deferred)

        assert "pdf" in result
        assert "xlsx" in result
        assert "theme-factory" in result
        assert len(composer.deferred_skills_manifest) == 3

    def test_manifest_includes_instructions(self, composer):
        """Test manifest includes user instructions"""
        deferred = [{"path": "test/skill", "description": "Test", "triggers": []}]

        result = composer.generate_skill_search_manifest(deferred)

        assert "Request a skill by saying" in result
        assert "not loaded by default" in result


class TestTokenBudgetAnalysis:
    """Test token budget analysis"""

    @pytest.fixture
    def composer(self, tmp_path):
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"
        library_path.mkdir()
        project_path.mkdir()
        return AgentComposer(library_path, project_path)

    def test_count_tokens(self, composer):
        """Test basic token counting"""
        # Approximately 4 characters per token
        text = "a" * 4000  # Should be ~1000 tokens

        result = composer.count_tokens(text)

        assert result == 1000

    def test_analyze_within_budget(self, composer):
        """Test analysis for content within budget"""
        content = "a" * 20000  # ~5000 tokens, well within 12000 limit

        result = composer.analyze_token_budget(content, "test_agent", {})

        assert result['total_tokens'] == 5000
        assert result['within_budget'] is True
        assert result['needs_warning'] is False

    def test_analyze_exceeds_budget(self, composer):
        """Test analysis for content exceeding budget"""
        content = "a" * 60000  # ~15000 tokens, over 12000 limit

        result = composer.analyze_token_budget(content, "test_agent", {})

        assert result['total_tokens'] == 15000
        assert result['within_budget'] is False

    def test_analyze_warning_threshold(self, composer):
        """Test analysis triggers warning near threshold"""
        # Warning at 75% of 12000 = 9000 tokens
        content = "a" * 40000  # ~10000 tokens, above warning

        result = composer.analyze_token_budget(content, "test_agent", {})

        assert result['needs_warning'] is True


class TestComposition:
    """Test full agent composition"""

    @pytest.fixture
    def setup_library(self, tmp_path):
        """Set up a mock library structure"""
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"

        # Create directory structure
        (library_path / "base").mkdir(parents=True)
        (library_path / "skills" / "core").mkdir(parents=True)
        (library_path / "skills" / "documents").mkdir(parents=True)
        (project_path / ".ai-agents" / "context").mkdir(parents=True)

        # Create mock files
        (library_path / "base" / "software-developer.md").write_text(
            "# Base Software Developer\n\nYou are a software developer."
        )
        (library_path / "skills" / "core" / "web-artifacts-builder.md").write_text(
            "# Web Artifacts Builder\n\nBuild web components."
        )
        (library_path / "skills" / "documents" / "pdf.md").write_text(
            "# PDF Generation\n\nGenerate PDF documents."
        )

        return library_path, project_path

    def test_compose_with_legacy_skills(self, setup_library):
        """Test composition with legacy skills format"""
        library_path, project_path = setup_library

        composer = AgentComposer(library_path, project_path)

        agent_config = {
            "base": "base/software-developer.md",
            "skills": ["core/web-artifacts-builder"]
        }

        project_config = {
            "project_name": "Test Project",
            "agent_library": {"version": "2.0.0"}
        }

        result = composer.compose_agent("test_agent", agent_config, project_config)

        assert "Base Software Developer" in result
        assert "Web Artifacts Builder" in result
        assert "ANTHROPIC SKILLS (Always Loaded)" in result

    def test_compose_with_deferred_skills(self, setup_library):
        """Test composition with deferred loading format"""
        library_path, project_path = setup_library

        composer = AgentComposer(library_path, project_path)

        agent_config = {
            "base": "base/software-developer.md",
            "skills": {
                "always_loaded": ["core/web-artifacts-builder"],
                "deferred": [
                    {
                        "path": "documents/pdf",
                        "description": "Generate PDF documents",
                        "triggers": ["pdf", "report"]
                    }
                ]
            }
        }

        project_config = {
            "project_name": "Test Project",
            "agent_library": {"version": "2.0.0"}
        }

        result = composer.compose_agent("test_agent", agent_config, project_config)

        # Always loaded skill should be in content
        assert "Web Artifacts Builder" in result

        # Deferred skill should NOT be in content (only manifest)
        assert "PDF Generation" not in result  # Full content not loaded
        assert "ON-DEMAND SKILLS" in result
        assert "documents/pdf" in result or "pdf" in result

    def test_compose_manifest_saved(self, setup_library, tmp_path):
        """Test that deferred skills manifest is saved"""
        library_path, project_path = setup_library

        composer = AgentComposer(library_path, project_path)

        agent_config = {
            "base": "base/software-developer.md",
            "skills": {
                "always_loaded": ["core/web-artifacts-builder"],
                "deferred": [
                    {"path": "documents/pdf", "description": "PDF gen", "triggers": ["pdf"]}
                ]
            }
        }

        project_config = {
            "project_name": "Test Project",
            "agent_library": {"version": "2.0.0"}
        }

        content = composer.compose_agent("test_agent", agent_config, project_config)

        # Save the agent
        output_dir = tmp_path / "output"
        composer.save_agent("test_agent", content, output_dir, agent_config)

        # Check manifest file was created
        manifest_file = output_dir / "test_agent-deferred-skills.json"
        assert manifest_file.exists()

        with open(manifest_file) as f:
            manifest = json.load(f)

        assert manifest['agent'] == "test_agent"
        assert len(manifest['deferred_skills']) == 1
        assert manifest['deferred_skills'][0]['name'] == "pdf"


class TestBackwardCompatibility:
    """Test backward compatibility with existing configurations"""

    @pytest.fixture
    def composer(self, tmp_path):
        library_path = tmp_path / "library"
        project_path = tmp_path / "project"
        library_path.mkdir()
        project_path.mkdir()
        return AgentComposer(library_path, project_path)

    def test_legacy_array_still_works(self, composer):
        """Ensure legacy array format still works"""
        # This is how existing configs define skills
        legacy_config = ["skill1", "skill2", "skill3"]

        result = composer.parse_skills_config(legacy_config)

        # All skills should be in always_loaded
        assert result['always_loaded'] == legacy_config
        assert result['deferred'] == []

    def test_mixed_format_in_deferred(self, composer):
        """Test mixing string and object formats in deferred"""
        config = {
            "always_loaded": ["primary/skill"],
            "deferred": [
                "simple/string/skill",  # String format
                {"path": "detailed/skill", "description": "Detailed", "triggers": ["a"]}
            ]
        }

        result = composer.parse_skills_config(config)

        assert len(result['deferred']) == 2

        # Both should be parseable
        parsed1 = composer.parse_deferred_skill(result['deferred'][0])
        parsed2 = composer.parse_deferred_skill(result['deferred'][1])

        assert parsed1['path'] == "simple/string/skill"
        assert parsed2['path'] == "detailed/skill"


class UnittestRunner(unittest.TestCase):
    """Unittest-compatible test runner for when pytest is not available"""

    def setUp(self):
        """Set up test fixtures"""
        self.tmp_dir = tempfile.mkdtemp()
        self.library_path = Path(self.tmp_dir) / "library"
        self.project_path = Path(self.tmp_dir) / "project"

        self.library_path.mkdir()
        self.project_path.mkdir()

        # Create skills directories
        (self.library_path / "skills" / "core").mkdir(parents=True)
        (self.library_path / "skills" / "documents").mkdir(parents=True)
        (self.library_path / "skills" / "design").mkdir(parents=True)
        (self.library_path / "base").mkdir(parents=True)

        # Create mock skill files
        (self.library_path / "base" / "software-developer.md").write_text(
            "# Software Developer\n\nYou are a software developer."
        )
        (self.library_path / "skills" / "core" / "web-artifacts-builder.md").write_text(
            "# Web Artifacts\n\nBuild web components."
        )
        (self.library_path / "skills" / "documents" / "pdf.md").write_text(
            "# PDF\n\nGenerate PDFs."
        )

        self.composer = AgentComposer(self.library_path, self.project_path)

    def tearDown(self):
        """Clean up temp directory"""
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_parse_legacy_format(self):
        """Test parsing legacy array format"""
        skills_config = ["core/web-artifacts-builder", "documents/pdf"]
        result = self.composer.parse_skills_config(skills_config)
        self.assertEqual(result['always_loaded'], skills_config)
        self.assertEqual(result['deferred'], [])

    def test_parse_new_format(self):
        """Test parsing new object format"""
        skills_config = {
            "always_loaded": ["core/web-artifacts-builder"],
            "deferred": ["documents/pdf"]
        }
        result = self.composer.parse_skills_config(skills_config)
        self.assertEqual(result['always_loaded'], ["core/web-artifacts-builder"])
        self.assertEqual(result['deferred'], ["documents/pdf"])

    def test_parse_deferred_string(self):
        """Test parsing string deferred skill"""
        result = self.composer.parse_deferred_skill("documents/pdf")
        self.assertEqual(result['path'], "documents/pdf")
        self.assertEqual(result['triggers'], [])

    def test_parse_deferred_object(self):
        """Test parsing object deferred skill"""
        skill = {
            "path": "documents/pdf",
            "description": "Generate PDFs",
            "triggers": ["pdf", "report"]
        }
        result = self.composer.parse_deferred_skill(skill)
        self.assertEqual(result['path'], "documents/pdf")
        self.assertEqual(result['description'], "Generate PDFs")
        self.assertEqual(result['triggers'], ["pdf", "report"])

    def test_generate_manifest(self):
        """Test manifest generation"""
        deferred = [{"path": "documents/pdf", "description": "PDF gen", "triggers": ["pdf"]}]
        result = self.composer.generate_skill_search_manifest(deferred)
        self.assertIn("Available On-Demand Skills", result)
        self.assertIn("pdf", result)

    def test_count_tokens(self):
        """Test token counting"""
        text = "a" * 4000  # ~1000 tokens
        result = self.composer.count_tokens(text)
        self.assertEqual(result, 1000)

    def test_analyze_token_budget(self):
        """Test token budget analysis"""
        content = "a" * 20000  # ~5000 tokens
        result = self.composer.analyze_token_budget(content, "test", {})
        self.assertEqual(result['total_tokens'], 5000)
        self.assertTrue(result['within_budget'])


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        print("Running tests with unittest (pytest not available)")
        print("=" * 60)
        unittest.main(verbosity=2)
