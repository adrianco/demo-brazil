# Brazilian Soccer MCP Knowledge Graph - Implementation Guide

## Overview
This document outlines the complete plan for creating an MCP (Model Context Protocol) knowledge graph focused on Brazilian soccer players, teams, and games. This is designed for a demo using free data sources.

---

## Project Requirements

- **Purpose**: Demo/Non-commercial use
- **Data Access**: Free sources only
- **Real-time Updates**: Not required
- **Integration**: MCP server connected to Claude for natural language queries

---

## Data Sources

### Primary Data Sources (Recommended)

#### 1. Kaggle Datasets (Best for Starting)
**Advantages:**
- Completely free
- No API rate limits
- Downloadable CSV/JSON files
- Good historical data
- No registration barriers

**Key Datasets:**
- **Brazilian Soccer Database** (jogos-do-campeonato-brasileiro)
  - Covers matches of main competitions
  - URL: https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro
  
- **Brazilian Football Matches**
  - 14,406+ matches from main Brazilian leagues
  - URL: https://www.kaggle.com/datasets/cuecacuela/brazilian-football-matches

- **Brazilian Soccer League (2003-2019)**
  - Historical league data
  - URL: https://www.kaggle.com/datasets/macedojleo/campeonato-brasileiro-2003-a-2019

#### 2. API-Football (api-football.com)
**Features:**
- Free plan with access to all endpoints
- No credit card required
- Covers Brasil Serie A and 1,100+ competitions
- Always remains free (with limitations)

**Limitations:**
- Daily request limits on free tier
- Good for supplemental data

**Access:** Register at https://dashboard.api-football.com/

#### 3. TheSportsDB
**Features:**
- Free JSON sports API
- Data for Brazilian Serie A and Copa do Brasil
- Team logos and artwork
- Player photos

**Access:**
- Free test key: "123"
- Documentation: https://www.thesportsdb.com/documentation
- Limited to 2 requests per minute on free tier

#### 4. Other Data Sources
- **Wikipedia/DBpedia**: Structured data about notable players, teams, tournaments
- **International Football Results**: 47,000+ international matches (Kaggle)
- **Transfermarkt Data**: Available through Kaggle datasets (scraped)

### Recommended Implementation Strategy

**Phase 1 - Core Data (Offline)**
- Download Kaggle Brazilian Football Matches dataset
- Provides: Teams, players, match results, competitions
- No API limits during development

**Phase 2 - Enhancement (API)**
- Use TheSportsDB for team logos/artwork and player photos
- Use API-Football for current season data (optional)

---

## MCP Server Architecture

### Graph Schema Design

#### Core Entities
1. **Player**
   - Properties: name, birth_date, nationality, position, jersey_number
   - Unique ID: player_id

2. **Team**
   - Properties: name, city, stadium, founded_year, colors
   - Unique ID: team_id

3. **Match**
   - Properties: date, home_score, away_score, competition, attendance
   - Unique ID: match_id

4. **Competition**
   - Properties: name, season, type (league/cup), tier
   - Unique ID: competition_id

5. **Stadium**
   - Properties: name, city, capacity, opened_year
   - Unique ID: stadium_id

6. **Coach**
   - Properties: name, nationality, birth_date
   - Unique ID: coach_id

#### Relationships
- Player → PLAYS_FOR → Team (with date ranges)
- Player → SCORED_IN → Match (with goal details)
- Player → ASSISTED_IN → Match
- Team → COMPETED_IN → Match (home/away)
- Match → PART_OF → Competition
- Match → PLAYED_AT → Stadium
- Player → TRANSFERRED_FROM → Team
- Player → TRANSFERRED_TO → Team (with transfer_date, fee)
- Coach → MANAGES → Team (with date ranges)
- Player → YELLOW_CARD_IN → Match
- Player → RED_CARD_IN → Match

### MCP Tools to Implement

#### 1. Player Tools
```
search_player(name: string, team?: string, position?: string)
get_player_stats(player_id: string, season?: string)
get_player_career(player_id: string)
get_player_transfers(player_id: string)
```

#### 2. Team Tools
```
search_team(name: string)
get_team_roster(team_id: string, season?: string)
get_team_stats(team_id: string, season?: string)
get_team_history(team_id: string)
```

#### 3. Match Tools
```
get_match_details(match_id: string)
search_matches(team?: string, date_from?: string, date_to?: string)
get_head_to_head(team1_id: string, team2_id: string)
get_match_scorers(match_id: string)
```

#### 4. Competition Tools
```
get_competition_standings(competition_id: string, season: string)
get_competition_top_scorers(competition_id: string, season: string)
get_competition_matches(competition_id: string, season: string)
```

#### 5. Analysis Tools
```
find_common_teammates(player1_id: string, player2_id: string)
get_rivalry_stats(team1_id: string, team2_id: string)
find_players_by_career_path(criteria: object)
```

---

## Demo Question Set

### Category 1: Simple Lookups
*Test basic entity retrieval*

1. "Who scored the most goals for Flamengo in 2023?"
2. "What teams has Neymar played for in his career?"
3. "When was the last match between Palmeiras and São Paulo?"
4. "Tell me about Pelé's career statistics"
5. "What is Corinthians' home stadium?"

### Category 2: Relationship Queries
*Test graph traversal*

6. "Which players have played for both Corinthians and Palmeiras?"
7. "Show me all Brazilian players who moved to European clubs in 2024"
8. "What teams did Ronaldo Nazário play for during his career?"
9. "Who were Neymar's teammates at Santos?"
10. "Find all players who scored in a Flamengo vs Fluminense match"

### Category 3: Aggregate & Statistical Analysis
*Test data aggregation*

11. "Which team has won the most Brasileirão titles?"
12. "Who are the top 5 goal scorers in Brazilian Serie A history?"
13. "What's Flamengo's win rate against Internacional in the last 10 years?"
14. "Which stadium has hosted the most championship finals?"
15. "What's the average number of goals per match in Serie A 2023?"

### Category 4: Complex Multi-hop Queries
*Test complex reasoning across relationships*

16. "Find players who scored in a Copa do Brasil final and later played in Europe"
17. "Which coaches have managed multiple championship-winning teams?"
18. "Show me teammates of Neymar at Santos who also made it to European leagues"
19. "Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar"
20. "Which players have won championships with three different Brazilian teams?"

### Category 5: Contextual & Historical
*Test knowledge integration*

21. "Why is Flamengo vs Fluminense called Fla-Flu?"
22. "What makes the Paulista championship (Paulistão) significant?"
23. "Explain the significance of Maracanã stadium in Brazilian football"
24. "Who are considered the greatest Brazilian strikers of all time?"
25. "What was special about Brazil's 1970 World Cup team?"

---

## Demo Flow (Recommended Sequence)

### Act 1: Introduction (Simple Queries)
1. **Start**: "Tell me about Pelé's career"
   - *Shows basic player lookup and stats*
   
2. **Follow-up**: "How many goals did he score for Santos?"
   - *Shows filtered statistics*

### Act 2: Relationships (Graph Traversal)
3. **Teammates**: "Which of Pelé's Santos teammates became famous?"
   - *Demonstrates relationship traversal*
   
4. **Rivalries**: "Show me the history of Flamengo vs Fluminense matches"
   - *Shows head-to-head analysis*

### Act 3: Complex Analysis (Multi-hop)
5. **Career Paths**: "Compare the career trajectories of Ronaldo, Ronaldinho, and Neymar"
   - *Demonstrates multi-entity comparison*
   
6. **Pattern Finding**: "Which players have played for both São Paulo clubs and later moved to Europe?"
   - *Shows complex filtering across multiple relationships*

### Act 4: Synthesis (Reasoning)
7. **Context**: "Why is the São Paulo vs Corinthians derby so important?"
   - *Requires synthesis of historical context and statistics*
   
8. **Insights**: "What trends do you see in Brazilian players moving to Europe over the past decade?"
   - *Demonstrates analytical capabilities using graph data*

---

## Technical Implementation Notes

### Graph Database Options
- **Neo4j**: Best for complex relationship queries
- **NetworkX** (Python): Good for demos, in-memory
- **SQLite with JSON**: Simple, portable, good enough for demo

### MCP Server Framework
```python
# Pseudo-code structure
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("brazilian-soccer-kb")

@server.tool()
async def search_player(name: str) -> list[TextContent]:
    # Query graph database
    # Return player information
    pass

@server.tool()
async def get_player_stats(player_id: str) -> list[TextContent]:
    # Query graph for player statistics
    pass

# Additional tools...
```

### Data Pipeline
1. **Extract**: Download Kaggle datasets
2. **Transform**: Clean and structure data
3. **Load**: Build knowledge graph
4. **Index**: Create search indices for fast lookup
5. **Serve**: Expose via MCP tools

### Performance Considerations
- Pre-compute common aggregations (top scorers, team stats)
- Cache frequently accessed data
- Index player names, team names for fast search
- Limit result sets to prevent overwhelming responses

---

## Expected Claude Interaction Pattern

**User asks**: "Which players have played for both Corinthians and Palmeiras?"

**Claude's internal process**:
1. Uses `search_team("Corinthians")` → gets team_id_1
2. Uses `search_team("Palmeiras")` → gets team_id_2
3. Uses `get_team_roster(team_id_1)` → gets list of players
4. Uses `get_team_roster(team_id_2)` → gets list of players
5. Finds intersection of player lists
6. Uses `get_player_career()` for each to verify timing

**Claude's response**: 
"I found 3 players who played for both rival clubs: [Names]. Notably, [Player X] played for Corinthians from [dates] and later moved to Palmeiras in [year], which was controversial given the rivalry..."

---

## Success Metrics for Demo

### Technical Success
- ✓ All MCP tools respond correctly
- ✓ Query response time < 2 seconds
- ✓ Can handle 25+ sample questions
- ✓ No errors or timeouts

### Demo Impact
- ✓ Shows clear value of knowledge graphs
- ✓ Demonstrates complex reasoning
- ✓ Highlights relationship traversal
- ✓ Proves natural language interface works

### Audience Engagement
- ✓ Answers are accurate and detailed
- ✓ Responses feel natural, not robotic
- ✓ Shows insights not obvious from raw data
- ✓ Demonstrates "aha moments"

---

## Next Steps

### Phase 1: Data Preparation (Week 1)
1. Download Brazilian Football Matches dataset from Kaggle
2. Clean and normalize data
3. Design final graph schema
4. Load into graph database

### Phase 2: MCP Server Development (Week 2)
1. Implement core MCP tools
2. Add caching layer
3. Test all sample questions
4. Optimize slow queries

### Phase 3: Integration & Testing (Week 3)
1. Connect MCP server to Claude
2. Run through demo script
3. Refine responses
4. Add edge cases

### Phase 4: Demo Preparation (Week 4)
1. Prepare presentation slides
2. Create backup scenarios
3. Document known limitations
4. Practice demo flow

---

## Troubleshooting Guide

### Common Issues

**Issue**: Claude doesn't use MCP tools
- **Fix**: Ensure tool descriptions are clear and use keywords from questions

**Issue**: Slow query responses
- **Fix**: Add caching, pre-compute aggregations, reduce graph depth

**Issue**: Incomplete data
- **Fix**: Supplement with API data or acknowledge gaps in demo

**Issue**: Wrong answers
- **Fix**: Validate data quality, add unit tests for each tool

---

## Additional Resources

### Documentation
- MCP Protocol: https://modelcontextprotocol.io
- Neo4j Graph Database: https://neo4j.com/docs
- Kaggle Datasets: https://www.kaggle.com/datasets

### Community
- MCP Discord/Forum for implementation questions
- Brazilian soccer data enthusiasts on Reddit (r/soccer)
- Knowledge graph communities for schema design

### Related Projects
- Similar implementations with other sports
- Other MCP knowledge graph examples
- Graph database best practices

---

## Appendix: Data Schema Examples

### Sample Player Node
```json
{
  "player_id": "P12345",
  "name": "Neymar da Silva Santos Júnior",
  "birth_date": "1992-02-05",
  "nationality": "Brazilian",
  "position": "Forward",
  "current_team_id": "T789"
}
```

### Sample Match Node
```json
{
  "match_id": "M67890",
  "date": "2023-11-15",
  "home_team_id": "T123",
  "away_team_id": "T456",
  "home_score": 2,
  "away_score": 1,
  "competition_id": "C001",
  "stadium_id": "S555"
}
```

### Sample Relationship
```json
{
  "type": "SCORED_IN",
  "player_id": "P12345",
  "match_id": "M67890",
  "minute": 67,
  "goal_type": "penalty"
}
```

---

## Document Version
- **Version**: 1.0
- **Created**: Based on conversation on September 27, 2025
- **Purpose**: Implementation guide for Brazilian Soccer MCP Knowledge Graph demo
- **Status**: Ready for implementation

---

## Contact & Support
For questions about this implementation:
- Review MCP documentation
- Check data source documentation
- Test incrementally with simple queries first
- Build complexity gradually
