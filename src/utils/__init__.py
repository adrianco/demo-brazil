"""
Brazilian Soccer MCP Knowledge Graph - Utilities Package

CONTEXT:
Utilities package initialization for the Brazilian Soccer MCP Knowledge Graph.
This module exposes commonly used utility functions for data processing,
cleaning, and normalization across the entire project.

PHASE: 1 (Core Data)
COMPONENT: Utilities Package
DEPENDENCIES: data_utils module

The utilities package provides essential data processing functions that are
used throughout the graph construction pipeline, ensuring consistent data
quality and standardization across all components.
"""

from .data_utils import (
    normalize_text,
    normalize_team_name,
    normalize_brazilian_name,
    parse_date,
    safe_int,
    safe_float,
    safe_decimal,
    generate_id,
    validate_brazilian_name,
    validate_team_name,
    validate_score,
    clean_dict,
    format_brazilian_currency,
    extract_numbers_from_text,
    is_valid_year,
    normalize_position,
    BRAZILIAN_STATES,
    PLAYER_POSITIONS
)

__all__ = [
    "normalize_text",
    "normalize_team_name",
    "normalize_brazilian_name",
    "parse_date",
    "safe_int",
    "safe_float",
    "safe_decimal",
    "generate_id",
    "validate_brazilian_name",
    "validate_team_name",
    "validate_score",
    "clean_dict",
    "format_brazilian_currency",
    "extract_numbers_from_text",
    "is_valid_year",
    "normalize_position",
    "BRAZILIAN_STATES",
    "PLAYER_POSITIONS"
]