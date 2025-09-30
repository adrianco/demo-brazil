"""
Brazilian Soccer MCP Knowledge Graph - Data Pipeline Package

CONTEXT:
Data pipeline package initialization for the Brazilian Soccer MCP Knowledge Graph.
This module exposes the core data loading and graph building components for
processing Brazilian soccer data and constructing the knowledge graph.

PHASE: 1 (Core Data)
COMPONENT: Data Pipeline Package
DEPENDENCIES: kaggle_loader, graph_builder modules

The data pipeline package handles the complete data processing workflow from
raw data sources to the final graph database, including data loading,
cleaning, normalization, and graph construction.
"""

from .kaggle_loader import KaggleLoader

# GraphBuilder will be imported separately due to additional dependencies
try:
    from .graph_builder import GraphBuilder
    __all__ = ["KaggleLoader", "GraphBuilder"]
except ImportError:
    # GraphBuilder not available, only expose KaggleLoader
    __all__ = ["KaggleLoader"]