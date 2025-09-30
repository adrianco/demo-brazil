# Brazilian Soccer MCP Knowledge Graph 🇧🇷 ⚽

A comprehensive Model Context Protocol (MCP) server implementation providing intelligent access to Brazilian soccer data through a Neo4j graph database. This project enables Claude AI to answer complex questions about Brazilian soccer players, teams, matches, and competitions.

## NOTE: This repo was used as part of an AI demo
The initial setup and installation of Claude and Claude-Flow was done in Codespaces. The idea for the demo was a brief chat with the Claude mobile app, saved as a file in the repo. Claude was used to install and document Neo4j. Then on the day of the demo, claude-flow was run. Most of the prompts and some of the results are recorded in prompts.txt. Claude-flow ran for about 1hr before completing the task. On trying to run the BDD tests, more problems were found and fixed. Claude had to be told to download the full dataset, and to fix all the problems so that 100% had no errors, and to run end to end BDD tests against the live database. The testing process resulting in a functonal demo took around another hour, with occasional guidance.

## 📋 Project Overview

This implementation follows the three-phase approach outlined in `brazilian-soccer-mcp-guide.md`:

- **Phase 1 (Core Data)**: Neo4j graph database with Brazilian soccer entities
- **Phase 2 (Enhancement)**: MCP server with 13 specialized query tools
- **Phase 3 (Integration)**: BDD testing with pytest-bdd

## 🚀 Quick Start

### Prerequisites

1. **Neo4j Database** (Community Edition)
   - Already configured at `bolt://localhost:7687`
   - Credentials: `neo4j` / `neo4j123`
   - See `docs/neo4j-setup.md` for details

2. **Python 3.8+**
   ```bash
   pip install -r requirements.txt
   ```

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/demo-brazil.git
cd demo-brazil

# 2. Install dependencies
pip install neo4j pytest pytest-bdd pandas click

# 3. Start Neo4j (if not running)
sudo service neo4j start

# 4. Initialize the database
python main.py build --clear-first

# 5. Run tests
pytest tests/ -v
```

## 🏗️ Project Structure

```
demo-brazil/
├── src/
│   ├── graph/               # Neo4j integration
│   │   ├── database.py      # Connection management
│   │   ├── models.py        # Entity models & schema
│   │   └── queries.py       # Cypher query builders
│   ├── data_pipeline/       # Data processing
│   │   ├── kaggle_loader.py # Data loading
│   │   └── graph_builder.py # Graph construction
│   ├── mcp_server/          # MCP server implementation
│   │   ├── server.py        # Main server
│   │   └── tools/           # MCP tools
│   └── utils/               # Utilities
├── tests/                   # BDD tests
│   ├── features/            # Gherkin scenarios
│   └── step_defs/           # Step implementations
├── config/                  # Configuration files
├── data/                    # Data storage
└── main.py                  # CLI interface
```

## 🔧 MCP Server Tools

The server implements 13 specialized tools for querying Brazilian soccer data:

### Player Tools
- `search_player` - Search players by name, team, or position
- `get_player_stats` - Get detailed player statistics
- `get_player_career` - Get complete career history

### Team Tools
- `search_team` - Search teams by name
- `get_team_roster` - Get current team roster
- `get_team_stats` - Get team statistics

### Match Tools
- `get_match_details` - Get specific match information
- `search_matches` - Search matches by criteria
- `get_head_to_head` - Get team rivalry statistics

### Competition Tools
- `get_competition_standings` - Get league standings
- `get_competition_top_scorers` - Get top scorers

### Analysis Tools
- `find_common_teammates` - Find shared teammates
- `get_rivalry_stats` - Analyze team rivalries

## 📊 Graph Schema

### Entities (Nodes)
- **Player**: Brazilian soccer players
- **Team**: Soccer clubs and teams
- **Match**: Individual matches
- **Competition**: Tournaments and leagues
- **Stadium**: Soccer venues
- **Coach**: Team coaches

### Relationships
- `PLAYS_FOR` - Player → Team
- `SCORED_IN` - Player → Match
- `COMPETED_IN` - Team → Match
- `HOSTED_AT` - Match → Stadium
- `PART_OF` - Match → Competition
- `COACHED_BY` - Team → Coach

## 🧪 Testing

The project uses BDD (Behavior-Driven Development) with pytest-bdd:

```bash
# Run all tests
pytest tests/ -v

# Run specific feature
pytest tests/features/player_management.feature -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Scenarios

```gherkin
Feature: Player Search
  Scenario: Search for famous Brazilian player
    Given the knowledge graph contains player data
    When I search for "Neymar"
    Then I should get player details with career information
```

## 💻 CLI Commands

```bash
# Database Management
python main.py test-connection    # Test Neo4j connection
python main.py schema             # Create database schema
python main.py build              # Build complete graph
python main.py stats              # Show database statistics
python main.py validate           # Validate graph integrity

# Data Loading
python main.py load-data --source sample  # Load sample data
python main.py clear              # Clear all data

# MCP Server
python src/run_mcp_server.py     # Start MCP server
```

## 📈 Implementation Status

### ✅ Phase 1: Core Data (Complete)
- [x] Neo4j database connection
- [x] Graph schema with 6+ entities
- [x] Data loader for Brazilian soccer data
- [x] Graph builder with batch operations
- [x] Sample data generation

### ✅ Phase 2: Enhancement (Complete)
- [x] MCP server implementation
- [x] 13 specialized query tools
- [x] Caching layer for performance
- [x] Error handling and validation

### ✅ Phase 3: Integration & Testing (Complete)
- [x] BDD tests with pytest-bdd
- [x] 39+ test scenarios
- [x] Integration with Neo4j
- [x] Demo question coverage

## 🎯 Demo Questions Supported

The system can answer all 25 demo questions including:

1. **Simple Lookups**: "Who scored the most goals for Flamengo in 2023?"
2. **Relationships**: "Which players have played for both Corinthians and Palmeiras?"
3. **Aggregations**: "What's Flamengo's win rate against Internacional?"
4. **Complex Queries**: "Find players who scored in a Copa do Brasil final"
5. **Historical Context**: "What makes the Paulista championship significant?"

## 📝 Context Block Documentation

Every code file includes a detailed context block:

```python
"""
Brazilian Soccer MCP Knowledge Graph - [Module Name]

CONTEXT:
This module implements [functionality] for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying player, team, match, and competition data
stored in a Neo4j graph database.

PHASE: [1/2/3] - [Core Data/Enhancement/Integration]
PURPOSE: [Specific purpose]
DATA SOURCES: [Data sources used]
DEPENDENCIES: [Key dependencies]

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: [Entities and relationships]
- Performance: [Optimization strategies]
- Testing: [Test coverage]

INTEGRATION:
- MCP Tools: [Tools provided]
- Error Handling: [Strategy]
- Rate Limiting: [If applicable]
"""
```

## 🔐 Configuration

Database configuration in `config/database.json`:

```json
{
  "development": {
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "username": "neo4j",
      "password": "neo4j123"
    }
  }
}
```

## 📊 Performance

- Query response time: < 2 seconds
- Batch processing: 1000 records/batch
- Caching: 30-minute TTL
- Connection pooling: 50 max connections

## 🛠️ Development

### Adding New MCP Tools

1. Create tool in `src/mcp_server/tools/`
2. Register in `src/mcp_server/server.py`
3. Add BDD tests in `tests/features/`
4. Update documentation

### Data Sources

- **Primary**: Kaggle Brazilian Football Matches dataset
- **Enhancement**: TheSportsDB API (optional)
- **Current Season**: API-Football (optional)

## 📚 Documentation

- `brazilian-soccer-mcp-guide.md` - Complete implementation guide
- `docs/neo4j-setup.md` - Neo4j setup instructions
- `src/MCP_SERVER_README.md` - MCP server details
- `src/IMPLEMENTATION_SUMMARY.md` - Technical summary

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for demo/educational purposes. See LICENSE for details.

## 🙏 Acknowledgments

- Brazilian soccer data from Kaggle community
- Neo4j for graph database technology
- Anthropic for MCP protocol specification
- pytest-bdd for BDD testing framework

---

Built with ❤️ for demonstrating MCP capabilities with Brazilian soccer data
