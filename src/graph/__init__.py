"""
Brazilian Soccer MCP Knowledge Graph - Graph Database Module

This module provides Neo4j integration and graph database operations for the Brazilian Soccer Knowledge Graph.
It includes schema management, query builders, and graph algorithms.

Context Block:
- Purpose: Neo4j integration and graph database operations
- Scope: Database connection, schema management, CRUD operations, graph algorithms
- Schema: Players, Teams, Matches, Competitions, Stadiums, Coaches with relationships
- Features: Query optimization, transaction management, bulk operations, graph analytics
"""

__version__ = "1.0.0"
__author__ = "Brazilian Soccer Knowledge Graph Team"
__description__ = "Neo4j integration and graph operations for Brazilian soccer data"

from .database import Neo4jDatabase
# Create an alias for backwards compatibility
Neo4jConnection = Neo4jDatabase
from .models import (
    GraphEntity,
    Player, Team, Match, Stadium, Competition, Season, Coach,
    Goal, Card, Transfer,
    GraphSchema,
    PlayerPosition, MatchResult, CardType,
    ENTITY_TYPES
)

__all__ = [
    "Neo4jConnection",
    "GraphEntity",
    "Player", "Team", "Match", "Stadium", "Competition", "Season", "Coach",
    "Goal", "Card", "Transfer",
    "GraphSchema",
    "PlayerPosition", "MatchResult", "CardType",
    "ENTITY_TYPES"
]