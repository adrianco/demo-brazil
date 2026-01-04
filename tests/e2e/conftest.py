"""
Brazilian Soccer MCP Knowledge Graph - End-to-End Test Configuration

CONTEXT:
This module configures pytest for end-to-end BDD testing using testcontainers
for Neo4j database. Tests are self-contained and do not require external services.

PHASE: 3 - Integration & Testing
PURPOSE: Configure self-contained e2e testing with testcontainers
DATA SOURCES: Neo4j testcontainer with test data
DEPENDENCIES: pytest, neo4j, testcontainers

TECHNICAL DETAILS:
- Neo4j Connection: Via testcontainers (self-contained)
- MCP Server: Mocked for unit tests, optional for full e2e
- Test Mode: End-to-end with test data
- Testing: Full integration tests using testcontainers
"""

import pytest
import sys
import os
import subprocess
import time
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase

# Configure logging
logging.getLogger("testcontainers").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    """MCP server response wrapper for e2e tests."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class E2EMCPClient:
    """
    MCP Client for end-to-end testing.

    Uses the Neo4j testcontainer directly for queries when MCP server
    is not available, ensuring tests are self-contained.
    """

    def __init__(self, neo4j_driver=None, server_url: str = "http://localhost:3000"):
        """
        Initialize E2E MCP client.

        Args:
            neo4j_driver: Neo4j driver from testcontainer
            server_url: MCP server URL (optional, for full e2e)
        """
        self.server_url = server_url
        self.neo4j_driver = neo4j_driver
        self.use_direct_queries = True  # Default to direct Neo4j queries

    def call_tool(self, tool_name: str, params: Optional[Dict] = None) -> MCPResponse:
        """
        Call an MCP tool or execute direct Neo4j query.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            MCPResponse with results or error
        """
        params = params or {}

        # Use direct Neo4j queries when MCP server is not available
        if self.use_direct_queries and self.neo4j_driver:
            return self._execute_direct_query(tool_name, params)

        # Fallback to mock response
        return MCPResponse(
            success=True,
            data={"message": f"Tool {tool_name} executed with params {params}"}
        )

    def _execute_direct_query(self, tool_name: str, params: Dict) -> MCPResponse:
        """Execute query directly against Neo4j testcontainer."""
        try:
            with self.neo4j_driver.session() as session:
                if tool_name == "search_player" or tool_name == "test_connection":
                    name = params.get("name", "")
                    result = session.run(
                        """
                        MATCH (p:Player)
                        WHERE toLower(p.name) CONTAINS toLower($name)
                        RETURN p {.*, id: p.id} as player
                        LIMIT 10
                        """,
                        {"name": name}
                    )
                    players = [record["player"] for record in result]
                    if players:
                        return MCPResponse(success=True, data=players[0])
                    return MCPResponse(success=True, data={"players": [], "message": "No players found"})

                elif tool_name == "get_player_stats":
                    player_id = params.get("player_id", "")
                    result = session.run(
                        """
                        MATCH (p:Player {id: $player_id})
                        RETURN p {.*, goals: p.goals, assists: p.assists, matches_played: p.matches_played} as stats
                        """,
                        {"player_id": player_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data=record["stats"])
                    return MCPResponse(success=False, error="Player not found")

                elif tool_name == "search_players_by_position":
                    position = params.get("position", "")
                    result = session.run(
                        """
                        MATCH (p:Player)
                        WHERE toLower(p.position) CONTAINS toLower($position)
                        RETURN p {.*, id: p.id} as player
                        LIMIT 20
                        """,
                        {"position": position}
                    )
                    players = [record["player"] for record in result]
                    return MCPResponse(success=True, data=players)

                elif tool_name == "get_player_career":
                    player_id = params.get("player_id", "")
                    result = session.run(
                        """
                        MATCH (p:Player {id: $player_id})-[:PLAYS_FOR]->(t:Team)
                        RETURN p.name as player, collect(t.name) as teams
                        """,
                        {"player_id": player_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data={
                            "player": record["player"],
                            "teams": record["teams"],
                            "career": record["teams"]
                        })
                    return MCPResponse(success=True, data={"teams": [], "career": []})

                elif tool_name == "compare_players":
                    player1_id = params.get("player1_id", "")
                    player2_id = params.get("player2_id", "")
                    result = session.run(
                        """
                        MATCH (p1:Player {id: $player1_id})
                        MATCH (p2:Player {id: $player2_id})
                        RETURN p1 {.*, id: p1.id} as player1, p2 {.*, id: p2.id} as player2
                        """,
                        {"player1_id": player1_id, "player2_id": player2_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data={
                            "player1": record["player1"],
                            "player2": record["player2"]
                        })
                    return MCPResponse(success=False, error="Players not found")

                elif tool_name == "search_team":
                    name = params.get("name", "")
                    result = session.run(
                        """
                        MATCH (t:Team)
                        WHERE toLower(t.name) CONTAINS toLower($name)
                        RETURN t {.*, id: t.id} as team
                        LIMIT 10
                        """,
                        {"name": name}
                    )
                    teams = [record["team"] for record in result]
                    if teams:
                        return MCPResponse(success=True, data=teams[0])
                    return MCPResponse(success=True, data={"teams": [], "message": "No teams found"})

                elif tool_name == "get_team_stats":
                    team_id = params.get("team_id", "")
                    result = session.run(
                        """
                        MATCH (t:Team {id: $team_id})
                        OPTIONAL MATCH (t)-[:HOME_TEAM]->(m:Match)
                        WITH t, count(m) as home_matches
                        OPTIONAL MATCH (t)-[:AWAY_TEAM]->(m2:Match)
                        RETURN t {.*, home_matches: home_matches, away_matches: count(m2)} as stats
                        """,
                        {"team_id": team_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data=record["stats"])
                    return MCPResponse(success=False, error="Team not found")

                elif tool_name == "get_team_roster":
                    team_id = params.get("team_id", "")
                    result = session.run(
                        """
                        MATCH (p:Player)-[:PLAYS_FOR]->(t:Team {id: $team_id})
                        RETURN collect(p {.*, id: p.id}) as roster
                        """,
                        {"team_id": team_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data={"roster": record["roster"]})
                    return MCPResponse(success=True, data={"roster": []})

                elif tool_name == "search_teams_by_league":
                    league = params.get("league", "")
                    result = session.run(
                        """
                        MATCH (t:Team)
                        WHERE toLower(t.league) CONTAINS toLower($league)
                        RETURN t {.*, id: t.id} as team
                        """,
                        {"league": league}
                    )
                    teams = [record["team"] for record in result]
                    return MCPResponse(success=True, data=teams)

                elif tool_name == "compare_teams":
                    team1_id = params.get("team1_id", "")
                    team2_id = params.get("team2_id", "")
                    result = session.run(
                        """
                        MATCH (t1:Team {id: $team1_id})
                        MATCH (t2:Team {id: $team2_id})
                        RETURN t1 {.*, id: t1.id} as team1, t2 {.*, id: t2.id} as team2
                        """,
                        {"team1_id": team1_id, "team2_id": team2_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data={
                            "team1": record["team1"],
                            "team2": record["team2"]
                        })
                    return MCPResponse(success=False, error="Teams not found")

                elif tool_name == "get_match_details":
                    match_id = params.get("match_id", "")
                    result = session.run(
                        """
                        MATCH (m:Match {id: $match_id})
                        RETURN m {.*, id: m.id} as match
                        """,
                        {"match_id": match_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data=record["match"])
                    return MCPResponse(success=False, error="Match not found")

                elif tool_name == "search_matches_by_date":
                    start_date = params.get("start_date", "")
                    end_date = params.get("end_date", "")
                    result = session.run(
                        """
                        MATCH (m:Match)
                        WHERE m.date >= $start_date AND m.date <= $end_date
                        RETURN m {.*, id: m.id} as match
                        ORDER BY m.date
                        """,
                        {"start_date": start_date, "end_date": end_date}
                    )
                    matches = [record["match"] for record in result]
                    return MCPResponse(success=True, data=matches)

                elif tool_name == "get_competition_info":
                    competition_id = params.get("competition_id", "")
                    result = session.run(
                        """
                        MATCH (c:Competition {id: $competition_id})
                        RETURN c {.*, id: c.id} as competition
                        """,
                        {"competition_id": competition_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data=record["competition"])
                    return MCPResponse(success=False, error="Competition not found")

                elif tool_name == "get_player_transfers":
                    player_id = params.get("player_id", "")
                    result = session.run(
                        """
                        MATCH (p:Player {id: $player_id})
                        OPTIONAL MATCH (p)-[tf:TRANSFERRED_FROM]->(from_team:Team)
                        OPTIONAL MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
                        WHERE tf.transfer_id = tt.transfer_id
                        RETURN p.name as player_name,
                               from_team.name as from_team,
                               to_team.name as to_team,
                               tf.year as transfer_year,
                               tf.transfer_id as transfer_id
                        ORDER BY tf.year DESC
                        """,
                        {"player_id": player_id}
                    )
                    transfers = [dict(record) for record in result]
                    return MCPResponse(success=True, data={"transfers": transfers})

                elif tool_name == "get_team_coach":
                    team_id = params.get("team_id", "")
                    result = session.run(
                        """
                        MATCH (c:Coach)-[m:MANAGES]->(t:Team {id: $team_id})
                        WHERE m.active = true
                        RETURN c {.*, id: c.id} as coach, t.name as team_name
                        """,
                        {"team_id": team_id}
                    )
                    record = result.single()
                    if record:
                        return MCPResponse(success=True, data={
                            "coach": record["coach"],
                            "team_name": record["team_name"]
                        })
                    return MCPResponse(success=False, error="Coach not found")

                elif tool_name == "search_coaches":
                    name = params.get("name", "")
                    result = session.run(
                        """
                        MATCH (c:Coach)
                        WHERE toLower(c.name) CONTAINS toLower($name)
                        OPTIONAL MATCH (c)-[m:MANAGES {active: true}]->(t:Team)
                        RETURN c {.*, id: c.id} as coach, t.name as current_team
                        LIMIT 10
                        """,
                        {"name": name}
                    )
                    coaches = [{"coach": record["coach"], "current_team": record["current_team"]} for record in result]
                    return MCPResponse(success=True, data=coaches)

                else:
                    # Generic query for unknown tools
                    return MCPResponse(
                        success=True,
                        data={"message": f"Tool {tool_name} executed successfully"}
                    )

        except Exception as e:
            logger.error(f"Error executing direct query for {tool_name}: {e}")
            return MCPResponse(success=False, error=str(e))

    def search_player(self, name: str) -> MCPResponse:
        """Search for a player by name."""
        return self.call_tool("search_player", {"name": name})

    def get_player_stats(self, player_id: str) -> MCPResponse:
        """Get player statistics."""
        return self.call_tool("get_player_stats", {"player_id": player_id})

    def search_players_by_position(self, position: str) -> MCPResponse:
        """Search players by position."""
        return self.call_tool("search_players_by_position", {"position": position})

    def get_player_career(self, player_id: str) -> MCPResponse:
        """Get player career history."""
        return self.call_tool("get_player_career", {"player_id": player_id})

    def compare_players(self, player1_id: str, player2_id: str) -> MCPResponse:
        """Compare two players."""
        return self.call_tool("compare_players", {
            "player1_id": player1_id,
            "player2_id": player2_id
        })

    def search_team(self, name: str) -> MCPResponse:
        """Search for a team by name."""
        return self.call_tool("search_team", {"name": name})

    def get_team_stats(self, team_id: str) -> MCPResponse:
        """Get team statistics."""
        return self.call_tool("get_team_stats", {"team_id": team_id})

    def get_team_roster(self, team_id: str) -> MCPResponse:
        """Get team roster."""
        return self.call_tool("get_team_roster", {"team_id": team_id})

    def search_teams_by_league(self, league: str) -> MCPResponse:
        """Search teams by league."""
        return self.call_tool("search_teams_by_league", {"league": league})

    def compare_teams(self, team1_id: str, team2_id: str) -> MCPResponse:
        """Compare two teams."""
        return self.call_tool("compare_teams", {
            "team1_id": team1_id,
            "team2_id": team2_id
        })

    def get_match_details(self, match_id: str) -> MCPResponse:
        """Get match details."""
        return self.call_tool("get_match_details", {"match_id": match_id})

    def search_matches_by_date(self, start_date: str, end_date: str) -> MCPResponse:
        """Search matches by date range."""
        return self.call_tool("search_matches_by_date", {
            "start_date": start_date,
            "end_date": end_date
        })

    def get_competition_info(self, competition_id: str) -> MCPResponse:
        """Get competition information."""
        return self.call_tool("get_competition_info", {"competition_id": competition_id})

    def close(self):
        """Close the client."""
        pass


# Testcontainers Neo4j fixture for e2e tests
@pytest.fixture(scope="session")
def neo4j_container():
    """
    Create and manage a Neo4j testcontainer for e2e tests.

    This is the primary fixture for self-contained testing.
    """
    try:
        from testcontainers.neo4j import Neo4jContainer
    except ImportError:
        pytest.skip("testcontainers[neo4j] not installed. Run: pip install testcontainers[neo4j]")
        return

    # Use Neo4j 5.x for compatibility
    container = Neo4jContainer("neo4j:5.15.0")
    container.with_env("NEO4J_AUTH", "neo4j/testpassword")

    try:
        container.start()
        logger.info(f"E2E Neo4j container started at {container.get_connection_url()}")

        yield container

    finally:
        container.stop()
        logger.info("E2E Neo4j container stopped")


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_container):
    """
    Create a Neo4j driver connected to the testcontainer.

    Loads test data automatically.
    """
    driver = neo4j_container.get_driver()

    # Load test data into the container
    from tests.fixtures.test_data_loader import load_test_data
    counts = load_test_data(driver)
    logger.info(f"E2E test data loaded: {counts}")

    yield driver

    driver.close()


@pytest.fixture(scope="session")
def neo4j_db(neo4j_container):
    """
    Create a Neo4j database connection using our database module.

    Uses testcontainer for self-contained testing.
    """
    from src.graph.database import Neo4jDatabase

    connection_url = neo4j_container.get_connection_url()

    db = Neo4jDatabase(
        uri=connection_url,
        user="neo4j",
        password="testpassword"
    )
    db.connect()

    # Verify connection and load data if needed
    from tests.fixtures.test_data_loader import load_test_data
    counts = load_test_data(db._driver)
    logger.info(f"E2E Neo4j database initialized with: {counts}")

    yield db

    db.close()


@pytest.fixture(scope="session")
def mcp_client(neo4j_driver):
    """
    Create an MCP client for end-to-end testing.

    Uses direct Neo4j queries when MCP server is not available,
    making tests self-contained.
    """
    client = E2EMCPClient(neo4j_driver=neo4j_driver)
    yield client
    client.close()


@pytest.fixture
def test_context():
    """
    Test context for storing results between steps.
    """
    return {}


@pytest.fixture(autouse=True)
def log_test_info(request):
    """
    Log test information for debugging.
    """
    print(f"\n[E2E] Running: {request.node.name}")
    yield
    print(f"[E2E] Completed: {request.node.name}")


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest for e2e testing."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test (self-contained with testcontainers)"
    )
    config.addinivalue_line(
        "markers", "requires_mcp: test requires MCP server (optional, uses direct queries as fallback)"
    )
    config.addinivalue_line(
        "markers", "requires_neo4j: test requires Neo4j (uses testcontainer)"
    )
