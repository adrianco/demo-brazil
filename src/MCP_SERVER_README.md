# Brazilian Soccer Knowledge Graph - MCP Server

## Overview

This directory contains the complete MCP (Model Context Protocol) server implementation for the Brazilian Soccer Knowledge Graph. The server provides 13 specialized tools for querying Brazilian soccer data through Claude and other MCP-compatible clients.

## Architecture

```
src/
├── mcp_server/
│   ├── __init__.py           # Package initialization
│   ├── server.py             # Main MCP server implementation
│   ├── config.py             # Configuration and settings
│   └── tools/                # Tool implementations
│       ├── __init__.py       # Tools package
│       ├── player_tools.py   # Player-related tools
│       ├── team_tools.py     # Team-related tools
│       ├── match_tools.py    # Match and competition tools
│       └── analysis_tools.py # Complex analysis tools
├── run_mcp_server.py         # Server entry point
├── test_mcp_server.py        # Testing and validation
├── requirements-mcp.txt      # Python dependencies
└── MCP_SERVER_README.md      # This documentation
```

## Available Tools

### Player Tools
- **search_player**: Search for players by name or partial name
- **get_player_stats**: Get detailed statistics for a specific player
- **get_player_career**: Get career history and teams for a player

### Team Tools
- **search_team**: Search for teams by name or partial name
- **get_team_roster**: Get current roster for a team
- **get_team_stats**: Get statistics and performance data for a team

### Match Tools
- **get_match_details**: Get detailed information about a specific match
- **search_matches**: Search for matches by teams, date range, or competition
- **get_head_to_head**: Get head-to-head statistics between two teams

### Competition Tools
- **get_competition_standings**: Get current standings for a competition
- **get_competition_top_scorers**: Get top scorers for a competition

### Analysis Tools
- **find_common_teammates**: Find players who were teammates with specific players
- **get_rivalry_stats**: Get detailed rivalry statistics and history

## Installation

### Prerequisites
- Python 3.8+
- Neo4j database running on localhost:7687
- Required Python packages

### Setup
1. Install dependencies:
```bash
pip install -r requirements-mcp.txt
```

2. Ensure Neo4j is running with:
   - URI: bolt://localhost:7687
   - Username: neo4j
   - Password: neo4j123

3. Test the connection:
```bash
python run_mcp_server.py --test-connection
```

## Usage

### Running the Server
```bash
# Start the MCP server
python run_mcp_server.py

# Start with debug logging
python run_mcp_server.py --debug

# Check configuration
python run_mcp_server.py --check
```

### Testing
```bash
# Run the test suite
python test_mcp_server.py
```

### Integration with Claude
Add the server to your Claude configuration:

```json
{
  "mcpServers": {
    "brazilian-soccer": {
      "command": "python",
      "args": ["/path/to/src/run_mcp_server.py"],
      "cwd": "/path/to/src"
    }
  }
}
```

## Configuration

The server can be configured via environment variables:

```bash
# Database settings
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="neo4j123"

# Performance settings
export CACHE_TTL_MINUTES="30"
export QUERY_TIMEOUT_SECONDS="30"

# Logging
export LOG_LEVEL="INFO"
```

## Example Queries

### Player Search
```python
# Search for Pelé
search_player(name="Pelé")

# Get detailed stats
get_player_stats(player_name="Ronaldinho")

# Get career history
get_player_career(player_name="Kaká")
```

### Team Analysis
```python
# Find Santos roster
get_team_roster(team_name="Santos")

# Get Flamengo statistics
get_team_stats(team_name="Flamengo")

# Compare Flamengo vs Palmeiras
get_head_to_head(team1="Flamengo", team2="Palmeiras")
```

### Competition Data
```python
# Get Brasileirão standings
get_competition_standings(competition="Brasileirão")

# Get top scorers
get_competition_top_scorers(competition="Brasileirão", limit=10)
```

### Advanced Analysis
```python
# Find common teammates
find_common_teammates(players=["Ronaldinho", "Kaká"])

# Analyze rivalry
get_rivalry_stats(team1="Flamengo", team2="Vasco", years=10)
```

## Error Handling

The server includes comprehensive error handling:

- **Database Connection**: Graceful handling of Neo4j connection issues
- **Query Validation**: Input parameter validation and sanitization
- **Timeout Management**: Configurable query timeouts
- **Caching**: Automatic caching with TTL to improve performance
- **Logging**: Detailed logging for debugging and monitoring

## Performance Features

- **Caching**: Intelligent caching with configurable TTL
- **Connection Pooling**: Efficient Neo4j connection management
- **Query Optimization**: Optimized Cypher queries for fast response
- **Parallel Processing**: Async/await for concurrent operations
- **Resource Management**: Proper cleanup and resource management

## Testing

The server includes a comprehensive test suite that validates:

- All 13 MCP tools
- Demo questions from the implementation guide
- Error handling scenarios
- Performance benchmarks
- Data integrity checks

Run tests with:
```bash
python test_mcp_server.py
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   ```bash
   # Check if Neo4j is running
   python run_mcp_server.py --test-connection
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements-mcp.txt
   ```

3. **Import Errors**
   ```bash
   # Ensure you're in the src directory
   cd src
   python run_mcp_server.py
   ```

### Debug Mode
```bash
python run_mcp_server.py --debug
```

### Checking Logs
The server logs to stderr by default. Look for:
- Connection status messages
- Query execution times
- Error details
- Cache hit/miss ratios

## Contributing

When extending the server:

1. Follow the existing tool pattern in `tools/` directory
2. Add appropriate error handling and validation
3. Include comprehensive docstrings with context blocks
4. Update the test suite
5. Maintain backward compatibility

## Integration Examples

### Claude Desktop
```json
{
  "mcpServers": {
    "brazilian-soccer": {
      "command": "python",
      "args": ["/workspaces/demo-brazil/src/run_mcp_server.py"]
    }
  }
}
```

### Custom Client
```python
import mcp

async def query_player(name):
    async with mcp.ClientSession(server_path) as session:
        result = await session.call_tool("search_player", {"name": name})
        return result
```

## License

This implementation is part of the Brazilian Soccer Knowledge Graph project and follows the same licensing terms.

## Support

For issues specific to the MCP server implementation:
1. Check the test results in `test_results.json`
2. Review server logs for error details
3. Validate your Neo4j connection and data
4. Ensure all dependencies are correctly installed