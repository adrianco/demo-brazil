#!/usr/bin/env python3
"""
Brazilian Soccer MCP Knowledge Graph - Server Runner

CONTEXT:
This script provides the entry point for running the Brazilian Soccer Knowledge Graph
MCP server. It handles command-line arguments, configuration, and server initialization.

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
import argparse
import logging
import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from mcp_server import main, BrazilianSoccerMCPServer

def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import neo4j
        import mcp
        return True
    except ImportError as e:
        print(f"Missing required dependency: {e}", file=sys.stderr)
        print("Please install with: pip install neo4j mcp", file=sys.stderr)
        return False

def main_cli():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Brazilian Soccer Knowledge Graph MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mcp_server.py                    # Run server with stdio
  python run_mcp_server.py --debug            # Run with debug logging
  python run_mcp_server.py --check            # Check configuration

The server provides MCP tools for querying Brazilian soccer data:
- Player tools: search_player, get_player_stats, get_player_career
- Team tools: search_team, get_team_roster, get_team_stats
- Match tools: get_match_details, search_matches, get_head_to_head
- Competition tools: get_competition_standings, get_competition_top_scorers
- Analysis tools: find_common_teammates, get_rivalry_stats
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check configuration and dependencies'
    )

    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test Neo4j database connection'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    if args.check:
        logger.info("Configuration check:")
        logger.info("- Dependencies: OK")
        logger.info("- Neo4j URL: bolt://localhost:7687")
        logger.info("- MCP Protocol: stdio")
        logger.info("Configuration check completed successfully")
        return

    if args.test_connection:
        async def test_connection():
            server = BrazilianSoccerMCPServer()
            try:
                await server.connect_to_neo4j()
                logger.info("✓ Neo4j connection successful")
                await server.close()
                return True
            except Exception as e:
                logger.error(f"✗ Neo4j connection failed: {e}")
                await server.close()
                return False

        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)

    # Run the server
    logger.info("Starting Brazilian Soccer Knowledge Graph MCP Server...")
    logger.info("Available tools: search_player, get_player_stats, get_player_career, search_team, get_team_roster, get_team_stats, get_match_details, search_matches, get_head_to_head, get_competition_standings, get_competition_top_scorers, find_common_teammates, get_rivalry_stats")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_cli()