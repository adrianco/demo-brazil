"""
Brazilian Soccer MCP Knowledge Graph - Tools Package

CONTEXT:
This package contains all MCP tools for the Brazilian Soccer Knowledge Graph
MCP server. It provides organized tool modules for different types of soccer data queries.

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

from .player_tools import PlayerTools
from .team_tools import TeamTools
from .match_tools import MatchTools
from .analysis_tools import AnalysisTools

__all__ = [
    'PlayerTools',
    'TeamTools',
    'MatchTools',
    'AnalysisTools'
]