# Generic AppFlowy Sync - Complete Guide

This guide explains how to use the generic `sync_project.py` script to sync ANY project's documentation to AppFlowy.

## What is Generic Sync?

`sync_project.py` is a universal, configuration-driven script that can sync documentation from any repository to AppFlowy. Unlike project-specific scripts, it works through configuration files rather than hardcoded paths.

## Key Features

- **Configuration-driven**: Define your document structure in YAML or JSON
- **Auto-discovery mode**: Automatically find and sync documentation files
- **Glob pattern support**: Use wildcards to match multiple files (e.g., `docs/**/*.md`)
- **Hierarchical structure**: Create nested folder organization in AppFlowy
- **Incremental sync**: Only syncs changed files (MD5 hash tracking)
- **Flexible naming**: Auto-generate or specify custom page names
- **Multiple input modes**: Config file, auto-discover, or specific folder sync
- **Dry-run support**: Preview changes before syncing
- **Force mode**: Re-sync everything, ignoring cache
- **Portable**: Works with any Git repository or project

## Quick Start

### 1. Copy the Example Configuration

```bash
cd /path/to/your/project
cp /path/to/appflowy-sync.example.yaml appflowy-sync.yaml
```

### 2. Edit Configuration for Your Project

```yaml
# appflowy-sync.yaml
parent_page: "My Project Documentation"

structure:
  - folder: "Getting Started"
    documents:
      - source: "README.md"
        name: "Overview"
      - source: "docs/quickstart.md"
        name: "Quick Start"

  - folder: "User Guide"
    documents:
      - source: "docs/guide/**/*.md"  # Glob pattern

  - folder: "API Reference"
    documents:
      - source: "docs/api/*.md"
```

### 3. Set Environment Variables

```bash
export APPFLOWY_API_URL="https://appflowy.ark-node.com"
export APPFLOWY_API_TOKEN="your_jwt_token"
export APPFLOWY_WORKSPACE_ID="your_workspace_id"
```

Or use a `.env` file:

```bash
# .env
APPFLOWY_API_URL=https://appflowy.ark-node.com
APPFLOWY_API_TOKEN=your_jwt_token
APPFLOWY_WORKSPACE_ID=your_workspace_id
```

### 4. Run the Sync

```bash
# Dry run to preview
python sync_project.py --config appflowy-sync.yaml --dry-run

# Sync for real
python sync_project.py --config appflowy-sync.yaml

# Force re-sync everything
python sync_project.py --config appflowy-sync.yaml --force
```

## Configuration Guide

### Basic Configuration Structure

```yaml
# Parent page name (will be created if doesn't exist)
parent_page: "Documentation"

# Document structure (folders and files)
structure:
  - folder: "Folder Name"
    documents:
      - source: "path/to/file.md"
        name: "Custom Page Name"
```

### Document Properties

Each document can have:

- **`source`** (required): Relative path to markdown file
  - Examples: `"README.md"`, `"docs/api.md"`, `"docs/**/*.md"`
  - Supports glob patterns: `*`, `**`, `?`, `[abc]`, `[!abc]`

- **`name`** (optional): Custom page name in AppFlowy
  - If not specified, uses file stem (filename without extension)
  - Example: `"API Reference"` instead of `"api-reference"`

- **`name_from_path`** (optional): Boolean flag to use parent folder name
  - Useful for organizing example projects
  - Example: `examples/web-app/README.md` → "Web App"

### Glob Pattern Examples

```yaml
structure:
  - folder: "All Docs"
    documents:
      # Single file
      - source: "README.md"

      # All .md files in docs/
      - source: "docs/*.md"

      # All .md files recursively
      - source: "docs/**/*.md"

      # README.md in each example subfolder
      - source: "examples/*/README.md"
        name_from_path: true

      # Specific pattern
      - source: "tutorials/[0-9][0-9]-*.md"
```

### Advanced Configuration Examples

#### Multi-Language Documentation

```yaml
parent_page: "Documentation"
structure:
  - folder: "English"
    documents:
      - source: "docs/en/**/*.md"
  - folder: "日本語"
    documents:
      - source: "docs/ja/**/*.md"
  - folder: "Español"
    documents:
      - source: "docs/es/**/*.md"
```

#### Version-Based Organization

```yaml
parent_page: "Product Docs"
structure:
  - folder: "Version 2.0"
    documents:
      - source: "docs/v2.0/**/*.md"
  - folder: "Version 1.0"
    documents:
      - source: "docs/v1.0/**/*.md"
```

#### Public vs Internal Docs

```yaml
parent_page: "All Documentation"
structure:
  - folder: "Public Documentation"
    documents:
      - source: "docs/public/**/*.md"
  - folder: "Internal Documentation"
    documents:
      - source: "docs/internal/**/*.md"
```

## Usage Modes

### Mode 1: Configuration File (Recommended)

```bash
# Create config file
cat > appflowy-sync.yaml <<EOF
parent_page: "Documentation"
structure:
  - folder: "Getting Started"
    documents:
      - source: "README.md"
EOF

# Sync
python sync_project.py --config appflowy-sync.yaml
```

**Benefits:**
- Full control over structure
- Version controlled configuration
- Repeatable syncs
- Team collaboration

### Mode 2: Auto-Discovery

```bash
# Auto-discover and sync all documentation
python sync_project.py --auto-discover --parent "Documentation"
```

**How it works:**
- Automatically finds common documentation patterns:
  - `README.md`
  - `docs/**/*.md`
  - `documentation/**/*.md`
  - `guides/**/*.md`
  - `examples/**/README.md`
- Creates folder structure based on directory names
- Useful for quick syncs without configuration

### Mode 3: Specific Folder

```bash
# Sync only the docs/ folder
python sync_project.py --source docs/ --parent "API Docs"
```

**Use cases:**
- Syncing a specific documentation folder
- Testing before full sync
- Partial updates

## Command-Line Options

```bash
python sync_project.py [options]

Required (choose one):
  --config FILE          Path to config file (YAML or JSON)
  --auto-discover        Auto-discover documentation files
  --source FOLDER        Sync specific folder

Options:
  --parent NAME          Parent page name (for auto-discover/source modes)
  --project-root DIR     Project root directory (default: current directory)
  --sync-status FILE     Path to sync status file (default: .appflowy-sync-status.json)
  --env-file FILE        Path to .env file
  --dry-run              Preview changes without syncing
  --force                Force re-sync all files (ignore cache)
  -h, --help             Show help message
```

## Incremental Sync

The script tracks which files have been synced using MD5 hash comparison:

- **First sync**: All files are synced
- **Subsequent syncs**: Only changed files are synced
- **Status tracking**: Stored in `.appflowy-sync-status.json`

### Sync Status File

```json
{
  "last_sync": "2025-12-08T10:30:00Z",
  "parent_page_id": "page-id-here",
  "folder_ids": {
    "Getting Started": "folder-id-1",
    "API Reference": "folder-id-2"
  },
  "synced_files": {
    "README.md": {
      "hash": "abc123...",
      "page_id": "page-id-here",
      "page_name": "Overview",
      "folder_name": "Getting Started",
      "last_sync": "2025-12-08T10:30:00Z"
    }
  }
}
```

### Force Re-sync

To force re-sync all files (ignore cache):

```bash
python sync_project.py --config appflowy-sync.yaml --force
```

Or delete the status file:

```bash
rm .appflowy-sync-status.json
python sync_project.py --config appflowy-sync.yaml
```

## Integration Examples

### Git Post-Commit Hook

```bash
# .git/hooks/post-commit
#!/bin/bash
python sync_project.py --config appflowy-sync.yaml
```

```bash
chmod +x .git/hooks/post-commit
```

### Cron Job

```bash
# Sync every hour
0 * * * * cd /path/to/project && python sync_project.py --config appflowy-sync.yaml

# Sync every day at 2 AM
0 2 * * * cd /path/to/project && python sync_project.py --config appflowy-sync.yaml
```

### GitHub Actions

```yaml
# .github/workflows/sync-docs.yml
name: Sync Documentation to AppFlowy

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'README.md'
      - 'appflowy-sync.yaml'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install requests pyyaml

      - name: Sync to AppFlowy
        env:
          APPFLOWY_API_URL: ${{ secrets.APPFLOWY_API_URL }}
          APPFLOWY_API_TOKEN: ${{ secrets.APPFLOWY_API_TOKEN }}
          APPFLOWY_WORKSPACE_ID: ${{ secrets.APPFLOWY_WORKSPACE_ID }}
        run: |
          python sync_project.py --config appflowy-sync.yaml
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
sync-docs:
  stage: deploy
  image: python:3.9
  script:
    - pip install requests pyyaml
    - python sync_project.py --config appflowy-sync.yaml
  only:
    refs:
      - main
    changes:
      - docs/**/*
      - README.md
  variables:
    APPFLOWY_API_URL: $APPFLOWY_API_URL
    APPFLOWY_API_TOKEN: $APPFLOWY_API_TOKEN
    APPFLOWY_WORKSPACE_ID: $APPFLOWY_WORKSPACE_ID
```

## Troubleshooting

### Authentication Failed

**Problem:** 401 or 403 errors

**Solutions:**
1. Check token is valid:
   ```bash
   curl "$APPFLOWY_API_URL/api/workspace" \
     -H "Authorization: Bearer $APPFLOWY_API_TOKEN"
   ```
2. Token may have expired - generate new token
3. Check workspace ID is correct

### Files Not Found

**Problem:** "File not found" warnings

**Solutions:**
1. Check file paths are relative to `--project-root`
2. Verify files exist: `ls docs/file.md`
3. Check glob patterns are correct
4. Use `--dry-run` to preview what will be synced

### No Files Synced

**Problem:** All files skipped (0 synced)

**Solutions:**
1. Files may be up to date (use `--force` to re-sync)
2. Check sync status file: `.appflowy-sync-status.json`
3. Verify config file is correct
4. Use `--dry-run` to see what would be synced

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'yaml'`

**Solution:**
```bash
pip install pyyaml requests
```

### Permission Denied

**Problem:** Cannot write to workspace

**Solutions:**
1. Check workspace ID is correct
2. Verify API token has write permissions
3. Check workspace membership

## Dependencies

```bash
pip install requests pyyaml
```

Or using requirements.txt:

```bash
# requirements.txt
requests>=2.28.0
pyyaml>=6.0
```

```bash
pip install -r requirements.txt
```

## Best Practices

### 1. Start with Dry-Run

Always test with `--dry-run` first:

```bash
python sync_project.py --config appflowy-sync.yaml --dry-run
```

### 2. Version Control Your Config

Commit `appflowy-sync.yaml` to Git:

```bash
git add appflowy-sync.yaml
git commit -m "Add AppFlowy sync configuration"
```

### 3. Ignore Sync Status

Add to `.gitignore`:

```
.appflowy-sync-status.json
```

### 4. Use Environment Variables

Never hardcode credentials in config files. Use environment variables or `.env` files.

### 5. Incremental Sync

Let the script track changes - don't use `--force` unless necessary.

### 6. Organize with Folders

Use hierarchical folder structure for better organization:

```yaml
structure:
  - folder: "Getting Started"
    documents: [...]
  - folder: "User Guide"
    documents: [...]
  - folder: "API Reference"
    documents: [...]
```

## Comparison: Generic vs Specific Scripts

| Feature | `sync_project.py` | `sync_docs.py` |
|---------|-------------------|----------------|
| Works with any project | ✅ | ❌ (AI_agents only) |
| Configuration-driven | ✅ | ❌ (hardcoded) |
| Glob pattern support | ✅ | ❌ |
| Auto-discovery mode | ✅ | ❌ |
| Incremental sync | ✅ | ✅ |
| Dry-run support | ✅ | ✅ |
| Force mode | ✅ | ✅ |
| Custom .env file | ✅ | ✅ |
| Portable | ✅ | ❌ |

**Recommendation:** Use `sync_project.py` for all new projects. Use `sync_docs.py` only if you're specifically working with the AI_agents repository.

## Support

For issues or questions:

1. Check this guide
2. Review `appflowy-sync.example.yaml` for examples
3. Run with `--dry-run` to preview changes
4. Examine sync status file: `.appflowy-sync-status.json`
5. See `SKILL.md` for complete documentation
6. Check `workflows/troubleshooting.md` for common issues

## License

This script is part of the AI_agents AppFlowy integration skill.

## Version

**Script Version:** 1.0.0
**Last Updated:** 2025-12-08
