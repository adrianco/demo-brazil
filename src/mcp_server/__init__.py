"""
Brazilian Soccer MCP Knowledge Graph - MCP Server Package

CONTEXT:
This package contains the complete MCP server implementation for the Brazilian Soccer
Knowledge Graph. It provides a comprehensive API for querying Brazilian soccer data
through Model Context Protocol (MCP) tools.

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

from .server import BrazilianSoccerMCPServer, main

__all__ = [
    'BrazilianSoccerMCPServer',
    'main'
]

__version__ = "1.0.0"