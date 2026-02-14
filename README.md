# Notion Kanban CLI Tool

A command-line tool for interacting with Notion kanban boards, designed for AI agent integration.

## Installation

### Quick Install (Recommended)

1. Clone this repository:

```bash
git clone <repository-url>
cd notion-tool
```

2. Run the install script:

```bash
./install.sh
```

3. Set your Notion API key:

```bash
export NOTION_API_KEY="your-api-key-here"
```

Add this to your `.zshenv` or `.bashrc` for persistence.

### Uninstall

To remove the tool:

```bash
./uninstall.sh
```

### Manual Install (Alternative)

1. Clone or navigate to this repository
2. Install in editable mode:

```bash
pip install -e .
```

## Configuration

The tool requires `NOTION_API_KEY` to be set as an environment variable:

```bash
export NOTION_API_KEY="your-api-key-here"
```

Add this to your `.zshenv` or `.bashrc` for persistence.

## Usage

### Available Commands

#### Read Item Details

```bash
notion-tool read --database <database-id> <item-id>
```

Example:
```bash
notion-tool read --database 0509def271a84947b6a55ddf1caee4df page-id-123
```

#### Update Item Status

```bash
notion-tool update-status --database <database-id> <item-id> <status>
```

Example:
```bash
notion-tool update-status --database 0509def271a84947b6a55ddf1caee4df page-id-123 "In Progress"
```

#### Query Items

```bash
notion-tool query --database <database-id> [OPTIONS]
```

Options:
- `--status, -s`: Filter by status
- `--tags, -t`: Filter by tags (comma-separated)
- `--filter, -f`: Custom filter (e.g., `priority=high`)
- `--limit, -l`: Maximum number of results

Examples:
```bash
# Query by status
notion-tool query --database 0509def271a84947b6a55ddf1caee4df --status "In Progress"

# Query by tags
notion-tool query --database 0509def271a84947b6a55ddf1caee4df --tags "urgent,important"

# Query with limit
notion-tool query --database 0509def271a84947b6a55ddf1caee4df --limit 5
```

#### List Status Options

```bash
notion-tool list-status --database <database-id>
```

Example:
```bash
notion-tool list-status --database 0509def271a84947b6a55ddf1caee4df
```

#### List Tag Options

```bash
notion-tool list-tags --database <database-id>
```

Example:
```bash
notion-tool list-tags --database 0509def271a84947b6a55ddf1caee4df
```

#### Get Database Schema

```bash
notion-tool schema --database <database-id>
```

Example:
```bash
notion-tool schema --database 0509def271a84947b6a55ddf1caee4df
```

## Output Format

All commands output JSON for easy parsing:

### Success Response
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": {
    "message": "Invalid status 'Archived'",
    "available_options": ["Todo", "In Progress", "Done"]
  }
}
```

## AI Agent Integration

The tool is designed for AI agents to use via shell commands:

```bash
# Get all items in progress
notion-tool query --database 0509def271a84947b6a55ddf1caee4df --status "In Progress"

# Update status to done
notion-tool update-status --database 0509def271a84947b6a55ddf1caee4df page-id "Done"

# Get available statuses
notion-tool list-status --database 0509def271a84947b6a55ddf1caee4df
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```
