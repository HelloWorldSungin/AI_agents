#!/usr/bin/env python3
"""
Test suite for JSON extraction in the Initializer Agent.

Tests the 3-strategy JSON extraction system:
1. Code Block Extraction
2. Smart JSON Object Detection
3. Fallback Raw JSON
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.autonomous.initializer import ProjectInitializer, InitializerConfig


def create_test_initializer():
    """Create a minimal initializer for testing."""
    # Create config that doesn't require external services
    config = InitializerConfig(
        backend="claude-code",
        state_provider_config={"type": "file", "file_path": "/tmp/test_tasks.json"}
    )
    # We only need the _extract_json method, so we'll test it directly
    return config


def test_json_in_json_code_block():
    """Test extraction from ```json code blocks."""
    text = '''Here's the task breakdown:

```json
{
  "project_summary": "Test project",
  "tasks": [
    {
      "id": "task-1",
      "title": "First task",
      "description": "Do something"
    }
  ]
}
```

Let me know if you need changes.'''

    # Create a mock initializer to test the method
    from scripts.autonomous.initializer import ProjectInitializer

    # Use a simple class to test just the extraction method
    class TestExtractor:
        def _extract_json(self, text):
            return ProjectInitializer._extract_json(self, text)

        def _extend_to_matching_brace(self, text, start):
            return ProjectInitializer._extend_to_matching_brace(self, text, start)

    extractor = TestExtractor()
    result = extractor._extract_json(text)

    assert result is not None, "Should extract JSON from ```json block"
    import json
    parsed = json.loads(result)
    assert "tasks" in parsed, "Should have tasks key"
    assert len(parsed["tasks"]) == 1, "Should have 1 task"
    print("✅ Test 1 PASSED: JSON in ```json code blocks")


def test_json_in_plain_code_block():
    """Test extraction from ``` code blocks (no language label)."""
    text = '''Analysis complete:

```
{
  "project_summary": "Another test",
  "tasks": [
    {
      "id": "task-1",
      "title": "Setup environment",
      "description": "Configure dev environment"
    },
    {
      "id": "task-2",
      "title": "Implement feature",
      "description": "Build the main feature"
    }
  ]
}
```

Done!'''

    class TestExtractor:
        def _extract_json(self, text):
            return ProjectInitializer._extract_json(self, text)

        def _extend_to_matching_brace(self, text, start):
            return ProjectInitializer._extend_to_matching_brace(self, text, start)

    extractor = TestExtractor()
    result = extractor._extract_json(text)

    assert result is not None, "Should extract JSON from ``` block"
    import json
    parsed = json.loads(result)
    assert "tasks" in parsed, "Should have tasks key"
    assert len(parsed["tasks"]) == 2, "Should have 2 tasks"
    print("✅ Test 2 PASSED: JSON in ``` code blocks (no language label)")


def test_raw_json_without_code_blocks():
    """Test extraction of raw JSON without code blocks."""
    text = '''I've analyzed the requirements. Here's the breakdown:

{
  "project_summary": "Raw JSON test",
  "total_estimated_tasks": 3,
  "tasks": [
    {
      "id": "task-1",
      "title": "Database setup",
      "description": "Create database schema"
    },
    {
      "id": "task-2",
      "title": "API endpoints",
      "description": "Build REST API"
    },
    {
      "id": "task-3",
      "title": "Frontend",
      "description": "Build UI"
    }
  ]
}

Let me know if you want me to adjust priorities.'''

    class TestExtractor:
        def _extract_json(self, text):
            return ProjectInitializer._extract_json(self, text)

        def _extend_to_matching_brace(self, text, start):
            return ProjectInitializer._extend_to_matching_brace(self, text, start)

    extractor = TestExtractor()
    result = extractor._extract_json(text)

    assert result is not None, "Should extract raw JSON"
    import json
    parsed = json.loads(result)
    assert "tasks" in parsed, "Should have tasks key"
    assert len(parsed["tasks"]) == 3, "Should have 3 tasks"
    print("✅ Test 3 PASSED: Raw JSON without code blocks")


def test_json_with_markdown_around():
    """Test extraction with lots of markdown before/after."""
    text = '''# Project Analysis

## Overview
This is a complex project with multiple components.

### Key Features
- Feature A
- Feature B
- Feature C

## Task Breakdown

Based on my analysis, here are the recommended tasks:

```json
{
  "project_summary": "Complex project with markdown",
  "tasks": [
    {
      "id": "task-1",
      "title": "Initialize project structure",
      "description": "Set up directories and config files",
      "priority": 1,
      "category": "infrastructure",
      "acceptance_criteria": ["Directory structure exists", "Config files created"],
      "test_steps": ["Run tree command", "Verify config loads"]
    }
  ]
}
```

## Next Steps

1. Review the tasks above
2. Approve or request changes
3. Begin implementation

---

*Generated by AI Assistant*'''

    class TestExtractor:
        def _extract_json(self, text):
            return ProjectInitializer._extract_json(self, text)

        def _extend_to_matching_brace(self, text, start):
            return ProjectInitializer._extend_to_matching_brace(self, text, start)

    extractor = TestExtractor()
    result = extractor._extract_json(text)

    assert result is not None, "Should extract JSON from markdown-heavy text"
    import json
    parsed = json.loads(result)
    assert "tasks" in parsed, "Should have tasks key"
    assert len(parsed["tasks"]) == 1, "Should have 1 task"
    assert "acceptance_criteria" in parsed["tasks"][0], "Should have acceptance_criteria"
    print("✅ Test 4 PASSED: JSON with markdown before/after")


def run_all_tests():
    """Run all test cases."""
    print("=" * 50)
    print("JSON Extraction Test Suite")
    print("=" * 50)
    print()

    tests = [
        test_json_in_json_code_block,
        test_json_in_plain_code_block,
        test_raw_json_without_code_blocks,
        test_json_with_markdown_around,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
