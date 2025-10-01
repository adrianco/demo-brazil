# Setting up Claude with Brazilian Soccer MCP Server

This guide covers two methods for connecting Claude to the Brazilian Soccer MCP server:
1. Claude Desktop (GUI application)
2. Claude Code (CLI/IDE integration)

## Prerequisites
- Python environment with dependencies installed
- Neo4j database running with Brazilian soccer data loaded
- For Claude Desktop: Claude Desktop app installed
- For Claude Code: Claude Code CLI installed

## Setup Instructions

---

## Option 1: Claude Desktop Setup

### 1. Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "brazilian-soccer": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/workspaces/demo-brazil",
      "env": {
        "PYTHONPATH": "/workspaces/demo-brazil"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

After adding the configuration, restart Claude Desktop for the changes to take effect.

### 3. Verify MCP Server Connection

In Claude Desktop, you should see "brazilian-soccer" in the MCP servers list when you start a new conversation.

---

## Option 2: Claude Code Setup

Claude Code can connect to MCP servers via the CLI configuration file.

### 1. Add MCP Server to Claude Code

Using the Claude Code CLI, add the MCP server:

```bash
# Navigate to project directory
cd /workspaces/demo-brazil

# Add the MCP server using Claude Code CLI
# Note: Use -- to separate command arguments from claude mcp options
claude mcp add brazilian-soccer python -- -m src.mcp_server.server
```

Alternatively, manually edit the Claude Code configuration file:

**Location**: `~/.config/claude-code/config.json` (Linux/macOS) or `%APPDATA%\claude-code\config.json` (Windows)

```json
{
  "mcpServers": {
    "brazilian-soccer": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/workspaces/demo-brazil",
      "env": {
        "PYTHONPATH": "/workspaces/demo-brazil",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "neo4j123"
      }
    }
  }
}
```

### 2. Start Claude Code with MCP Support

Start a new Claude Code session in your project directory:

```bash
cd /workspaces/demo-brazil
claude
```

### 3. Verify MCP Connection

In the Claude Code session, the MCP server should automatically connect. You can verify by asking:

```
Use the brazilian-soccer MCP to search for Pelé
```

Claude Code will automatically discover and use the available MCP tools.

### 4. Alternative: Use MCP Server Directly in Code

You can also interact with the MCP server programmatically in Claude Code:

```bash
# List available MCP servers
claude mcp list

# Test MCP server connection
claude mcp test brazilian-soccer

# Remove MCP server (if needed)
claude mcp remove brazilian-soccer
```

## Sample Questions to Test

Once configured, you can ask Claude questions like:

### Player Queries
- "Search for information about Pelé"
- "Find all forwards in the database"
- "Get statistics for player_0"
- "Compare Ronaldinho and Kaká"
- "Show me Neymar's career history"

### Team Queries
- "Search for Flamengo"
- "Get the roster for Santos"
- "Find all teams in Serie A"
- "Compare Flamengo and Corinthians"
- "Show team statistics for team_0"

### Match Queries
- "Get details for match_0"
- "Find matches between January and March 2023"
- "Show competition information for comp_0"

## Available MCP Tools

The Brazilian Soccer MCP server provides 13 tools:

1. **search_player** - Search for players by name
2. **get_player_stats** - Get player statistics
3. **search_players_by_position** - Find players by position
4. **get_player_career** - Get player career history
5. **compare_players** - Compare two players
6. **search_team** - Search for teams by name
7. **get_team_stats** - Get team statistics
8. **get_team_roster** - Get team roster
9. **search_teams_by_league** - Find teams by league
10. **compare_teams** - Compare two teams
11. **get_match_details** - Get match details
12. **search_matches_by_date** - Find matches by date range
13. **get_competition_info** - Get competition information

## Troubleshooting

### If MCP server doesn't appear in Claude:

1. Check Neo4j is running:
```bash
neo4j status
```

2. Verify Python dependencies:
```bash
pip install neo4j mcp aiohttp
```

3. Test the server manually:
```bash
cd /workspaces/demo-brazil
python -m src.mcp_server.server
```

4. Check Claude Desktop logs for errors:
- macOS: `~/Library/Logs/Claude/`
- Windows: `%LOCALAPPDATA%\Claude\Logs\`

### Common Issues:

- **"Failed to connect to Neo4j"**: Ensure Neo4j is running and credentials are correct (neo4j/neo4j123)
- **"Module not found"**: Install missing Python dependencies
- **"No data found"**: Run `python load_kaggle_data.py` to load the dataset

## Database Information

The Neo4j database contains (with full dataset):
- **1,197 Nodes**:
  - 1,000 Matches
  - 100 Transfers
  - 40 Players (including Pelé, Neymar, Ronaldo, Ronaldinho)
  - 20 Teams (Serie A teams like Flamengo, Corinthians, Palmeiras)
  - 17 Stadiums
  - 10 Competitions
  - 10 Coaches

- **10,534 Relationships**:
  - 4,400 PLAYED_IN (player match participation)
  - 1,000 HOME_TEAM, 1,000 AWAY_TEAM
  - 797 PLAYS_FOR (player-team relationships)
  - 543 SCORED_IN (goal records)
  - 474 ASSISTED_IN (assist records)
  - Plus stadium, competition, and transfer relationships

Data source: Generated Brazilian Football Dataset (Kaggle-compatible format)

### Quick Start with Sample Data

If you haven't loaded the full dataset yet:

```bash
# Generate the full dataset
python scripts/generate_full_dataset.py

# Load into Neo4j
python scripts/load_kaggle_data.py
```

## Testing with Claude Code (Current Session)

Since you're already in a Claude Code session, you can test the MCP server right now:

### 1. Add the MCP Server

```bash
claude mcp add brazilian-soccer python -- -m src.mcp_server.server
```

### 2. Test Queries

Try these queries in your current session:

**Player Queries:**
```
Use brazilian-soccer MCP to search for Neymar
Use brazilian-soccer MCP to find all forwards
Use brazilian-soccer MCP to get Pelé's statistics
```

**Team Queries:**
```
Use brazilian-soccer MCP to search for Flamengo
Use brazilian-soccer MCP to compare Flamengo and Corinthians
Use brazilian-soccer MCP to get Santos roster
```

**Match Queries:**
```
Use brazilian-soccer MCP to find matches in 2023
Use brazilian-soccer MCP to get Copa do Brasil competition info
```