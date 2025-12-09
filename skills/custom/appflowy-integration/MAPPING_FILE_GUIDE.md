# AppFlowy Mapping File Guide

## Overview

The `appflowy-mapping.yaml` file provides explicit mapping between repository files and AppFlowy pages. This prevents duplicate page creation and ensures consistent sync behavior across multiple syncs.

## Purpose

1. **Prevent Duplicate Pages**: By maintaining explicit page IDs, the sync script knows exactly which AppFlowy page corresponds to each repository file
2. **Recovery**: If the `.sync-status.json` file is lost, the mapping file serves as a backup source of page IDs
3. **Documentation**: Provides clear documentation of the workspace structure
4. **Team Collaboration**: Allows team members to understand the AppFlowy workspace organization

## File Location

```
/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/appflowy-mapping.yaml
```

## File Structure

### Workspace Configuration

```yaml
workspace:
  id: "c9674d81-6037-4dc3-9aa6-e2d833162b0f"
  name: "AI Agents"
```

Defines the target AppFlowy workspace.

### Documentation Configuration

```yaml
documentation:
  parent_id: "9a5772b0-005a-4ad7-a4c6-2b4efef21680"
  parent_name: "Documentation"
```

Defines the parent page that contains all documentation folders.

### Folder Mappings

```yaml
folders:
  "Getting Started":
    id: "80dc3152-7eb5-46b3-ac60-3d5922b0203c"
    description: "Introductory documentation and quick start guides"

  "Guides":
    id: "e2028dd9-c91e-4b06-ba0c-879a2d46184c"
    description: "Comprehensive guides for using the AI agents system"
```

Maps folder names to their AppFlowy folder IDs with optional descriptions.

### Page Mappings

```yaml
pages:
  - file: "README.md"
    folder: "Getting Started"
    name: "README"
    page_id: "af403dbc-c7a0-4292-8481-b9dd2e7f0149"
    description: "Main repository README"

  - file: "docs/guides/ARCHITECTURE.md"
    folder: "Guides"
    name: "Architecture"
    page_id: "3472443a-eb72-4039-807f-07cb0fc2211c"
    description: "System architecture documentation"
```

Maps each repository file to its AppFlowy page with:
- `file`: Repository file path (relative to project root)
- `folder`: Target folder name in AppFlowy
- `name`: Display name in AppFlowy
- `page_id`: AppFlowy page view ID
- `description`: Optional description of the page content

## How It Works

### Priority Order

The sync script checks for page IDs in this order:

1. **Mapping file** (`appflowy-mapping.yaml`)
2. **Sync status** (`.sync-status.json`)
3. **Create new page** (if neither has the page ID)

### Sync Behavior

#### With Mapping File

```
1. Load appflowy-mapping.yaml
2. For each file to sync:
   a. Look up page_id in mapping file
   b. If found, update existing page
   c. If not found, check sync status
   d. If still not found, create new page
3. Update sync status with latest sync info
```

#### Without Mapping File

```
1. Skip mapping file
2. For each file to sync:
   a. Check sync status for page_id
   b. If found, update existing page
   c. If not found, create new page
3. Update sync status with latest sync info
```

## Creating a Mapping File

### Method 1: From Existing Sync Status

If you already have a `.sync-status.json` file, you can create the mapping file from it:

```python
import json
import yaml

# Load sync status
with open('.sync-status.json', 'r') as f:
    status = json.load(f)

# Create mapping structure
mapping = {
    'workspace': {
        'id': 'YOUR_WORKSPACE_ID',
        'name': 'YOUR_WORKSPACE_NAME'
    },
    'documentation': {
        'parent_id': status.get('docs_parent_id'),
        'parent_name': 'Documentation'
    },
    'folders': {},
    'pages': []
}

# Add folders
for folder_name, folder_id in status.get('folder_ids', {}).items():
    mapping['folders'][folder_name] = {
        'id': folder_id,
        'description': ''
    }

# Add pages
for file_path, file_info in status.get('synced_files', {}).items():
    mapping['pages'].append({
        'file': file_path,
        'folder': file_info.get('folder_name'),
        'name': file_info.get('page_name'),
        'page_id': file_info.get('page_id'),
        'description': ''
    })

# Save mapping
with open('appflowy-mapping.yaml', 'w') as f:
    yaml.dump(mapping, f, sort_keys=False, default_flow_style=False)
```

### Method 2: Manual Creation

1. Create a new YAML file with the structure shown above
2. Fill in workspace ID and name
3. Get the Documentation parent page ID from AppFlowy
4. Add folder IDs for each category
5. Add page entries for each file

### Method 3: Generate from AppFlowy API

Use the AppFlowy API to query the workspace structure and automatically generate the mapping file.

## Maintaining the Mapping File

### When to Update

Update the mapping file when:

1. **Adding new pages**: Add entries for new documentation files
2. **Renaming pages**: Update the `name` field
3. **Moving pages**: Update the `folder` field
4. **Reorganizing**: Update folder structure

### Best Practices

1. **Version Control**: Commit the mapping file to git
2. **Documentation**: Keep descriptions up to date
3. **Validation**: Verify page IDs are correct
4. **Backup**: Keep a backup copy of the mapping file
5. **Team Sync**: Ensure all team members have the latest version

## Sync Configuration Options

The mapping file includes optional sync configuration:

```yaml
sync:
  # Strategy for handling conflicts
  conflict_resolution: "use_mapping"  # Options: use_mapping, use_status, create_new

  # Whether to validate page IDs before syncing
  validate_ids: true

  # Whether to create missing pages automatically
  auto_create_missing: true

  # Backup sync status file before major operations
  backup_status: true
```

### Conflict Resolution Strategies

- **use_mapping**: Always prefer page IDs from mapping file (default)
- **use_status**: Prefer page IDs from sync status
- **create_new**: Always create new pages (ignores both mapping and status)

## Troubleshooting

### Page Not Found Errors

If sync fails with "page not found" errors:

1. Verify the page ID in AppFlowy still exists
2. Check if the page was deleted or moved
3. Update the mapping file with the correct page ID
4. Or remove the entry to create a new page

### Duplicate Pages Created

If duplicate pages are created despite having a mapping file:

1. Verify the file path in mapping matches exactly (case-sensitive)
2. Check that the mapping file is in the correct location
3. Ensure the YAML syntax is valid
4. Check script logs for mapping file load errors

### Mapping File Not Loaded

If the mapping file isn't being loaded:

1. Check file location: `skills/custom/appflowy-integration/appflowy-mapping.yaml`
2. Verify YAML syntax (use a YAML validator)
3. Check file permissions (must be readable)
4. Look for error messages in script output

## Example: Complete Mapping File

See `/Users/sunginkim/GIT/AI_agents/skills/custom/appflowy-integration/appflowy-mapping.yaml` for a complete working example.

## Related Files

- **Sync Script**: `scripts/sync_docs.py`
- **Sync Status**: `.sync-status.json` (auto-generated)
- **Configuration**: Environment variables in `.env` file

## API Reference

The mapping file is loaded by the `DocumentSyncManager` class:

```python
class DocumentSyncManager:
    def _load_mapping_file(self) -> Optional[dict]:
        """Load mapping file if it exists."""

    def _get_page_id_from_mapping(self, file_path: Path) -> Optional[str]:
        """Get page ID from mapping file for a given file path."""
```

## Version History

- **v1.0** (2025-12-08): Initial mapping file support
  - Added YAML-based mapping configuration
  - Integrated with sync_docs.py
  - Priority-based page ID lookup
