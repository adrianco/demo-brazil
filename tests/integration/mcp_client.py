"""
Brazilian Soccer MCP Knowledge Graph - MCP Client for Integration Tests

CONTEXT:
This module implements a real MCP client that connects to the running MCP server
for end-to-end BDD testing against the Neo4j database.

PHASE: 3 - Integration & Testing
PURPOSE: Real MCP client for end-to-end BDD tests
DATA SOURCES: Live MCP server and Neo4j database
DEPENDENCIES: httpx, asyncio, json

TECHNICAL DETAILS:
- MCP Server: http://localhost:3000 (default)
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Communication: JSON-RPC 2.0 protocol
- Testing: End-to-end BDD scenarios with real data
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    """MCP server response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class RealMCPClient:
    """
    Real MCP client for end-to-end testing against live MCP server.

    This client communicates with the actual MCP server running locally,
    which in turn queries the Neo4j database with real data.
    """

    def __init__(self, server_url: str = "http://localhost:3000"):
        """
        Initialize MCP client.

        Args:
            server_url: MCP server URL
        """
        self.server_url = server_url
        self.client = httpx.Client(timeout=30.0)
        self.request_id = 0

    def _build_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """
        Build JSON-RPC request.

        Args:
            method: Tool/method name
            params: Method parameters

        Returns:
            JSON-RPC request object
        """
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        return request

    def call_tool(self, tool_name: str, params: Optional[Dict] = None) -> MCPResponse:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            MCPResponse with results or error
        """
        try:
            request = self._build_request(f"tools/{tool_name}", params)

            logger.info(f"Calling MCP tool: {tool_name}")
            logger.debug(f"Request: {json.dumps(request, indent=2)}")

            response = self.client.post(
                f"{self.server_url}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Response: {json.dumps(result, indent=2)}")

                if "result" in result:
                    return MCPResponse(success=True, data=result["result"])
                elif "error" in result:
                    return MCPResponse(success=False, error=result["error"]["message"])
                else:
                    return MCPResponse(success=False, error="Invalid response format")
            else:
                return MCPResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )

        except httpx.ConnectError:
            logger.error(f"Failed to connect to MCP server at {self.server_url}")
            return MCPResponse(
                success=False,
                error=f"Cannot connect to MCP server at {self.server_url}. Is it running?"
            )
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
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
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Async version for async tests
class AsyncMCPClient:
    """Async version of MCP client for async BDD tests."""

    def __init__(self, server_url: str = "http://localhost:3000"):
        self.server_url = server_url
        self.client = None
        self.request_id = 0

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def call_tool(self, tool_name: str, params: Optional[Dict] = None) -> MCPResponse:
        """Call an MCP tool asynchronously."""
        if not self.client:
            self.client = httpx.AsyncClient(timeout=30.0)

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": f"tools/{tool_name}",
            "params": params or {}
        }

        try:
            response = await self.client.post(
                f"{self.server_url}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return MCPResponse(success=True, data=result["result"])
                elif "error" in result:
                    return MCPResponse(success=False, error=result["error"]["message"])

            return MCPResponse(success=False, error=f"HTTP {response.status_code}")

        except Exception as e:
            return MCPResponse(success=False, error=str(e))