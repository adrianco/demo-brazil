# Sample Questions for Brazilian Soccer MCP Server in Claude

## How to Use
Once you have configured Claude Desktop with the MCP server (see setup_claude_mcp.md), you can ask these questions directly in Claude, and it will use the MCP tools to query the Neo4j database.

## Player-Related Questions

### Basic Search
- "Can you search for information about Pelé in the Brazilian soccer database?"
- "Find details about Neymar Jr using the MCP server"
- "Look up information about Ronaldinho"

### Player Statistics
- "Get the statistics for player with ID player_0"
- "Show me the career stats for Kaká"

### Position-Based Queries
- "Find all forwards in the Brazilian soccer database"
- "List midfielders in the database"
- "Which defenders are in the system?"

### Player Comparisons
- "Compare Pelé and Ronaldinho using the MCP tools"
- "Can you compare the stats of player_0 and player_1?"

### Career History
- "Show me the career history for Neymar Jr"
- "What teams has Ronaldo played for?"

## Team-Related Questions

### Team Search
- "Search for information about Flamengo"
- "Find details about Santos FC"
- "Look up Corinthians in the database"

### Team Statistics
- "Get statistics for team with ID team_0"
- "Show me Flamengo's performance stats"

### League Queries
- "Find all teams in Serie A"
- "List teams from the Brazilian championship"

### Team Rosters
- "Get the current roster for Santos"
- "Show me the players on team_0"

### Team Comparisons
- "Compare Flamengo and Santos"
- "Can you compare team_0 with team_1?"

## Match & Competition Questions

### Match Details
- "Get details for match with ID match_0"
- "Show information about a specific match"

### Date-Based Queries
- "Find matches played between January 2023 and March 2023"
- "Show games from the 2023 season"

### Competition Info
- "Get information about competition comp_0"
- "Show details about the Brazilian championship"

## Complex Queries (Combining Multiple Tools)

- "Find all forwards and then compare the top two players"
- "Search for Flamengo and show their roster"
- "Look up Santos and then find their recent matches"

## Data Analysis Questions

- "How many Brazilian players are in the database?"
- "Which team has the most players?"
- "Who are the most common player positions?"

## Testing MCP Functionality

### Connection Test
- "Can you verify the MCP server connection to the Brazilian soccer database?"
- "Test if the Brazilian soccer MCP tools are working"

### Tool Discovery
- "What MCP tools are available for the Brazilian soccer database?"
- "List all available soccer database query tools"

## Example Conversation Flow

**You**: "Search for information about Pelé"

**Claude**: *Uses search_player tool* "I found Pelé in the database. He's listed as a Midfielder, born on January 22, 2006 (note: this appears to be test data), with Brazilian nationality."

**You**: "Now compare him with Ronaldinho"

**Claude**: *Uses compare_players tool* "Let me compare these two legendary Brazilian players..."

## Debugging Questions

If the MCP server isn't responding:
- "Are the MCP servers connected?"
- "Can you list available MCP servers?"
- "Check if brazilian-soccer MCP server is available"

## Notes

- The database contains sample/test data that may not reflect real-world information
- Some birth dates and statistics are placeholder values
- The system has 28 players, 12 teams, and 50 matches loaded
- All queries are executed against the Neo4j graph database in real-time