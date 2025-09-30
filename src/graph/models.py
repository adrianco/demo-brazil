"""
Brazilian Soccer MCP Knowledge Graph - Graph Schema Models

CONTEXT:
This module implements the complete graph schema for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying player, team, match, and competition data
stored in a Neo4j graph database.

PHASE: 1 - Core Data
PURPOSE: Graph schema definitions and constraint management for Neo4j entities and relationships
DATA SOURCES: Kaggle Brazilian Football Matches
DEPENDENCIES: neo4j, py2neo

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition, Stadium, Coach nodes with all relationships
- Performance: Optimized constraints and indexes for query performance
- Testing: BDD scenarios for database operations

INTEGRATION:
- MCP Tools: Database backend for all query tools
- Error Handling: Comprehensive exception handling
- Rate Limiting: N/A for local database
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum

from .database import Neo4jDatabase, get_database


class MatchResult(Enum):
    """Match result types."""
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"


class CardType(Enum):
    """Card types in soccer."""
    YELLOW = "YELLOW"
    RED = "RED"


class PlayerPosition(Enum):
    """Player positions."""
    GOALKEEPER = "GK"
    DEFENDER = "DEF"
    MIDFIELDER = "MID"
    FORWARD = "FWD"
    UNKNOWN = "UNK"


class CompetitionType(Enum):
    """Competition types."""
    LEAGUE = "LEAGUE"
    CUP = "CUP"
    INTERNATIONAL = "INTERNATIONAL"
    FRIENDLY = "FRIENDLY"


class TransferType(Enum):
    """Transfer types."""
    PERMANENT = "PERMANENT"
    LOAN = "LOAN"
    FREE = "FREE"
    RETURN = "RETURN"


@dataclass
class GraphEntity:
    """Base class for all graph entities."""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for Neo4j storage."""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, date):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
            elif value is not None:
                data[key] = value
        return data


@dataclass
class Player(GraphEntity):
    """Soccer player entity with comprehensive attributes."""
    name: str = ""
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    position: Optional[PlayerPosition] = None
    preferred_foot: Optional[str] = None  # "left", "right", "both"
    jersey_number: Optional[int] = None
    market_value: Optional[float] = None  # in millions

    # Personal details
    place_of_birth: Optional[str] = None
    passport_country: Optional[str] = None

    # Career statistics
    total_goals: int = 0
    total_assists: int = 0
    total_matches: int = 0
    yellow_cards: int = 0
    red_cards: int = 0

    # Performance metrics
    minutes_played: int = 0
    goals_per_game: float = 0.0
    shots_per_game: float = 0.0
    pass_accuracy: float = 0.0

    # Social/Contract info
    agent: Optional[str] = None
    contract_expires: Optional[date] = None
    social_media_followers: Optional[int] = None


@dataclass
class Team(GraphEntity):
    """Soccer team entity with detailed information."""
    name: str = ""
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    founded_year: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Brazil"
    stadium_name: Optional[str] = None
    team_type: str = "club"  # "club", "national"

    # Team colors and identity
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    nickname: Optional[str] = None

    # Contact and business info
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    # Financial and administrative
    president: Optional[str] = None
    market_value: Optional[float] = None  # in millions
    revenue: Optional[float] = None  # in millions

    # Statistics
    total_matches: int = 0
    total_wins: int = 0
    total_draws: int = 0
    total_losses: int = 0
    total_goals_for: int = 0
    total_goals_against: int = 0

    # League information
    current_league: Optional[str] = None
    league_position: Optional[int] = None
    points: Optional[int] = None


@dataclass
class Stadium(GraphEntity):
    """Stadium entity with detailed venue information."""
    name: str = ""
    city: str = ""
    state: Optional[str] = None
    country: str = "Brazil"
    capacity: Optional[int] = None
    opened_year: Optional[int] = None
    surface: Optional[str] = None  # "grass", "artificial", "hybrid"

    # Location details
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None

    # Stadium features
    has_roof: bool = False
    has_heating: bool = False
    has_video_screen: bool = False
    parking_spaces: Optional[int] = None

    # Administrative
    owner: Optional[str] = None
    cost_built: Optional[float] = None  # in millions
    architect: Optional[str] = None

    # Usage statistics
    total_matches: int = 0
    record_attendance: Optional[int] = None
    average_attendance: Optional[float] = None


@dataclass
class Competition(GraphEntity):
    """Competition/tournament entity with comprehensive details."""
    name: str = ""
    full_name: Optional[str] = None
    type: Optional[CompetitionType] = None
    country: str = "Brazil"
    tier: Optional[int] = None  # 1 for top tier, 2 for second tier, etc.
    format: Optional[str] = None  # "round_robin", "knockout", "group_stage"

    # Competition organization
    organizer: Optional[str] = None
    founded_year: Optional[int] = None
    first_edition: Optional[int] = None
    frequency: Optional[str] = None  # "annual", "biennial"

    # Competition details
    total_teams: Optional[int] = None
    total_rounds: Optional[int] = None
    has_playoffs: bool = False
    promotion_spots: Optional[int] = None
    relegation_spots: Optional[int] = None

    # Prize and prestige
    prize_money: Optional[float] = None  # in millions
    qualification_to: Optional[str] = None  # what this competition qualifies for

    # Media and commercial
    tv_deal_value: Optional[float] = None  # in millions
    sponsor: Optional[str] = None

    # Current season info
    current_season: Optional[str] = None
    current_champion: Optional[str] = None
    most_successful_team: Optional[str] = None
    most_titles_count: Optional[int] = None


@dataclass
class Season(GraphEntity):
    """Season entity with comprehensive season information."""
    name: str = ""
    year: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False

    # Season structure
    total_matchdays: Optional[int] = None
    winter_break_start: Optional[date] = None
    winter_break_end: Optional[date] = None

    # Statistics
    total_goals: int = 0
    total_matches: int = 0
    average_goals_per_match: float = 0.0
    total_cards: int = 0

    # Records
    highest_attendance: Optional[int] = None
    lowest_attendance: Optional[int] = None
    biggest_win_margin: Optional[int] = None


@dataclass
class Coach(GraphEntity):
    """Coach entity with detailed coaching information."""
    name: str = ""
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None

    # Coaching career
    coaching_license: Optional[str] = None
    preferred_formation: Optional[str] = None
    coaching_style: Optional[str] = None

    # Personal details
    playing_career: Optional[str] = None
    languages: Optional[List[str]] = None
    education: Optional[str] = None

    # Coaching statistics
    total_matches: int = 0
    total_wins: int = 0
    total_draws: int = 0
    total_losses: int = 0
    win_percentage: float = 0.0

    # Achievements
    total_trophies: int = 0
    major_trophies: Optional[List[str]] = None

    # Contract and financial
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    salary: Optional[float] = None  # in millions per year


@dataclass
class Match(GraphEntity):
    """Match entity with comprehensive match information."""
    date: Optional[date] = None
    time: Optional[str] = None
    home_team_id: str = ""
    away_team_id: str = ""
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled"  # "scheduled", "live", "finished", "postponed", "cancelled"

    # Match context
    round: Optional[str] = None
    matchday: Optional[int] = None
    season_id: Optional[str] = None
    competition_id: Optional[str] = None
    stadium_id: Optional[str] = None

    # Officials
    referee: Optional[str] = None
    assistant_referee_1: Optional[str] = None
    assistant_referee_2: Optional[str] = None
    fourth_official: Optional[str] = None
    var_referee: Optional[str] = None

    # Match details
    attendance: Optional[int] = None
    weather: Optional[str] = None
    temperature: Optional[float] = None

    # Match statistics
    home_possession: Optional[float] = None
    away_possession: Optional[float] = None
    home_shots: Optional[int] = None
    away_shots: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    home_corners: Optional[int] = None
    away_corners: Optional[int] = None
    home_fouls: Optional[int] = None
    away_fouls: Optional[int] = None
    home_offsides: Optional[int] = None
    away_offsides: Optional[int] = None
    home_yellow_cards: Optional[int] = None
    away_yellow_cards: Optional[int] = None
    home_red_cards: Optional[int] = None
    away_red_cards: Optional[int] = None

    # Advanced statistics
    home_pass_accuracy: Optional[float] = None
    away_pass_accuracy: Optional[float] = None
    home_crosses: Optional[int] = None
    away_crosses: Optional[int] = None
    home_saves: Optional[int] = None
    away_saves: Optional[int] = None

    # Result details
    winner: Optional[str] = None  # "home", "away", "draw"
    margin_of_victory: Optional[int] = None
    comeback: bool = False  # if losing team came back to win/draw


@dataclass
class Goal(GraphEntity):
    """Goal entity with detailed goal information."""
    match_id: str = ""
    player_id: str = ""
    team_id: str = ""
    minute: int = 0
    type: str = "goal"  # "goal", "penalty", "own_goal", "free_kick"
    assist_player_id: Optional[str] = None

    # Goal details
    body_part: Optional[str] = None  # "left_foot", "right_foot", "head", "chest"
    position_x: Optional[float] = None  # field coordinates
    position_y: Optional[float] = None
    distance_from_goal: Optional[float] = None
    angle: Optional[float] = None

    # Context
    situation: Optional[str] = None  # "open_play", "corner", "free_kick", "counter_attack"
    assist_type: Optional[str] = None  # "pass", "cross", "through_ball", "set_piece"
    goalkeeper_id: Optional[str] = None

    # Video and analysis
    video_url: Optional[str] = None
    expected_goals: Optional[float] = None  # xG value

    # Celebration and reaction
    celebration_type: Optional[str] = None
    milestone: Optional[str] = None  # "first_goal", "100th_goal", etc.


@dataclass
class Card(GraphEntity):
    """Card (yellow/red) entity with detailed card information."""
    match_id: str = ""
    player_id: str = ""
    team_id: str = ""
    minute: int = 0
    type: Optional[CardType] = None
    reason: Optional[str] = None

    # Card context
    referee_id: Optional[str] = None
    foul_type: Optional[str] = None
    opponent_player_id: Optional[str] = None

    # Field position
    position_x: Optional[float] = None
    position_y: Optional[float] = None

    # Consequences
    is_second_yellow: bool = False
    resulting_suspension: Optional[int] = None  # games suspended
    fine_amount: Optional[float] = None

    # Video review
    var_reviewed: bool = False
    var_decision: Optional[str] = None


@dataclass
class Transfer(GraphEntity):
    """Player transfer entity with comprehensive transfer details."""
    player_id: str = ""
    from_team_id: Optional[str] = None
    to_team_id: str = ""
    transfer_date: Optional[date] = None
    transfer_fee: Optional[float] = None  # in millions
    contract_duration: Optional[int] = None  # in years
    transfer_type: Optional[TransferType] = None

    # Transfer details
    salary: Optional[float] = None  # annual salary in millions
    signing_bonus: Optional[float] = None
    release_clause: Optional[float] = None
    agent_fee: Optional[float] = None

    # Transfer context
    window: Optional[str] = None  # "summer", "winter", "emergency"
    announcement_date: Optional[date] = None
    medical_completed: bool = False

    # Financial structure
    payment_structure: Optional[str] = None  # "lump_sum", "installments"
    performance_bonuses: Optional[float] = None
    sell_on_percentage: Optional[float] = None

    # Status
    is_official: bool = False
    is_loan_return: bool = False
    contract_signed: bool = False


class GraphSchema:
    """Graph schema manager for creating and managing the database structure."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        """Initialize schema manager with database connection."""
        self.db = db or get_database()

    def create_constraints(self) -> List[str]:
        """
        Create uniqueness constraints for all entity types.

        Returns:
            List of constraint creation results
        """
        constraints = [
            "CREATE CONSTRAINT player_id IF NOT EXISTS FOR (p:Player) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT team_id IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT stadium_id IF NOT EXISTS FOR (s:Stadium) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT competition_id IF NOT EXISTS FOR (c:Competition) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT season_id IF NOT EXISTS FOR (se:Season) REQUIRE se.id IS UNIQUE",
            "CREATE CONSTRAINT coach_id IF NOT EXISTS FOR (co:Coach) REQUIRE co.id IS UNIQUE",
            "CREATE CONSTRAINT match_id IF NOT EXISTS FOR (m:Match) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT goal_id IF NOT EXISTS FOR (g:Goal) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT card_id IF NOT EXISTS FOR (ca:Card) REQUIRE ca.id IS UNIQUE",
            "CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (tr:Transfer) REQUIRE tr.id IS UNIQUE"
        ]

        results = []
        for constraint in constraints:
            try:
                self.db.execute_write_query(constraint)
                results.append(f"✓ {constraint}")
            except Exception as e:
                results.append(f"✗ {constraint}: {str(e)}")

        return results

    def create_indexes(self) -> List[str]:
        """
        Create indexes for better query performance.

        Returns:
            List of index creation results
        """
        indexes = [
            # Player indexes
            "CREATE INDEX player_name IF NOT EXISTS FOR (p:Player) ON (p.name)",
            "CREATE INDEX player_position IF NOT EXISTS FOR (p:Player) ON (p.position)",
            "CREATE INDEX player_nationality IF NOT EXISTS FOR (p:Player) ON (p.nationality)",
            "CREATE INDEX player_birth_date IF NOT EXISTS FOR (p:Player) ON (p.birth_date)",

            # Team indexes
            "CREATE INDEX team_name IF NOT EXISTS FOR (t:Team) ON (t.name)",
            "CREATE INDEX team_city IF NOT EXISTS FOR (t:Team) ON (t.city)",
            "CREATE INDEX team_country IF NOT EXISTS FOR (t:Team) ON (t.country)",
            "CREATE INDEX team_type IF NOT EXISTS FOR (t:Team) ON (t.team_type)",

            # Match indexes
            "CREATE INDEX match_date IF NOT EXISTS FOR (m:Match) ON (m.date)",
            "CREATE INDEX match_status IF NOT EXISTS FOR (m:Match) ON (m.status)",
            "CREATE INDEX match_season IF NOT EXISTS FOR (m:Match) ON (m.season_id)",
            "CREATE INDEX match_competition IF NOT EXISTS FOR (m:Match) ON (m.competition_id)",

            # Competition indexes
            "CREATE INDEX competition_name IF NOT EXISTS FOR (c:Competition) ON (c.name)",
            "CREATE INDEX competition_type IF NOT EXISTS FOR (c:Competition) ON (c.type)",
            "CREATE INDEX competition_country IF NOT EXISTS FOR (c:Competition) ON (c.country)",

            # Goal indexes
            "CREATE INDEX goal_minute IF NOT EXISTS FOR (g:Goal) ON (g.minute)",
            "CREATE INDEX goal_type IF NOT EXISTS FOR (g:Goal) ON (g.type)",
            "CREATE INDEX goal_match IF NOT EXISTS FOR (g:Goal) ON (g.match_id)",
            "CREATE INDEX goal_player IF NOT EXISTS FOR (g:Goal) ON (g.player_id)",

            # Transfer indexes
            "CREATE INDEX transfer_date IF NOT EXISTS FOR (tr:Transfer) ON (tr.transfer_date)",
            "CREATE INDEX transfer_type IF NOT EXISTS FOR (tr:Transfer) ON (tr.transfer_type)",
            "CREATE INDEX transfer_player IF NOT EXISTS FOR (tr:Transfer) ON (tr.player_id)",

            # Stadium indexes
            "CREATE INDEX stadium_city IF NOT EXISTS FOR (s:Stadium) ON (s.city)",
            "CREATE INDEX stadium_capacity IF NOT EXISTS FOR (s:Stadium) ON (s.capacity)",

            # Coach indexes
            "CREATE INDEX coach_name IF NOT EXISTS FOR (co:Coach) ON (co.name)",
            "CREATE INDEX coach_nationality IF NOT EXISTS FOR (co:Coach) ON (co.nationality)",

            # Season indexes
            "CREATE INDEX season_year IF NOT EXISTS FOR (se:Season) ON (se.year)",
            "CREATE INDEX season_current IF NOT EXISTS FOR (se:Season) ON (se.is_current)",

            # Card indexes
            "CREATE INDEX card_type IF NOT EXISTS FOR (ca:Card) ON (ca.type)",
            "CREATE INDEX card_minute IF NOT EXISTS FOR (ca:Card) ON (ca.minute)",
            "CREATE INDEX card_match IF NOT EXISTS FOR (ca:Card) ON (ca.match_id)"
        ]

        results = []
        for index in indexes:
            try:
                self.db.execute_write_query(index)
                results.append(f"✓ {index}")
            except Exception as e:
                results.append(f"✗ {index}: {str(e)}")

        return results

    def create_relationships(self) -> List[str]:
        """
        Create relationship type documentation and ensure they exist.
        This is informational as relationships are created with data.

        Returns:
            List of relationship types defined in the schema
        """
        relationships = [
            # Player relationships
            "PLAYS_FOR: Player -> Team",
            "SCORED: Player -> Goal",
            "ASSISTED: Player -> Goal",
            "RECEIVED: Player -> Card",
            "TRANSFERRED: Player -> Transfer",

            # Team relationships
            "HOME_TEAM: Team -> Match",
            "AWAY_TEAM: Team -> Match",
            "COACHED_BY: Team -> Coach",
            "PLAYS_AT: Team -> Stadium (home stadium)",
            "WON: Team -> Match",
            "LOST: Team -> Match",
            "DREW: Team -> Match",
            "PARTICIPATES_IN: Team -> Competition",

            # Match relationships
            "PLAYED_AT: Match -> Stadium",
            "PART_OF_COMPETITION: Match -> Competition",
            "IN_SEASON: Match -> Season",
            "REFEREED_BY: Match -> Referee",
            "OCCURRED_IN: Goal -> Match",
            "OCCURRED_IN: Card -> Match",

            # Competition relationships
            "HAS_SEASON: Competition -> Season",
            "WINNER: Team -> Competition (per season)",

            # Coach relationships
            "COACHES: Coach -> Team",
            "MANAGED_IN: Coach -> Match",

            # Stadium relationships
            "HOSTS: Stadium -> Match",
            "HOME_OF: Stadium -> Team",

            # Transfer relationships
            "FROM_TEAM: Transfer -> Team",
            "TO_TEAM: Transfer -> Team",
            "INVOLVES_PLAYER: Transfer -> Player"
        ]

        return relationships

    def create_schema(self) -> Dict[str, Any]:
        """
        Create the complete graph schema with constraints, indexes, and relationships.

        Returns:
            Dictionary with creation results
        """
        print("Creating Brazilian Soccer Knowledge Graph schema...")

        constraint_results = self.create_constraints()
        index_results = self.create_indexes()
        relationship_info = self.create_relationships()

        results = {
            "constraints": constraint_results,
            "indexes": index_results,
            "relationships": relationship_info,
            "status": "completed"
        }

        print(f"Schema creation completed!")
        print(f"- {len([r for r in constraint_results if r.startswith('✓')])} constraints created")
        print(f"- {len([r for r in index_results if r.startswith('✓')])} indexes created")
        print(f"- {len(relationship_info)} relationship types defined")

        return results

    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate the current schema against expected structure.

        Returns:
            Dictionary with validation results
        """
        try:
            schema_info = self.db.get_schema_info()

            expected_labels = {
                "Player", "Team", "Stadium", "Competition",
                "Season", "Coach", "Match", "Goal", "Card", "Transfer"
            }

            expected_relationships = {
                "PLAYS_FOR", "SCORED", "ASSISTED", "RECEIVED", "TRANSFERRED",
                "HOME_TEAM", "AWAY_TEAM", "COACHED_BY", "PLAYS_AT",
                "WON", "LOST", "DREW", "PARTICIPATES_IN",
                "PLAYED_AT", "PART_OF_COMPETITION", "IN_SEASON",
                "REFEREED_BY", "OCCURRED_IN", "HAS_SEASON", "WINNER",
                "COACHES", "MANAGED_IN", "HOSTS", "HOME_OF",
                "FROM_TEAM", "TO_TEAM", "INVOLVES_PLAYER"
            }

            current_labels = set(schema_info.get("labels", []))
            current_relationships = set(schema_info.get("relationship_types", []))

            missing_labels = expected_labels - current_labels
            missing_relationships = expected_relationships - current_relationships
            extra_labels = current_labels - expected_labels
            extra_relationships = current_relationships - expected_relationships

            return {
                "valid": len(missing_labels) == 0 and len(missing_relationships) == 0,
                "labels": {
                    "expected": list(expected_labels),
                    "current": list(current_labels),
                    "missing": list(missing_labels),
                    "extra": list(extra_labels)
                },
                "relationships": {
                    "expected": list(expected_relationships),
                    "current": list(current_relationships),
                    "missing": list(missing_relationships),
                    "extra": list(extra_relationships)
                },
                "constraints": len(schema_info.get("constraints", [])),
                "indexes": len(schema_info.get("indexes", []))
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information."""
        return self.db.get_schema_info()

    def drop_schema(self) -> Dict[str, Any]:
        """
        Drop all constraints and indexes (use with caution!).

        Returns:
            Dictionary with drop operation results
        """
        results = {"constraints": [], "indexes": [], "status": "completed"}

        try:
            # Get current constraints and indexes
            schema_info = self.db.get_schema_info()

            # Drop constraints
            for constraint in schema_info.get("constraints", []):
                constraint_name = constraint.get("name", "")
                if constraint_name:
                    try:
                        drop_query = f"DROP CONSTRAINT {constraint_name}"
                        self.db.execute_write_query(drop_query)
                        results["constraints"].append(f"✓ Dropped {constraint_name}")
                    except Exception as e:
                        results["constraints"].append(f"✗ Failed to drop {constraint_name}: {str(e)}")

            # Drop indexes
            for index in schema_info.get("indexes", []):
                index_name = index.get("name", "")
                if index_name and index_name != "constraint":  # Don't drop constraint-based indexes
                    try:
                        drop_query = f"DROP INDEX {index_name}"
                        self.db.execute_write_query(drop_query)
                        results["indexes"].append(f"✓ Dropped {index_name}")
                    except Exception as e:
                        results["indexes"].append(f"✗ Failed to drop {index_name}: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results


# Entity type mapping for factory pattern
ENTITY_TYPES = {
    "Player": Player,
    "Team": Team,
    "Stadium": Stadium,
    "Competition": Competition,
    "Season": Season,
    "Coach": Coach,
    "Match": Match,
    "Goal": Goal,
    "Card": Card,
    "Transfer": Transfer
}

# Enum mappings for validation
ENUM_MAPPINGS = {
    "MatchResult": MatchResult,
    "CardType": CardType,
    "PlayerPosition": PlayerPosition,
    "CompetitionType": CompetitionType,
    "TransferType": TransferType
}


def create_entity(entity_type: str, data: Dict[str, Any]) -> Optional[GraphEntity]:
    """
    Factory function to create entity instances.

    Args:
        entity_type: Type of entity to create
        data: Entity data dictionary

    Returns:
        Entity instance or None if type is invalid
    """
    if entity_type not in ENTITY_TYPES:
        return None

    entity_class = ENTITY_TYPES[entity_type]

    # Handle enum fields
    if entity_type == "Player" and "position" in data:
        if isinstance(data["position"], str):
            data["position"] = PlayerPosition(data["position"])

    if entity_type == "Card" and "type" in data:
        if isinstance(data["type"], str):
            data["type"] = CardType(data["type"])

    if entity_type == "Competition" and "type" in data:
        if isinstance(data["type"], str):
            data["type"] = CompetitionType(data["type"])

    if entity_type == "Transfer" and "transfer_type" in data:
        if isinstance(data["transfer_type"], str):
            data["transfer_type"] = TransferType(data["transfer_type"])

    # Handle date fields
    date_fields = ["birth_date", "date", "transfer_date", "start_date", "end_date",
                   "contract_start", "contract_end", "contract_expires", "announcement_date"]

    for field in date_fields:
        if field in data and isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field]).date()
            except (ValueError, TypeError):
                data[field] = None

    # Handle datetime fields
    datetime_fields = ["created_at", "updated_at"]
    for field in datetime_fields:
        if field in data and isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field])
            except (ValueError, TypeError):
                data[field] = None

    try:
        return entity_class(**data)
    except Exception as e:
        print(f"Error creating {entity_type} entity: {e}")
        return None


# Global schema instance
_schema_instance: Optional[GraphSchema] = None


def get_schema() -> GraphSchema:
    """
    Get global schema instance (singleton pattern).

    Returns:
        GraphSchema instance
    """
    global _schema_instance
    if _schema_instance is None:
        _schema_instance = GraphSchema()
    return _schema_instance