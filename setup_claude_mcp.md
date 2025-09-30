# Setting up Claude Desktop with Brazilian Soccer MCP Server

## Prerequisites
- Claude Desktop app installed
- Python environment with dependencies installed
- Neo4j database running with Brazilian soccer data loaded

## Setup Instructions

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

In Claude, you should see "brazilian-soccer" in the MCP servers list when you start a new conversation.

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

The Neo4j database contains:
- 28 Players
- 12 Teams
- 50 Matches
- 22 Competitions
- 100+ Relationships

Data source: Kaggle Brazilian Football Dataset