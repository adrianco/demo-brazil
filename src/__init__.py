"""
Brazilian Soccer MCP Knowledge Graph

CONTEXT:
Main package initialization for the Brazilian Soccer MCP Knowledge Graph project.
This module provides the entry point and exposes the main components for building
and querying a comprehensive graph database of Brazilian soccer data.

PHASE: 1 (Core Data)
COMPONENT: Package Initialization
DEPENDENCIES: All submodules

ARCHITECTURE:
The package is organized into several key modules:

- graph/: Neo4j database connection and schema models
- data_pipeline/: Data loading and graph building components
- utils/: Utility functions for data processing
- mcp_server/: MCP server implementation (future phases)

PUBLIC API:
The package exposes the most commonly used classes and functions:
- Neo4jConnection: Database connection management
- GraphBuilder: Main graph construction interface
- KaggleLoader: Data loading from Kaggle datasets
- GraphSchema: Schema management and validation

USAGE:
```python
from src import Neo4jConnection, GraphBuilder, KaggleLoader

# Initialize components
db = Neo4jConnection()
loader = KaggleLoader()
builder = GraphBuilder(db)

# Build the complete graph
stats = builder.build_complete_graph()
```

This package forms the foundation for the Brazilian Soccer MCP Knowledge Graph,
enabling comprehensive analysis of Brazilian soccer data through graph queries
and providing a structured approach to soccer data management.
"""

from .graph.database import Neo4jConnection
from .graph.models import (
    Player, Team, Match, Stadium, Competition, Season, Coach,
    Goal, Card, Transfer, GraphSchema, PlayerPosition, MatchResult, CardType
)
from .data_pipeline.kaggle_loader import KaggleLoader
from .data_pipeline.graph_builder import GraphBuilder
from .utils.data_utils import (
    normalize_text, normalize_team_name, normalize_player_name,
    parse_date, safe_int, safe_float, safe_bool
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Brazilian Soccer MCP Knowledge Graph Team"
__description__ = "A comprehensive knowledge graph for Brazilian soccer data"

# Export main classes
__all__ = [
    # Core database and schema
    "Neo4jConnection",
    "GraphSchema",

    # Entity models
    "Player",
    "Team",
    "Match",
    "Stadium",
    "Competition",
    "Season",
    "Coach",
    "Goal",
    "Card",
    "Transfer",

    # Enums
    "PlayerPosition",
    "MatchResult",
    "CardType",

    # Data pipeline
    "KaggleLoader",
    "GraphBuilder",

    # Utilities
    "normalize_text",
    "normalize_team_name",
    "normalize_player_name",
    "parse_date",
    "safe_int",
    "safe_float",
    "safe_bool"
]

# Package-level configuration
DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USERNAME = "neo4j"
DEFAULT_NEO4J_PASSWORD = "neo4j123"

# Logging configuration
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())