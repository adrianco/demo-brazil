#!/usr/bin/env python3
"""
Test MCP server using stdio protocol - simulating what Claude Desktop does
"""

import json
import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_mcp_stdio():
    """Test MCP server via stdio protocol."""

    # Import the server
    from src.mcp_server.server import BrazilianSoccerMCPServer

    # Create server instance
    server = BrazilianSoccerMCPServer()

    # Connect to Neo4j
    await server.connect_to_neo4j()

    print("✅ Connected to Neo4j")

    # Test player search directly
    if server.player_tools:
        result = await server.player_tools.search_player(name="Pelé")
        print(f"\n🔍 Search for Pelé:")
        print(json.dumps(result, indent=2))

        result = await server.player_tools.search_player(name="Neymar")
        print(f"\n🔍 Search for Neymar:")
        print(json.dumps(result, indent=2))

    # Test team search
    if server.team_tools:
        result = await server.team_tools.search_team(name="Flamengo")
        print(f"\n🔍 Search for Flamengo:")
        print(json.dumps(result, indent=2))

        result = await server.team_tools.search_team(name="Santos")
        print(f"\n🔍 Search for Santos:")
        print(json.dumps(result, indent=2))

    # Close connection
    await server.close()

    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_stdio())