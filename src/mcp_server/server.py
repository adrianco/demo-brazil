"""
Brazilian Soccer MCP Knowledge Graph - Main Server

CONTEXT:
This module implements the main MCP server for the Brazilian Soccer Knowledge Graph.
It provides tools for querying player, team, match, and competition data
stored in a Neo4j graph database.

PHASE: 2/3 - Enhancement/Integration
PURPOSE: MCP server implementation for Claude integration
DATA SOURCES: Neo4j graph database with Brazilian soccer data
DEPENDENCIES: mcp, neo4j, asyncio

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition entities
- Performance: Caching, query optimization
- Testing: Integration with demo questions

INTEGRATION:
- MCP Tools: Complete tool set for soccer data queries
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

from neo4j import AsyncGraphDatabase
from datetime import datetime, timedelta
import json

# Import tool modules
from .tools.player_tools import PlayerTools
from .tools.team_tools import TeamTools
from .tools.match_tools import MatchTools
from .tools.analysis_tools import AnalysisTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrazilianSoccerMCPServer:
    """Main MCP server for Brazilian Soccer Knowledge Graph"""

    def __init__(self):
        self.server = Server("brazilian-soccer-kg")
        self.driver = None
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)

        # Tool modules
        self.player_tools = None
        self.team_tools = None
        self.match_tools = None
        self.analysis_tools = None

        # Register handlers
        self.setup_handlers()

    async def connect_to_neo4j(self):
        """Connect to Neo4j database"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "neo4j123")
            )

            # Test connection
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.consume()

            logger.info("Successfully connected to Neo4j")

            # Initialize tool modules
            self.player_tools = PlayerTools(self.driver, self.cache)
            self.team_tools = TeamTools(self.driver, self.cache)
            self.match_tools = MatchTools(self.driver, self.cache)
            self.analysis_tools = AnalysisTools(self.driver, self.cache)

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self):
        """Close database connections"""
        if self.driver:
            await self.driver.close()

    def setup_handlers(self):
        """Setup MCP handlers"""

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="brazilian-soccer://help",
                    name="Help and Documentation",
                    description="Complete guide for using the Brazilian Soccer Knowledge Graph",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="brazilian-soccer://schema",
                    name="Database Schema",
                    description="Neo4j graph database schema documentation",
                    mimeType="application/json"
                )
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "brazilian-soccer://help":
                return self._get_help_content()
            elif uri == "brazilian-soccer://schema":
                return await self._get_schema_info()
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools"""
            tools = []

            # Player tools
            tools.extend([
                Tool(
                    name="search_player",
                    description="Search for players by name or partial name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Player name or partial name"},
                            "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="get_player_stats",
                    description="Get detailed statistics for a specific player",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "player_name": {"type": "string", "description": "Full player name"},
                            "season": {"type": "string", "description": "Season year (optional)"}
                        },
                        "required": ["player_name"]
                    }
                ),
                Tool(
                    name="get_player_career",
                    description="Get career history and teams for a player",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "player_name": {"type": "string", "description": "Full player name"}
                        },
                        "required": ["player_name"]
                    }
                )
            ])

            # Team tools
            tools.extend([
                Tool(
                    name="search_team",
                    description="Search for teams by name or partial name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Team name or partial name"},
                            "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="get_team_roster",
                    description="Get current roster for a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_name": {"type": "string", "description": "Full team name"},
                            "season": {"type": "string", "description": "Season year (optional)"}
                        },
                        "required": ["team_name"]
                    }
                ),
                Tool(
                    name="get_team_stats",
                    description="Get statistics and performance data for a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_name": {"type": "string", "description": "Full team name"},
                            "competition": {"type": "string", "description": "Competition name (optional)"}
                        },
                        "required": ["team_name"]
                    }
                )
            ])

            # Match tools
            tools.extend([
                Tool(
                    name="get_match_details",
                    description="Get detailed information about a specific match",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "match_id": {"type": "string", "description": "Match ID"},
                            "team1": {"type": "string", "description": "First team name (alternative)"},
                            "team2": {"type": "string", "description": "Second team name (alternative)"},
                            "date": {"type": "string", "description": "Match date (YYYY-MM-DD, alternative)"}
                        }
                    }
                ),
                Tool(
                    name="search_matches",
                    description="Search for matches by teams, date range, or competition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team": {"type": "string", "description": "Team name (optional)"},
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD, optional)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD, optional)"},
                            "competition": {"type": "string", "description": "Competition name (optional)"},
                            "limit": {"type": "integer", "description": "Maximum results", "default": 20}
                        }
                    }
                ),
                Tool(
                    name="get_head_to_head",
                    description="Get head-to-head statistics between two teams",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team1": {"type": "string", "description": "First team name"},
                            "team2": {"type": "string", "description": "Second team name"},
                            "competition": {"type": "string", "description": "Competition name (optional)"}
                        },
                        "required": ["team1", "team2"]
                    }
                )
            ])

            # Competition tools
            tools.extend([
                Tool(
                    name="get_competition_standings",
                    description="Get current standings for a competition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "competition": {"type": "string", "description": "Competition name"},
                            "season": {"type": "string", "description": "Season year (optional)"}
                        },
                        "required": ["competition"]
                    }
                ),
                Tool(
                    name="get_competition_top_scorers",
                    description="Get top scorers for a competition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "competition": {"type": "string", "description": "Competition name"},
                            "season": {"type": "string", "description": "Season year (optional)"},
                            "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                        },
                        "required": ["competition"]
                    }
                )
            ])

            # Analysis tools
            tools.extend([
                Tool(
                    name="find_common_teammates",
                    description="Find players who were teammates with specific players",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "players": {"type": "array", "items": {"type": "string"}, "description": "List of player names"},
                            "team": {"type": "string", "description": "Specific team (optional)"}
                        },
                        "required": ["players"]
                    }
                ),
                Tool(
                    name="get_rivalry_stats",
                    description="Get detailed rivalry statistics and history",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team1": {"type": "string", "description": "First team name"},
                            "team2": {"type": "string", "description": "Second team name"},
                            "years": {"type": "integer", "description": "Number of years to analyze", "default": 10}
                        },
                        "required": ["team1", "team2"]
                    }
                )
            ])

            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if not self.driver:
                    await self.connect_to_neo4j()

                # Player tools
                if name == "search_player":
                    result = await self.player_tools.search_player(**arguments)
                elif name == "get_player_stats":
                    result = await self.player_tools.get_player_stats(**arguments)
                elif name == "get_player_career":
                    result = await self.player_tools.get_player_career(**arguments)

                # Team tools
                elif name == "search_team":
                    result = await self.team_tools.search_team(**arguments)
                elif name == "get_team_roster":
                    result = await self.team_tools.get_team_roster(**arguments)
                elif name == "get_team_stats":
                    result = await self.team_tools.get_team_stats(**arguments)

                # Match tools
                elif name == "get_match_details":
                    result = await self.match_tools.get_match_details(**arguments)
                elif name == "search_matches":
                    result = await self.match_tools.search_matches(**arguments)
                elif name == "get_head_to_head":
                    result = await self.match_tools.get_head_to_head(**arguments)

                # Competition tools
                elif name == "get_competition_standings":
                    result = await self.match_tools.get_competition_standings(**arguments)
                elif name == "get_competition_top_scorers":
                    result = await self.match_tools.get_competition_top_scorers(**arguments)

                # Analysis tools
                elif name == "find_common_teammates":
                    result = await self.analysis_tools.find_common_teammates(**arguments)
                elif name == "get_rivalry_stats":
                    result = await self.analysis_tools.get_rivalry_stats(**arguments)

                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]

            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    def _get_help_content(self) -> str:
        """Get help documentation"""
        return """
Brazilian Soccer Knowledge Graph - MCP Server

AVAILABLE TOOLS:

PLAYER TOOLS:
- search_player: Search for players by name
- get_player_stats: Get detailed player statistics
- get_player_career: Get player career history

TEAM TOOLS:
- search_team: Search for teams by name
- get_team_roster: Get team roster/squad
- get_team_stats: Get team statistics

MATCH TOOLS:
- get_match_details: Get specific match information
- search_matches: Search matches by criteria
- get_head_to_head: Compare two teams

COMPETITION TOOLS:
- get_competition_standings: Get league tables
- get_competition_top_scorers: Get top scorers

ANALYSIS TOOLS:
- find_common_teammates: Find shared teammates
- get_rivalry_stats: Analyze team rivalries

EXAMPLE QUERIES:
1. "Search for Pelé" → search_player(name="Pelé")
2. "Get Santos roster" → get_team_roster(team_name="Santos")
3. "Flamengo vs Palmeiras" → get_head_to_head(team1="Flamengo", team2="Palmeiras")
"""

    async def _get_schema_info(self) -> str:
        """Get database schema information"""
        schema = {
            "nodes": {
                "Player": ["name", "position", "birth_date", "nationality"],
                "Team": ["name", "city", "founded", "stadium"],
                "Match": ["date", "score", "competition", "venue"],
                "Competition": ["name", "season", "type", "country"]
            },
            "relationships": {
                "PLAYS_FOR": "Player → Team",
                "PLAYED_IN": "Player → Match",
                "PARTICIPATED_IN": "Team → Match",
                "PART_OF": "Match → Competition"
            }
        }
        return json.dumps(schema, indent=2)

# Main server instance
server_instance = BrazilianSoccerMCPServer()

async def main():
    """Main server entry point"""
    # Use stdin/stdout for MCP communication
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.connect_to_neo4j()
        try:
            await server_instance.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="brazilian-soccer-kg",
                    server_version="1.0.0",
                    capabilities=server_instance.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
        finally:
            await server_instance.close()

if __name__ == "__main__":
    asyncio.run(main())