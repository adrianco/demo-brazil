#!/usr/bin/env python3
"""
Brazilian Soccer MCP Knowledge Graph - HTTP Server Wrapper

CONTEXT:
This module provides an HTTP wrapper around the MCP server for testing purposes.
It converts HTTP requests to MCP protocol and handles responses.

PHASE: 3 - Integration & Testing
PURPOSE: HTTP interface for MCP server testing
DATA SOURCES: Neo4j database via MCP server
DEPENDENCIES: aiohttp, mcp_server

TECHNICAL DETAILS:
- HTTP Server: http://localhost:3000
- Converts JSON-RPC over HTTP to MCP protocol
- Wraps MCP server for testing
"""

import asyncio
import json
import logging
from aiohttp import web
from typing import Dict, Any
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mcp_server.server import BrazilianSoccerMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPMCPBridge:
    """HTTP to MCP bridge for testing."""

    def __init__(self):
        self.mcp_server = BrazilianSoccerMCPServer()
        self.initialized = False

    async def initialize(self):
        """Initialize MCP server connection."""
        if not self.initialized:
            await self.mcp_server.connect_to_neo4j()
            self.initialized = True
            logger.info("MCP server initialized with Neo4j connection")

    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle HTTP request and convert to MCP call."""
        try:
            # Parse JSON-RPC request
            data = await request.json()

            method = data.get("method", "")
            params = data.get("params", {})
            request_id = data.get("id", 1)

            logger.info(f"Received request: {method}")

            # Extract tool name from method (e.g., "tools/search_player" -> "search_player")
            if method.startswith("tools/"):
                tool_name = method[6:]  # Remove "tools/" prefix
            else:
                tool_name = method

            # Handle different tool names
            result = None

            if tool_name == "test_connection":
                result = {
                    "status": "connected",
                    "server": "brazilian-soccer-kg",
                    "version": "1.0.0"
                }
            elif tool_name == "search_player":
                if self.mcp_server.player_tools:
                    result = await self.mcp_server.player_tools.search_player(**params)
                else:
                    result = {"error": "Player tools not initialized"}
            elif tool_name == "get_player_stats":
                if self.mcp_server.player_tools:
                    # Convert player_id to player_name if needed
                    if "player_id" in params:
                        params["player_name"] = params.pop("player_id")
                    result = await self.mcp_server.player_tools.get_player_stats(**params)
                else:
                    result = {"error": "Player tools not initialized"}
            elif tool_name == "search_players_by_position":
                if self.mcp_server.player_tools:
                    result = await self.mcp_server.player_tools.search_players_by_position(**params)
                else:
                    result = {"error": "Player tools not initialized"}
            elif tool_name == "get_player_career":
                if self.mcp_server.player_tools:
                    # Convert player_id to player_name if needed
                    if "player_id" in params:
                        params["player_name"] = params.pop("player_id")
                    result = await self.mcp_server.player_tools.get_player_career(**params)
                else:
                    result = {"error": "Player tools not initialized"}
            elif tool_name == "compare_players":
                if self.mcp_server.player_tools:
                    result = await self.mcp_server.player_tools.compare_players(**params)
                else:
                    result = {"error": "Player tools not initialized"}
            elif tool_name == "search_team":
                if self.mcp_server.team_tools:
                    result = await self.mcp_server.team_tools.search_team(**params)
                else:
                    result = {"error": "Team tools not initialized"}
            elif tool_name == "get_team_stats":
                if self.mcp_server.team_tools:
                    # Convert team_id to team_name if needed
                    if "team_id" in params:
                        params["team_name"] = params.pop("team_id")
                    result = await self.mcp_server.team_tools.get_team_stats(**params)
                else:
                    result = {"error": "Team tools not initialized"}
            elif tool_name == "get_team_roster":
                if self.mcp_server.team_tools:
                    # Convert team_id to team_name if needed
                    if "team_id" in params:
                        params["team_name"] = params.pop("team_id")
                    result = await self.mcp_server.team_tools.get_team_roster(**params)
                else:
                    result = {"error": "Team tools not initialized"}
            elif tool_name == "search_teams_by_league":
                if self.mcp_server.team_tools:
                    result = await self.mcp_server.team_tools.search_teams_by_league(**params)
                else:
                    result = {"error": "Team tools not initialized"}
            elif tool_name == "compare_teams":
                if self.mcp_server.team_tools:
                    result = await self.mcp_server.team_tools.compare_teams(**params)
                else:
                    result = {"error": "Team tools not initialized"}
            elif tool_name == "get_match_details":
                if self.mcp_server.match_tools:
                    result = await self.mcp_server.match_tools.get_match_details(**params)
                else:
                    result = {"error": "Match tools not initialized"}
            elif tool_name == "search_matches_by_date":
                if self.mcp_server.match_tools:
                    result = await self.mcp_server.match_tools.search_matches_by_date(**params)
                else:
                    result = {"error": "Match tools not initialized"}
            elif tool_name == "get_competition_info":
                if self.mcp_server.match_tools:
                    result = await self.mcp_server.match_tools.get_competition_info(**params)
                else:
                    result = {"error": "Match tools not initialized"}
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {tool_name}"
                    }
                })

            # Return JSON-RPC response
            return web.json_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": 0,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }, status=400)

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": data.get("id", 0) if 'data' in locals() else 0,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }, status=500)

    async def handle_mcp(self, request: web.Request) -> web.Response:
        """Handle MCP endpoint."""
        return await self.handle_request(request)

    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "server": "brazilian-soccer-kg"})


async def create_app():
    """Create aiohttp application."""
    bridge = HTTPMCPBridge()
    await bridge.initialize()

    app = web.Application()

    # Add routes
    app.router.add_post('/mcp', bridge.handle_mcp)
    app.router.add_get('/health', bridge.handle_health)

    # Add CORS headers
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        return middleware_handler

    app.middlewares.append(cors_middleware)

    return app


def main():
    """Run HTTP server."""
    logger.info("Starting Brazilian Soccer MCP HTTP Server on http://localhost:3000")
    app = asyncio.run(create_app())
    web.run_app(app, host='0.0.0.0', port=3000)


if __name__ == "__main__":
    main()