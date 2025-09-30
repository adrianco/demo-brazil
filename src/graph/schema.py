"""
Brazilian Soccer MCP Knowledge Graph - Neo4j Schema Definition

This module defines the complete Neo4j graph schema for Brazilian soccer data including
nodes, relationships, constraints, and indexes for optimal performance.

Context Block:
- Purpose: Define Neo4j graph database schema for Brazilian soccer domain
- Entities: Player, Team, Match, Competition, Stadium, Coach, Season
- Relationships: All soccer-specific relationships with proper cardinalities
- Constraints: Unique constraints and data integrity rules
- Indexes: Performance optimization indexes for common queries
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class NodeLabel(Enum):
    """Enumeration of all node labels in the graph schema."""
    PLAYER = "Player"
    TEAM = "Team"
    MATCH = "Match"
    COMPETITION = "Competition"
    STADIUM = "Stadium"
    COACH = "Coach"
    SEASON = "Season"
    TRANSFER = "Transfer"
    GOAL = "Goal"
    CARD = "Card"


class RelationshipType(Enum):
    """Enumeration of all relationship types in the graph schema."""
    PLAYS_FOR = "PLAYS_FOR"
    PLAYED_IN = "PLAYED_IN"
    HOSTED_AT = "HOSTED_AT"
    COACHED_BY = "COACHED_BY"
    COMPETES_IN = "COMPETES_IN"
    SCORED_IN = "SCORED_IN"
    ASSISTS_IN = "ASSISTS_IN"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    TRANSFERRED_FROM = "TRANSFERRED_FROM"
    RECEIVED_CARD = "RECEIVED_CARD"
    HOME_TEAM = "HOME_TEAM"
    AWAY_TEAM = "AWAY_TEAM"
    PART_OF_SEASON = "PART_OF_SEASON"
    MANAGES_TEAM = "MANAGES_TEAM"
    SUBSTITUTED_IN = "SUBSTITUTED_IN"
    SUBSTITUTED_OUT = "SUBSTITUTED_OUT"


@dataclass
class NodeSchema:
    """Schema definition for a node type."""
    label: str
    properties: Dict[str, str]
    required_properties: List[str]
    unique_properties: List[str]
    indexed_properties: List[str]


@dataclass
class RelationshipSchema:
    """Schema definition for a relationship type."""
    type: str
    start_node: str
    end_node: str
    properties: Dict[str, str]
    required_properties: List[str]


class GraphSchema:
    """Complete Neo4j graph schema for Brazilian Soccer Knowledge Graph."""

    def __init__(self):
        self.nodes = self._define_nodes()
        self.relationships = self._define_relationships()
        self.constraints = self._define_constraints()
        self.indexes = self._define_indexes()

    def _define_nodes(self) -> Dict[str, NodeSchema]:
        """Define all node schemas in the graph."""
        return {
            "Player": NodeSchema(
                label="Player",
                properties={
                    "player_id": "STRING",
                    "name": "STRING",
                    "full_name": "STRING",
                    "birth_date": "DATE",
                    "nationality": "STRING",
                    "position": "STRING",
                    "height": "FLOAT",
                    "weight": "FLOAT",
                    "preferred_foot": "STRING",
                    "market_value": "INTEGER",
                    "jersey_number": "INTEGER",
                    "status": "STRING",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["player_id", "name", "position"],
                unique_properties=["player_id"],
                indexed_properties=["name", "position", "nationality"]
            ),

            "Team": NodeSchema(
                label="Team",
                properties={
                    "team_id": "STRING",
                    "name": "STRING",
                    "short_name": "STRING",
                    "founded": "INTEGER",
                    "city": "STRING",
                    "state": "STRING",
                    "country": "STRING",
                    "logo_url": "STRING",
                    "stadium_capacity": "INTEGER",
                    "colors": "LIST",
                    "website": "STRING",
                    "social_media": "MAP",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["team_id", "name"],
                unique_properties=["team_id"],
                indexed_properties=["name", "city", "state"]
            ),

            "Match": NodeSchema(
                label="Match",
                properties={
                    "match_id": "STRING",
                    "date": "DATETIME",
                    "round": "INTEGER",
                    "home_score": "INTEGER",
                    "away_score": "INTEGER",
                    "status": "STRING",
                    "attendance": "INTEGER",
                    "referee": "STRING",
                    "weather": "STRING",
                    "duration": "INTEGER",
                    "extra_time": "BOOLEAN",
                    "penalties": "BOOLEAN",
                    "home_penalties": "INTEGER",
                    "away_penalties": "INTEGER",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["match_id", "date"],
                unique_properties=["match_id"],
                indexed_properties=["date", "round", "status"]
            ),

            "Competition": NodeSchema(
                label="Competition",
                properties={
                    "competition_id": "STRING",
                    "name": "STRING",
                    "short_name": "STRING",
                    "type": "STRING",
                    "level": "INTEGER",
                    "country": "STRING",
                    "start_date": "DATE",
                    "end_date": "DATE",
                    "format": "STRING",
                    "prize_money": "INTEGER",
                    "sponsor": "STRING",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["competition_id", "name", "type"],
                unique_properties=["competition_id"],
                indexed_properties=["name", "type", "level"]
            ),

            "Stadium": NodeSchema(
                label="Stadium",
                properties={
                    "stadium_id": "STRING",
                    "name": "STRING",
                    "capacity": "INTEGER",
                    "city": "STRING",
                    "state": "STRING",
                    "country": "STRING",
                    "latitude": "FLOAT",
                    "longitude": "FLOAT",
                    "opened": "INTEGER",
                    "surface": "STRING",
                    "roof": "BOOLEAN",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["stadium_id", "name"],
                unique_properties=["stadium_id"],
                indexed_properties=["name", "city", "state"]
            ),

            "Coach": NodeSchema(
                label="Coach",
                properties={
                    "coach_id": "STRING",
                    "name": "STRING",
                    "full_name": "STRING",
                    "birth_date": "DATE",
                    "nationality": "STRING",
                    "experience_years": "INTEGER",
                    "licenses": "LIST",
                    "preferred_formation": "STRING",
                    "achievements": "LIST",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["coach_id", "name"],
                unique_properties=["coach_id"],
                indexed_properties=["name", "nationality"]
            ),

            "Season": NodeSchema(
                label="Season",
                properties={
                    "season_id": "STRING",
                    "year": "INTEGER",
                    "start_date": "DATE",
                    "end_date": "DATE",
                    "status": "STRING",
                    "created_at": "DATETIME",
                    "updated_at": "DATETIME"
                },
                required_properties=["season_id", "year"],
                unique_properties=["season_id"],
                indexed_properties=["year", "status"]
            ),

            "Goal": NodeSchema(
                label="Goal",
                properties={
                    "goal_id": "STRING",
                    "minute": "INTEGER",
                    "type": "STRING",
                    "body_part": "STRING",
                    "assist": "BOOLEAN",
                    "own_goal": "BOOLEAN",
                    "penalty": "BOOLEAN",
                    "created_at": "DATETIME"
                },
                required_properties=["goal_id", "minute"],
                unique_properties=["goal_id"],
                indexed_properties=["minute", "type"]
            ),

            "Card": NodeSchema(
                label="Card",
                properties={
                    "card_id": "STRING",
                    "minute": "INTEGER",
                    "type": "STRING",
                    "reason": "STRING",
                    "created_at": "DATETIME"
                },
                required_properties=["card_id", "minute", "type"],
                unique_properties=["card_id"],
                indexed_properties=["minute", "type"]
            )
        }

    def _define_relationships(self) -> Dict[str, RelationshipSchema]:
        """Define all relationship schemas in the graph."""
        return {
            "PLAYS_FOR": RelationshipSchema(
                type="PLAYS_FOR",
                start_node="Player",
                end_node="Team",
                properties={
                    "start_date": "DATE",
                    "end_date": "DATE",
                    "jersey_number": "INTEGER",
                    "position": "STRING",
                    "salary": "INTEGER",
                    "contract_type": "STRING"
                },
                required_properties=["start_date"]
            ),

            "PLAYED_IN": RelationshipSchema(
                type="PLAYED_IN",
                start_node="Player",
                end_node="Match",
                properties={
                    "minutes_played": "INTEGER",
                    "position": "STRING",
                    "starter": "BOOLEAN",
                    "substituted_in": "INTEGER",
                    "substituted_out": "INTEGER",
                    "rating": "FLOAT"
                },
                required_properties=["minutes_played"]
            ),

            "HOSTED_AT": RelationshipSchema(
                type="HOSTED_AT",
                start_node="Match",
                end_node="Stadium",
                properties={
                    "attendance": "INTEGER",
                    "weather": "STRING"
                },
                required_properties=[]
            ),

            "COACHED_BY": RelationshipSchema(
                type="COACHED_BY",
                start_node="Team",
                end_node="Coach",
                properties={
                    "start_date": "DATE",
                    "end_date": "DATE",
                    "contract_type": "STRING",
                    "salary": "INTEGER"
                },
                required_properties=["start_date"]
            ),

            "COMPETES_IN": RelationshipSchema(
                type="COMPETES_IN",
                start_node="Team",
                end_node="Competition",
                properties={
                    "season": "STRING",
                    "final_position": "INTEGER",
                    "points": "INTEGER",
                    "matches_played": "INTEGER",
                    "wins": "INTEGER",
                    "draws": "INTEGER",
                    "losses": "INTEGER",
                    "goals_for": "INTEGER",
                    "goals_against": "INTEGER"
                },
                required_properties=["season"]
            ),

            "SCORED_IN": RelationshipSchema(
                type="SCORED_IN",
                start_node="Player",
                end_node="Goal",
                properties={
                    "assist": "BOOLEAN"
                },
                required_properties=[]
            ),

            "HOME_TEAM": RelationshipSchema(
                type="HOME_TEAM",
                start_node="Match",
                end_node="Team",
                properties={},
                required_properties=[]
            ),

            "AWAY_TEAM": RelationshipSchema(
                type="AWAY_TEAM",
                start_node="Match",
                end_node="Team",
                properties={},
                required_properties=[]
            ),

            "PART_OF_SEASON": RelationshipSchema(
                type="PART_OF_SEASON",
                start_node="Match",
                end_node="Season",
                properties={},
                required_properties=[]
            ),

            "RECEIVED_CARD": RelationshipSchema(
                type="RECEIVED_CARD",
                start_node="Player",
                end_node="Card",
                properties={},
                required_properties=[]
            )
        }

    def _define_constraints(self) -> List[str]:
        """Define uniqueness constraints for the graph."""
        return [
            "CREATE CONSTRAINT player_id_unique IF NOT EXISTS FOR (p:Player) REQUIRE p.player_id IS UNIQUE",
            "CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.team_id IS UNIQUE",
            "CREATE CONSTRAINT match_id_unique IF NOT EXISTS FOR (m:Match) REQUIRE m.match_id IS UNIQUE",
            "CREATE CONSTRAINT competition_id_unique IF NOT EXISTS FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE",
            "CREATE CONSTRAINT stadium_id_unique IF NOT EXISTS FOR (s:Stadium) REQUIRE s.stadium_id IS UNIQUE",
            "CREATE CONSTRAINT coach_id_unique IF NOT EXISTS FOR (co:Coach) REQUIRE co.coach_id IS UNIQUE",
            "CREATE CONSTRAINT season_id_unique IF NOT EXISTS FOR (se:Season) REQUIRE se.season_id IS UNIQUE",
            "CREATE CONSTRAINT goal_id_unique IF NOT EXISTS FOR (g:Goal) REQUIRE g.goal_id IS UNIQUE",
            "CREATE CONSTRAINT card_id_unique IF NOT EXISTS FOR (ca:Card) REQUIRE ca.card_id IS UNIQUE"
        ]

    def _define_indexes(self) -> List[str]:
        """Define indexes for optimal query performance."""
        return [
            # Player indexes
            "CREATE INDEX player_name_index IF NOT EXISTS FOR (p:Player) ON (p.name)",
            "CREATE INDEX player_position_index IF NOT EXISTS FOR (p:Player) ON (p.position)",
            "CREATE INDEX player_nationality_index IF NOT EXISTS FOR (p:Player) ON (p.nationality)",

            # Team indexes
            "CREATE INDEX team_name_index IF NOT EXISTS FOR (t:Team) ON (t.name)",
            "CREATE INDEX team_city_index IF NOT EXISTS FOR (t:Team) ON (t.city)",
            "CREATE INDEX team_state_index IF NOT EXISTS FOR (t:Team) ON (t.state)",

            # Match indexes
            "CREATE INDEX match_date_index IF NOT EXISTS FOR (m:Match) ON (m.date)",
            "CREATE INDEX match_round_index IF NOT EXISTS FOR (m:Match) ON (m.round)",
            "CREATE INDEX match_status_index IF NOT EXISTS FOR (m:Match) ON (m.status)",

            # Competition indexes
            "CREATE INDEX competition_name_index IF NOT EXISTS FOR (c:Competition) ON (c.name)",
            "CREATE INDEX competition_type_index IF NOT EXISTS FOR (c:Competition) ON (c.type)",
            "CREATE INDEX competition_level_index IF NOT EXISTS FOR (c:Competition) ON (c.level)",

            # Stadium indexes
            "CREATE INDEX stadium_name_index IF NOT EXISTS FOR (s:Stadium) ON (s.name)",
            "CREATE INDEX stadium_city_index IF NOT EXISTS FOR (s:Stadium) ON (s.city)",

            # Coach indexes
            "CREATE INDEX coach_name_index IF NOT EXISTS FOR (co:Coach) ON (co.name)",
            "CREATE INDEX coach_nationality_index IF NOT EXISTS FOR (co:Coach) ON (co.nationality)",

            # Season indexes
            "CREATE INDEX season_year_index IF NOT EXISTS FOR (se:Season) ON (se.year)",
            "CREATE INDEX season_status_index IF NOT EXISTS FOR (se:Season) ON (se.status)",

            # Composite indexes for common queries
            "CREATE INDEX match_date_competition IF NOT EXISTS FOR (m:Match) ON (m.date, m.competition_id)",
            "CREATE INDEX player_team_date IF NOT EXISTS FOR ()-[r:PLAYS_FOR]-() ON (r.start_date, r.end_date)"
        ]

    def get_schema_creation_queries(self) -> List[str]:
        """Get all queries needed to create the complete schema."""
        queries = []
        queries.extend(self.constraints)
        queries.extend(self.indexes)
        return queries

    def get_node_properties(self, node_label: str) -> Dict[str, str]:
        """Get properties for a specific node type."""
        if node_label in self.nodes:
            return self.nodes[node_label].properties
        return {}

    def get_relationship_properties(self, relationship_type: str) -> Dict[str, str]:
        """Get properties for a specific relationship type."""
        if relationship_type in self.relationships:
            return self.relationships[relationship_type].properties
        return {}