#!/usr/bin/env python3
"""
Pytest configuration and fixtures for AI Agents tests
"""

import sys
from pathlib import Path

import pytest

# Add project directories to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "scripts" / "orchestration"))


@pytest.fixture
def project_root_path():
    """Return the project root path"""
    return project_root


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing"""
    return {
        "agent_id": "test-dev-001",
        "version": "1.0.0",
        "type": "developer",
        "base": "base/software-developer.md",
        "skills": {
            "always_loaded": ["core/web-artifacts-builder"],
            "deferred": [
                {
                    "path": "documents/pdf",
                    "description": "Generate PDF documents",
                    "triggers": ["pdf", "report", "document"]
                },
                {
                    "path": "design/theme-factory",
                    "description": "Create UI themes",
                    "triggers": ["theme", "dark mode", "styling"]
                }
            ]
        },
        "cache_control": {
            "enabled": True,
            "stable_context": ["base/software-developer.md"],
            "dynamic_context": [".ai-agents/context/current-task.md"],
            "cache_ttl_seconds": 300
        }
    }


@pytest.fixture
def sample_project_config():
    """Sample project configuration for testing"""
    return {
        "project_name": "Test Project",
        "description": "A test project for unit tests",
        "agent_library": {
            "version": "2.0.0"
        },
        "project": {
            "tech_stack": {
                "frontend": ["React", "TypeScript"],
                "backend": ["Node.js", "Express"]
            }
        }
    }


@pytest.fixture
def mock_library_structure(tmp_path):
    """Create a mock library structure for testing"""
    library_path = tmp_path / "library"

    # Create directories
    (library_path / "base").mkdir(parents=True)
    (library_path / "platforms" / "web").mkdir(parents=True)
    (library_path / "skills" / "core").mkdir(parents=True)
    (library_path / "skills" / "documents").mkdir(parents=True)
    (library_path / "skills" / "design").mkdir(parents=True)
    (library_path / "tools").mkdir(parents=True)

    # Create mock files
    files = {
        "base/software-developer.md": "# Software Developer\nYou are a software developer.",
        "base/manager.md": "# Manager\nYou are a team manager.",
        "platforms/web/frontend-developer.md": "# Frontend\nFrontend development skills.",
        "skills/core/web-artifacts-builder.md": "# Web Artifacts\nBuild web components and artifacts.",
        "skills/core/webapp-testing.md": "# Testing\nTest web applications.",
        "skills/documents/pdf.md": "# PDF\nGenerate PDF documents.",
        "skills/design/theme-factory.md": "# Themes\nCreate UI themes.",
    }

    for path, content in files.items():
        file_path = library_path / path
        file_path.write_text(content)

    return library_path


@pytest.fixture
def mock_project_structure(tmp_path):
    """Create a mock project structure for testing"""
    project_path = tmp_path / "project"

    # Create directories
    (project_path / ".ai-agents" / "context").mkdir(parents=True)
    (project_path / ".ai-agents" / "composed").mkdir(parents=True)

    # Create mock context files
    files = {
        ".ai-agents/context/architecture.md": "# Architecture\nProject architecture docs.",
        ".ai-agents/context/current-task.md": "# Current Task\nWorking on feature X.",
    }

    for path, content in files.items():
        file_path = project_path / path
        file_path.write_text(content)

    return project_path
