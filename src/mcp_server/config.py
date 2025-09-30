"""
Brazilian Soccer MCP Knowledge Graph - Configuration

CONTEXT:
This module contains configuration settings for the Brazilian Soccer Knowledge Graph
MCP server. It manages database connections, caching settings, and tool configurations.

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

import os
from typing import Dict, Any
from datetime import timedelta

class Config:
    """Configuration class for MCP server"""

    # Database Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'neo4j123')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')

    # MCP Server Configuration
    SERVER_NAME = 'brazilian-soccer-kg'
    SERVER_VERSION = '1.0.0'
    SERVER_DESCRIPTION = 'Brazilian Soccer Knowledge Graph MCP Server'

    # Caching Configuration
    CACHE_TTL_MINUTES = int(os.getenv('CACHE_TTL_MINUTES', '30'))
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '1000'))
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'

    # Query Limits
    DEFAULT_SEARCH_LIMIT = 10
    MAX_SEARCH_LIMIT = 100
    DEFAULT_MATCH_LIMIT = 20
    MAX_MATCH_LIMIT = 200

    # Performance Settings
    QUERY_TIMEOUT_SECONDS = int(os.getenv('QUERY_TIMEOUT_SECONDS', '30'))
    CONNECTION_POOL_SIZE = int(os.getenv('CONNECTION_POOL_SIZE', '10'))

    # Tool Configuration
    TOOLS_CONFIG = {
        'player_tools': {
            'enabled': True,
            'cache_ttl': timedelta(minutes=CACHE_TTL_MINUTES),
            'max_results': MAX_SEARCH_LIMIT
        },
        'team_tools': {
            'enabled': True,
            'cache_ttl': timedelta(minutes=CACHE_TTL_MINUTES),
            'max_results': MAX_SEARCH_LIMIT
        },
        'match_tools': {
            'enabled': True,
            'cache_ttl': timedelta(minutes=CACHE_TTL_MINUTES),
            'max_results': MAX_MATCH_LIMIT
        },
        'analysis_tools': {
            'enabled': True,
            'cache_ttl': timedelta(minutes=CACHE_TTL_MINUTES * 2),  # Longer cache for complex analysis
            'max_results': MAX_SEARCH_LIMIT
        }
    }

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @classmethod
    def get_neo4j_config(cls) -> Dict[str, Any]:
        """Get Neo4j connection configuration"""
        return {
            'uri': cls.NEO4J_URI,
            'auth': (cls.NEO4J_USER, cls.NEO4J_PASSWORD),
            'database': cls.NEO4J_DATABASE,
            'max_connection_pool_size': cls.CONNECTION_POOL_SIZE,
            'connection_timeout': cls.QUERY_TIMEOUT_SECONDS,
            'max_transaction_retry_time': cls.QUERY_TIMEOUT_SECONDS
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get caching configuration"""
        return {
            'enabled': cls.ENABLE_CACHING,
            'ttl': timedelta(minutes=cls.CACHE_TTL_MINUTES),
            'max_size': cls.CACHE_MAX_SIZE
        }

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        required_vars = [
            'NEO4J_URI',
            'NEO4J_USER',
            'NEO4J_PASSWORD'
        ]

        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required configuration variable {var} is not set")

        if cls.CACHE_TTL_MINUTES <= 0:
            raise ValueError("CACHE_TTL_MINUTES must be positive")

        if cls.QUERY_TIMEOUT_SECONDS <= 0:
            raise ValueError("QUERY_TIMEOUT_SECONDS must be positive")

        return True

# Demo Questions Configuration
DEMO_QUESTIONS = [
    {
        "id": 1,
        "question": "Who is Pelé?",
        "tool": "search_player",
        "params": {"name": "Pelé"},
        "expected_fields": ["name", "position", "nationality"]
    },
    {
        "id": 2,
        "question": "What teams did Ronaldinho play for?",
        "tool": "get_player_career",
        "params": {"player_name": "Ronaldinho"},
        "expected_fields": ["career_history", "teams"]
    },
    {
        "id": 3,
        "question": "Show me Santos roster",
        "tool": "get_team_roster",
        "params": {"team_name": "Santos"},
        "expected_fields": ["roster", "total_players"]
    },
    {
        "id": 4,
        "question": "Head to head between Flamengo and Palmeiras",
        "tool": "get_head_to_head",
        "params": {"team1": "Flamengo", "team2": "Palmeiras"},
        "expected_fields": ["overall_record", "recent_form"]
    },
    {
        "id": 5,
        "question": "Brasileirão standings",
        "tool": "get_competition_standings",
        "params": {"competition": "Brasileirão"},
        "expected_fields": ["standings", "competition"]
    }
]

# Tool Help Text
TOOL_HELP = {
    "search_player": "Search for players by name or partial name. Returns player info and current teams.",
    "get_player_stats": "Get detailed statistics for a specific player including goals, assists, matches played.",
    "get_player_career": "Get complete career history showing all teams, transfers, and achievements.",
    "search_team": "Search for teams by name or partial name. Returns team info and current player count.",
    "get_team_roster": "Get current roster/squad for a team with player details and positions.",
    "get_team_stats": "Get team statistics including wins, losses, goals, and recent form.",
    "get_match_details": "Get detailed information about a specific match including lineups and events.",
    "search_matches": "Search for matches by team, date range, or competition with flexible filters.",
    "get_head_to_head": "Compare two teams with historical record, goals, and match details.",
    "get_competition_standings": "Get current league table/standings for a competition.",
    "get_competition_top_scorers": "Get top goal scorers in a competition with stats and rankings.",
    "find_common_teammates": "Find players who were teammates with specified players at any point.",
    "get_rivalry_stats": "Get comprehensive rivalry analysis between two teams over specified years."
}