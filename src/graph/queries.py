"""
Brazilian Soccer MCP Knowledge Graph - Query Module

CONTEXT:
This module implements common Cypher queries for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying player, team, match, and competition data
stored in a Neo4j graph database.

PHASE: 1 - Core Data
PURPOSE: Common Cypher queries and query builders for Brazilian soccer data
DATA SOURCES: Kaggle Brazilian Football Matches
DEPENDENCIES: neo4j, py2neo

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition, Stadium, Coach nodes with relationships
- Performance: Optimized queries with proper indexing and parameterization
- Testing: BDD scenarios for database operations

INTEGRATION:
- MCP Tools: Database backend for all query tools
- Error Handling: Comprehensive exception handling
- Rate Limiting: N/A for local database
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
import logging

from .database import Neo4jDatabase, get_database, execute_read_query, execute_write_query

logger = logging.getLogger(__name__)


class QueryBuilder:
    """
    Query builder for constructing complex Cypher queries dynamically.
    """

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        """Initialize query builder with database connection."""
        self.db = db or get_database()
        self._query_parts = []
        self._parameters = {}
        self._return_clause = ""
        self._order_by = ""
        self._limit = ""

    def match(self, pattern: str) -> 'QueryBuilder':
        """Add MATCH clause to query."""
        self._query_parts.append(f"MATCH {pattern}")
        return self

    def where(self, condition: str) -> 'QueryBuilder':
        """Add WHERE clause to query."""
        self._query_parts.append(f"WHERE {condition}")
        return self

    def optional_match(self, pattern: str) -> 'QueryBuilder':
        """Add OPTIONAL MATCH clause to query."""
        self._query_parts.append(f"OPTIONAL MATCH {pattern}")
        return self

    def with_clause(self, clause: str) -> 'QueryBuilder':
        """Add WITH clause to query."""
        self._query_parts.append(f"WITH {clause}")
        return self

    def return_clause(self, clause: str) -> 'QueryBuilder':
        """Set RETURN clause."""
        self._return_clause = f"RETURN {clause}"
        return self

    def order_by(self, clause: str) -> 'QueryBuilder':
        """Set ORDER BY clause."""
        self._order_by = f"ORDER BY {clause}"
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """Set LIMIT clause."""
        self._limit = f"LIMIT {count}"
        return self

    def parameter(self, key: str, value: Any) -> 'QueryBuilder':
        """Add parameter to query."""
        self._parameters[key] = value
        return self

    def build(self) -> Tuple[str, Dict[str, Any]]:
        """Build the final query and parameters."""
        query_parts = self._query_parts.copy()

        if self._return_clause:
            query_parts.append(self._return_clause)

        if self._order_by:
            query_parts.append(self._order_by)

        if self._limit:
            query_parts.append(self._limit)

        query = "\n".join(query_parts)
        return query, self._parameters

    def execute(self) -> List[Dict[str, Any]]:
        """Build and execute the query."""
        query, parameters = self.build()
        return self.db.execute_read_query(query, parameters)

    def reset(self) -> 'QueryBuilder':
        """Reset the query builder for reuse."""
        self._query_parts = []
        self._parameters = {}
        self._return_clause = ""
        self._order_by = ""
        self._limit = ""
        return self


class PlayerQueries:
    """Player-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_player_by_id(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player by ID with all details."""
        query = """
        MATCH (p:Player {id: $player_id})
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(current_team:Team)
        OPTIONAL MATCH (p)-[:SCORED]->(goals:Goal)
        OPTIONAL MATCH (p)-[:ASSISTED]->(assists:Goal)
        OPTIONAL MATCH (p)-[:RECEIVED]->(cards:Card)
        RETURN p,
               current_team.name as current_team,
               count(DISTINCT goals) as total_goals,
               count(DISTINCT assists) as total_assists,
               count(DISTINCT cards) as total_cards
        """
        result = self.db.execute_read_query(query, {"player_id": player_id})
        return result[0] if result else None

    def search_players_by_name(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search players by name (case-insensitive)."""
        query = """
        MATCH (p:Player)
        WHERE toLower(p.name) CONTAINS toLower($name)
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(team:Team)
        RETURN p, team.name as current_team
        ORDER BY p.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"name": name, "limit": limit})

    def get_players_by_position(self, position: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get players by position."""
        query = """
        MATCH (p:Player {position: $position})
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(team:Team)
        RETURN p, team.name as current_team
        ORDER BY p.total_goals DESC, p.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"position": position, "limit": limit})

    def get_top_scorers(self, limit: int = 10, competition_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top goal scorers overall or in specific competition."""
        if competition_id:
            query = """
            MATCH (p:Player)-[:SCORED]->(g:Goal)-[:OCCURRED_IN]->(m:Match)-[:PART_OF_COMPETITION]->(c:Competition {id: $competition_id})
            OPTIONAL MATCH (p)-[:PLAYS_FOR]->(team:Team)
            RETURN p, team.name as current_team, count(g) as goals
            ORDER BY goals DESC, p.name
            LIMIT $limit
            """
            params = {"competition_id": competition_id, "limit": limit}
        else:
            query = """
            MATCH (p:Player)
            WHERE p.total_goals > 0
            OPTIONAL MATCH (p)-[:PLAYS_FOR]->(team:Team)
            RETURN p, team.name as current_team, p.total_goals as goals
            ORDER BY goals DESC, p.name
            LIMIT $limit
            """
            params = {"limit": limit}

        return self.db.execute_read_query(query, params)

    def get_player_career_stats(self, player_id: str) -> Dict[str, Any]:
        """Get comprehensive career statistics for a player."""
        query = """
        MATCH (p:Player {id: $player_id})
        OPTIONAL MATCH (p)-[:SCORED]->(goals:Goal)
        OPTIONAL MATCH (p)-[:ASSISTED]->(assists:Goal)
        OPTIONAL MATCH (p)-[:RECEIVED]->(yellow_cards:Card {type: 'YELLOW'})
        OPTIONAL MATCH (p)-[:RECEIVED]->(red_cards:Card {type: 'RED'})
        OPTIONAL MATCH (p)-[:TRANSFERRED]->(transfers:Transfer)
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(teams:Team)

        WITH p,
             count(DISTINCT goals) as total_goals,
             count(DISTINCT assists) as total_assists,
             count(DISTINCT yellow_cards) as yellow_cards,
             count(DISTINCT red_cards) as red_cards,
             count(DISTINCT transfers) as total_transfers,
             collect(DISTINCT teams.name) as teams_played_for

        RETURN {
            player: p,
            stats: {
                goals: total_goals,
                assists: total_assists,
                yellow_cards: yellow_cards,
                red_cards: red_cards,
                total_transfers: total_transfers,
                teams_played_for: teams_played_for
            }
        } as career_data
        """
        result = self.db.execute_read_query(query, {"player_id": player_id})
        return result[0]["career_data"] if result else {}


class TeamQueries:
    """Team-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_team_by_id(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team by ID with comprehensive details."""
        query = """
        MATCH (t:Team {id: $team_id})
        OPTIONAL MATCH (t)<-[:PLAYS_FOR]-(players:Player)
        OPTIONAL MATCH (t)<-[:COACHES]-(coach:Coach)
        OPTIONAL MATCH (t)-[:PLAYS_AT]->(stadium:Stadium)
        RETURN t,
               count(DISTINCT players) as squad_size,
               coach.name as current_coach,
               stadium.name as home_stadium
        """
        result = self.db.execute_read_query(query, {"team_id": team_id})
        return result[0] if result else None

    def search_teams_by_name(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search teams by name (case-insensitive)."""
        query = """
        MATCH (t:Team)
        WHERE toLower(t.name) CONTAINS toLower($name) OR toLower(t.full_name) CONTAINS toLower($name)
        OPTIONAL MATCH (t)-[:PLAYS_AT]->(stadium:Stadium)
        RETURN t, stadium.name as home_stadium
        ORDER BY t.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"name": name, "limit": limit})

    def get_teams_by_city(self, city: str) -> List[Dict[str, Any]]:
        """Get teams from a specific city."""
        query = """
        MATCH (t:Team {city: $city})
        OPTIONAL MATCH (t)-[:PLAYS_AT]->(stadium:Stadium)
        RETURN t, stadium.name as home_stadium
        ORDER BY t.name
        """
        return self.db.execute_read_query(query, {"city": city})

    def get_team_squad(self, team_id: str) -> List[Dict[str, Any]]:
        """Get current squad for a team."""
        query = """
        MATCH (t:Team {id: $team_id})<-[:PLAYS_FOR]-(p:Player)
        RETURN p
        ORDER BY p.position, p.jersey_number, p.name
        """
        return self.db.execute_read_query(query, {"team_id": team_id})

    def get_team_matches(self, team_id: str, limit: int = 10, season_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent matches for a team."""
        if season_id:
            query = """
            MATCH (t:Team {id: $team_id})
            MATCH (m:Match {season_id: $season_id})
            WHERE m.home_team_id = $team_id OR m.away_team_id = $team_id
            OPTIONAL MATCH (home:Team {id: m.home_team_id})
            OPTIONAL MATCH (away:Team {id: m.away_team_id})
            OPTIONAL MATCH (m)-[:PLAYED_AT]->(stadium:Stadium)
            RETURN m, home.name as home_team, away.name as away_team, stadium.name as stadium
            ORDER BY m.date DESC
            LIMIT $limit
            """
            params = {"team_id": team_id, "season_id": season_id, "limit": limit}
        else:
            query = """
            MATCH (t:Team {id: $team_id})
            MATCH (m:Match)
            WHERE m.home_team_id = $team_id OR m.away_team_id = $team_id
            OPTIONAL MATCH (home:Team {id: m.home_team_id})
            OPTIONAL MATCH (away:Team {id: m.away_team_id})
            OPTIONAL MATCH (m)-[:PLAYED_AT]->(stadium:Stadium)
            RETURN m, home.name as home_team, away.name as away_team, stadium.name as stadium
            ORDER BY m.date DESC
            LIMIT $limit
            """
            params = {"team_id": team_id, "limit": limit}

        return self.db.execute_read_query(query, params)

    def get_team_statistics(self, team_id: str, season_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive team statistics."""
        if season_id:
            query = """
            MATCH (t:Team {id: $team_id})
            OPTIONAL MATCH (m:Match {season_id: $season_id})
            WHERE m.home_team_id = $team_id OR m.away_team_id = $team_id

            WITH t, m,
                 CASE WHEN m.home_team_id = $team_id THEN m.home_score ELSE m.away_score END as goals_for,
                 CASE WHEN m.home_team_id = $team_id THEN m.away_score ELSE m.home_score END as goals_against,
                 CASE
                    WHEN m.home_team_id = $team_id AND m.home_score > m.away_score THEN 'win'
                    WHEN m.away_team_id = $team_id AND m.away_score > m.home_score THEN 'win'
                    WHEN m.home_score = m.away_score THEN 'draw'
                    ELSE 'loss'
                 END as result

            RETURN {
                team: t,
                matches_played: count(m),
                wins: sum(CASE WHEN result = 'win' THEN 1 ELSE 0 END),
                draws: sum(CASE WHEN result = 'draw' THEN 1 ELSE 0 END),
                losses: sum(CASE WHEN result = 'loss' THEN 1 ELSE 0 END),
                goals_for: sum(goals_for),
                goals_against: sum(goals_against),
                goal_difference: sum(goals_for) - sum(goals_against),
                points: sum(CASE WHEN result = 'win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END)
            } as stats
            """
            params = {"team_id": team_id, "season_id": season_id}
        else:
            query = """
            MATCH (t:Team {id: $team_id})
            RETURN {
                team: t,
                matches_played: t.total_matches,
                wins: t.total_wins,
                draws: t.total_draws,
                losses: t.total_losses,
                goals_for: t.total_goals_for,
                goals_against: t.total_goals_against,
                goal_difference: t.total_goals_for - t.total_goals_against
            } as stats
            """
            params = {"team_id": team_id}

        result = self.db.execute_read_query(query, params)
        return result[0]["stats"] if result else {}


class MatchQueries:
    """Match-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_match_by_id(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match by ID with comprehensive details."""
        query = """
        MATCH (m:Match {id: $match_id})
        OPTIONAL MATCH (home:Team {id: m.home_team_id})
        OPTIONAL MATCH (away:Team {id: m.away_team_id})
        OPTIONAL MATCH (m)-[:PLAYED_AT]->(stadium:Stadium)
        OPTIONAL MATCH (m)-[:PART_OF_COMPETITION]->(comp:Competition)
        OPTIONAL MATCH (m)-[:IN_SEASON]->(season:Season)
        OPTIONAL MATCH (g:Goal {match_id: $match_id})<-[:SCORED]-(player:Player)
        OPTIONAL MATCH (c:Card {match_id: $match_id})<-[:RECEIVED]-(card_player:Player)

        RETURN m,
               home.name as home_team,
               away.name as away_team,
               stadium.name as stadium,
               comp.name as competition,
               season.name as season,
               collect(DISTINCT {goal: g, player: player.name}) as goals,
               collect(DISTINCT {card: c, player: card_player.name}) as cards
        """
        result = self.db.execute_read_query(query, {"match_id": match_id})
        return result[0] if result else None

    def get_recent_matches(self, limit: int = 20, status: str = "finished") -> List[Dict[str, Any]]:
        """Get recent matches by status."""
        query = """
        MATCH (m:Match {status: $status})
        OPTIONAL MATCH (home:Team {id: m.home_team_id})
        OPTIONAL MATCH (away:Team {id: m.away_team_id})
        OPTIONAL MATCH (m)-[:PLAYED_AT]->(stadium:Stadium)
        OPTIONAL MATCH (m)-[:PART_OF_COMPETITION]->(comp:Competition)
        RETURN m, home.name as home_team, away.name as away_team,
               stadium.name as stadium, comp.name as competition
        ORDER BY m.date DESC
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"status": status, "limit": limit})

    def get_matches_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get matches within a date range."""
        query = """
        MATCH (m:Match)
        WHERE m.date >= date($start_date) AND m.date <= date($end_date)
        OPTIONAL MATCH (home:Team {id: m.home_team_id})
        OPTIONAL MATCH (away:Team {id: m.away_team_id})
        OPTIONAL MATCH (m)-[:PART_OF_COMPETITION]->(comp:Competition)
        RETURN m, home.name as home_team, away.name as away_team, comp.name as competition
        ORDER BY m.date DESC
        """
        return self.db.execute_read_query(query, {"start_date": start_date, "end_date": end_date})

    def get_match_goals(self, match_id: str) -> List[Dict[str, Any]]:
        """Get all goals for a specific match."""
        query = """
        MATCH (g:Goal {match_id: $match_id})<-[:SCORED]-(player:Player)
        OPTIONAL MATCH (g)<-[:ASSISTED]-(assist_player:Player)
        OPTIONAL MATCH (team:Team {id: g.team_id})
        RETURN g, player.name as scorer, assist_player.name as assister, team.name as team
        ORDER BY g.minute
        """
        return self.db.execute_read_query(query, {"match_id": match_id})

    def get_head_to_head(self, team1_id: str, team2_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get head-to-head match history between two teams."""
        query = """
        MATCH (m:Match)
        WHERE (m.home_team_id = $team1_id AND m.away_team_id = $team2_id) OR
              (m.home_team_id = $team2_id AND m.away_team_id = $team1_id)
        OPTIONAL MATCH (home:Team {id: m.home_team_id})
        OPTIONAL MATCH (away:Team {id: m.away_team_id})
        OPTIONAL MATCH (m)-[:PART_OF_COMPETITION]->(comp:Competition)
        RETURN m, home.name as home_team, away.name as away_team, comp.name as competition
        ORDER BY m.date DESC
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"team1_id": team1_id, "team2_id": team2_id, "limit": limit})


class CompetitionQueries:
    """Competition-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_competition_by_id(self, competition_id: str) -> Optional[Dict[str, Any]]:
        """Get competition by ID with details."""
        query = """
        MATCH (c:Competition {id: $competition_id})
        OPTIONAL MATCH (c)-[:HAS_SEASON]->(seasons:Season)
        OPTIONAL MATCH (m:Match)-[:PART_OF_COMPETITION]->(c)
        RETURN c,
               count(DISTINCT seasons) as total_seasons,
               count(DISTINCT m) as total_matches
        """
        result = self.db.execute_read_query(query, {"competition_id": competition_id})
        return result[0] if result else None

    def get_all_competitions(self) -> List[Dict[str, Any]]:
        """Get all competitions."""
        query = """
        MATCH (c:Competition)
        OPTIONAL MATCH (c)-[:HAS_SEASON]->(current_season:Season {is_current: true})
        RETURN c, current_season.name as current_season
        ORDER BY c.tier, c.name
        """
        return self.db.execute_read_query(query)

    def get_competition_table(self, competition_id: str, season_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get league table for a competition."""
        where_clause = "m.competition_id = $competition_id"
        params = {"competition_id": competition_id}

        if season_id:
            where_clause += " AND m.season_id = $season_id"
            params["season_id"] = season_id

        query = f"""
        MATCH (m:Match)
        WHERE {where_clause} AND m.status = 'finished'
        MATCH (home:Team {{id: m.home_team_id}})
        MATCH (away:Team {{id: m.away_team_id}})

        WITH home as team, m.home_score as goals_for, m.away_score as goals_against,
             CASE
                WHEN m.home_score > m.away_score THEN 3
                WHEN m.home_score = m.away_score THEN 1
                ELSE 0
             END as points,
             CASE WHEN m.home_score > m.away_score THEN 1 ELSE 0 END as wins,
             CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END as draws,
             CASE WHEN m.home_score < m.away_score THEN 1 ELSE 0 END as losses

        UNION

        MATCH (m:Match)
        WHERE {where_clause} AND m.status = 'finished'
        MATCH (home:Team {{id: m.home_team_id}})
        MATCH (away:Team {{id: m.away_team_id}})

        WITH away as team, m.away_score as goals_for, m.home_score as goals_against,
             CASE
                WHEN m.away_score > m.home_score THEN 3
                WHEN m.away_score = m.home_score THEN 1
                ELSE 0
             END as points,
             CASE WHEN m.away_score > m.home_score THEN 1 ELSE 0 END as wins,
             CASE WHEN m.away_score = m.home_score THEN 1 ELSE 0 END as draws,
             CASE WHEN m.away_score < m.home_score THEN 1 ELSE 0 END as losses

        RETURN team.name as team_name,
               team.id as team_id,
               count(*) as matches_played,
               sum(points) as points,
               sum(wins) as wins,
               sum(draws) as draws,
               sum(losses) as losses,
               sum(goals_for) as goals_for,
               sum(goals_against) as goals_against,
               sum(goals_for) - sum(goals_against) as goal_difference
        ORDER BY points DESC, goal_difference DESC, goals_for DESC, team_name
        """
        return self.db.execute_read_query(query, params)


class StadiumQueries:
    """Stadium-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_stadium_by_id(self, stadium_id: str) -> Optional[Dict[str, Any]]:
        """Get stadium by ID with details."""
        query = """
        MATCH (s:Stadium {id: $stadium_id})
        OPTIONAL MATCH (s)<-[:PLAYS_AT]-(home_teams:Team)
        OPTIONAL MATCH (s)<-[:PLAYED_AT]-(matches:Match)
        RETURN s,
               collect(DISTINCT home_teams.name) as home_teams,
               count(DISTINCT matches) as total_matches_hosted
        """
        result = self.db.execute_read_query(query, {"stadium_id": stadium_id})
        return result[0] if result else None

    def get_stadiums_by_capacity(self, min_capacity: int = 0, max_capacity: int = 200000) -> List[Dict[str, Any]]:
        """Get stadiums by capacity range."""
        query = """
        MATCH (s:Stadium)
        WHERE s.capacity >= $min_capacity AND s.capacity <= $max_capacity
        RETURN s
        ORDER BY s.capacity DESC
        """
        return self.db.execute_read_query(query, {"min_capacity": min_capacity, "max_capacity": max_capacity})


class TransferQueries:
    """Transfer-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_player_transfers(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all transfers for a specific player.

        Args:
            player_id: The player's ID

        Returns:
            List of transfer records with source and destination teams
        """
        query = """
        MATCH (p:Player {id: $player_id})
        OPTIONAL MATCH (p)-[tf:TRANSFERRED_FROM]->(from_team:Team)
        OPTIONAL MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
        WHERE tf.transfer_id = tt.transfer_id
        RETURN p.name as player_name,
               from_team.name as from_team,
               to_team.name as to_team,
               tf.year as transfer_year,
               tf.transfer_type as transfer_type,
               tf.transfer_id as transfer_id
        ORDER BY tf.year DESC
        """
        return self.db.execute_read_query(query, {"player_id": player_id})

    def get_player_transfer_history(self, player_id: str) -> Dict[str, Any]:
        """
        Get comprehensive transfer history for a player.

        Args:
            player_id: The player's ID

        Returns:
            Dictionary with player info and transfer timeline
        """
        query = """
        MATCH (p:Player {id: $player_id})
        OPTIONAL MATCH (p)-[tf:TRANSFERRED_FROM]->(from_team:Team)
        OPTIONAL MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
        WHERE tf.transfer_id = tt.transfer_id
        WITH p,
             collect({
                 from_team: from_team.name,
                 to_team: to_team.name,
                 year: tf.year,
                 type: tf.transfer_type
             }) as transfers
        RETURN {
            player: p,
            total_transfers: size(transfers),
            transfers: transfers
        } as history
        """
        result = self.db.execute_read_query(query, {"player_id": player_id})
        return result[0]["history"] if result else {}

    def get_team_transfer_history(self, team_id: str, direction: str = "both", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get transfer history for a team (incoming, outgoing, or both).

        Args:
            team_id: The team's ID
            direction: "in" for incoming, "out" for outgoing, "both" for all
            limit: Maximum number of transfers to return

        Returns:
            List of transfers involving the team
        """
        if direction == "in":
            query = """
            MATCH (p:Player)-[tt:TRANSFERRED_TO]->(t:Team {id: $team_id})
            OPTIONAL MATCH (p)-[tf:TRANSFERRED_FROM]->(from_team:Team)
            WHERE tf.transfer_id = tt.transfer_id
            RETURN p.name as player_name,
                   p.id as player_id,
                   from_team.name as from_team,
                   t.name as to_team,
                   tt.year as transfer_year,
                   tt.transfer_type as transfer_type,
                   'incoming' as direction
            ORDER BY tt.year DESC
            LIMIT $limit
            """
        elif direction == "out":
            query = """
            MATCH (p:Player)-[tf:TRANSFERRED_FROM]->(t:Team {id: $team_id})
            OPTIONAL MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
            WHERE tf.transfer_id = tt.transfer_id
            RETURN p.name as player_name,
                   p.id as player_id,
                   t.name as from_team,
                   to_team.name as to_team,
                   tf.year as transfer_year,
                   tf.transfer_type as transfer_type,
                   'outgoing' as direction
            ORDER BY tf.year DESC
            LIMIT $limit
            """
        else:
            query = """
            MATCH (t:Team {id: $team_id})
            OPTIONAL MATCH (p1:Player)-[tt:TRANSFERRED_TO]->(t)
            OPTIONAL MATCH (p1)-[tf1:TRANSFERRED_FROM]->(from_team:Team)
            WHERE tf1.transfer_id = tt.transfer_id
            WITH t, collect({
                player_name: p1.name,
                player_id: p1.id,
                from_team: from_team.name,
                to_team: t.name,
                year: tt.year,
                type: tt.transfer_type,
                direction: 'incoming'
            }) as incoming

            OPTIONAL MATCH (p2:Player)-[tf2:TRANSFERRED_FROM]->(t)
            OPTIONAL MATCH (p2)-[tt2:TRANSFERRED_TO]->(to_team:Team)
            WHERE tf2.transfer_id = tt2.transfer_id
            WITH incoming, collect({
                player_name: p2.name,
                player_id: p2.id,
                from_team: t.name,
                to_team: to_team.name,
                year: tf2.year,
                type: tf2.transfer_type,
                direction: 'outgoing'
            }) as outgoing

            RETURN incoming + outgoing as transfers
            LIMIT $limit
            """
        return self.db.execute_read_query(query, {"team_id": team_id, "limit": limit})

    def get_transfers_by_year(self, year: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all transfers for a specific year.

        Args:
            year: The transfer year
            limit: Maximum number of transfers to return

        Returns:
            List of transfers for that year
        """
        query = """
        MATCH (p:Player)-[tf:TRANSFERRED_FROM]->(from_team:Team)
        MATCH (p)-[tt:TRANSFERRED_TO]->(to_team:Team)
        WHERE tf.transfer_id = tt.transfer_id AND tf.year = $year
        RETURN p.name as player_name,
               p.id as player_id,
               from_team.name as from_team,
               to_team.name as to_team,
               tf.year as transfer_year,
               tf.transfer_type as transfer_type
        ORDER BY p.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"year": year, "limit": limit})

    def get_transfer_statistics(self) -> Dict[str, Any]:
        """
        Get overall transfer statistics.

        Returns:
            Dictionary with transfer statistics
        """
        query = """
        MATCH ()-[tf:TRANSFERRED_FROM]->()
        WITH count(tf) as total_transfers
        MATCH ()-[tf:TRANSFERRED_FROM]->()
        WITH total_transfers, tf.year as year, count(*) as count
        ORDER BY year
        WITH total_transfers, collect({year: year, count: count}) as by_year
        MATCH ()-[tf:TRANSFERRED_FROM]->()
        WITH total_transfers, by_year, tf.transfer_type as type, count(*) as count
        RETURN {
            total_transfers: total_transfers,
            by_year: by_year,
            by_type: collect({type: type, count: count})
        } as stats
        """
        result = self.db.execute_read_query(query)
        return result[0]["stats"] if result else {}


class CoachQueries:
    """Coach-related queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_team_coach(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current coach for a team.

        Args:
            team_id: The team's ID

        Returns:
            Coach information or None if not found
        """
        query = """
        MATCH (c:Coach)-[m:MANAGES]->(t:Team {id: $team_id})
        WHERE m.active = true
        RETURN c, t.name as team_name, m.active as is_active
        """
        result = self.db.execute_read_query(query, {"team_id": team_id})
        return result[0] if result else None

    def get_coach_by_id(self, coach_id: str) -> Optional[Dict[str, Any]]:
        """
        Get coach by ID with all managed teams.

        Args:
            coach_id: The coach's ID

        Returns:
            Coach information with teams or None if not found
        """
        query = """
        MATCH (c:Coach {id: $coach_id})
        OPTIONAL MATCH (c)-[m:MANAGES]->(teams:Team)
        RETURN c,
               collect({team: teams.name, active: m.active}) as managed_teams,
               count(teams) as total_teams_managed
        """
        result = self.db.execute_read_query(query, {"coach_id": coach_id})
        return result[0] if result else None

    def get_coach_teams(self, coach_id: str) -> List[Dict[str, Any]]:
        """
        Get all teams managed by a coach.

        Args:
            coach_id: The coach's ID

        Returns:
            List of teams with management status
        """
        query = """
        MATCH (c:Coach {id: $coach_id})-[m:MANAGES]->(t:Team)
        RETURN t.id as team_id,
               t.name as team_name,
               m.active as is_current,
               m.start_date as start_date,
               m.end_date as end_date
        ORDER BY m.active DESC, m.start_date DESC
        """
        return self.db.execute_read_query(query, {"coach_id": coach_id})

    def search_coaches_by_name(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search coaches by name (case-insensitive).

        Args:
            name: Name to search for
            limit: Maximum results to return

        Returns:
            List of matching coaches
        """
        query = """
        MATCH (c:Coach)
        WHERE toLower(c.name) CONTAINS toLower($name)
        OPTIONAL MATCH (c)-[m:MANAGES {active: true}]->(t:Team)
        RETURN c, t.name as current_team
        ORDER BY c.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"name": name, "limit": limit})

    def get_coaches_by_nationality(self, nationality: str) -> List[Dict[str, Any]]:
        """
        Get coaches by nationality.

        Args:
            nationality: Coach's nationality

        Returns:
            List of coaches with that nationality
        """
        query = """
        MATCH (c:Coach {nationality: $nationality})
        OPTIONAL MATCH (c)-[m:MANAGES {active: true}]->(t:Team)
        RETURN c, t.name as current_team
        ORDER BY c.name
        """
        return self.db.execute_read_query(query, {"nationality": nationality})

    def get_all_coaches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all coaches with their current teams.

        Args:
            limit: Maximum number of coaches to return

        Returns:
            List of all coaches
        """
        query = """
        MATCH (c:Coach)
        OPTIONAL MATCH (c)-[m:MANAGES {active: true}]->(t:Team)
        RETURN c, t.name as current_team
        ORDER BY c.name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"limit": limit})

    def get_coach_statistics(self, coach_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a coach.

        Args:
            coach_id: The coach's ID

        Returns:
            Dictionary with coach statistics
        """
        query = """
        MATCH (c:Coach {id: $coach_id})
        OPTIONAL MATCH (c)-[m:MANAGES]->(teams:Team)
        WITH c, count(teams) as teams_managed, collect(teams.name) as team_names
        RETURN {
            coach: c,
            total_teams_managed: teams_managed,
            teams: team_names,
            win_percentage: c.win_percentage,
            total_matches: c.total_matches,
            total_trophies: c.total_trophies
        } as stats
        """
        result = self.db.execute_read_query(query, {"coach_id": coach_id})
        return result[0]["stats"] if result else {}


class AnalyticsQueries:
    """Advanced analytics queries for the Brazilian Soccer Knowledge Graph."""

    def __init__(self, db: Optional[Neo4jDatabase] = None):
        self.db = db or get_database()

    def get_top_scorers_by_competition(self, competition_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scorers in a specific competition."""
        query = """
        MATCH (p:Player)-[:SCORED]->(g:Goal)-[:OCCURRED_IN]->(m:Match)-[:PART_OF_COMPETITION]->(c:Competition {id: $competition_id})
        OPTIONAL MATCH (p)-[:PLAYS_FOR]->(team:Team)
        RETURN p.name as player_name,
               p.id as player_id,
               team.name as team_name,
               count(g) as goals
        ORDER BY goals DESC, player_name
        LIMIT $limit
        """
        return self.db.execute_read_query(query, {"competition_id": competition_id, "limit": limit})

    def get_goal_statistics_by_minute(self) -> List[Dict[str, Any]]:
        """Get goal distribution by match minute."""
        query = """
        MATCH (g:Goal)
        WITH CASE
            WHEN g.minute <= 15 THEN '0-15'
            WHEN g.minute <= 30 THEN '16-30'
            WHEN g.minute <= 45 THEN '31-45'
            WHEN g.minute <= 60 THEN '46-60'
            WHEN g.minute <= 75 THEN '61-75'
            WHEN g.minute <= 90 THEN '76-90'
            ELSE '90+'
        END as minute_range, g
        RETURN minute_range, count(g) as goals
        ORDER BY
            CASE minute_range
                WHEN '0-15' THEN 1
                WHEN '16-30' THEN 2
                WHEN '31-45' THEN 3
                WHEN '46-60' THEN 4
                WHEN '61-75' THEN 5
                WHEN '76-90' THEN 6
                ELSE 7
            END
        """
        return self.db.execute_read_query(query)

    def get_team_form(self, team_id: str, matches: int = 5) -> List[Dict[str, Any]]:
        """Get recent form for a team (last N matches)."""
        query = """
        MATCH (m:Match)
        WHERE m.home_team_id = $team_id OR m.away_team_id = $team_id
        AND m.status = 'finished'
        OPTIONAL MATCH (home:Team {id: m.home_team_id})
        OPTIONAL MATCH (away:Team {id: m.away_team_id})

        WITH m, home, away,
             CASE
                WHEN m.home_team_id = $team_id AND m.home_score > m.away_score THEN 'W'
                WHEN m.away_team_id = $team_id AND m.away_score > m.home_score THEN 'W'
                WHEN m.home_score = m.away_score THEN 'D'
                ELSE 'L'
             END as result

        RETURN m.date as match_date,
               home.name as home_team,
               away.name as away_team,
               m.home_score as home_score,
               m.away_score as away_score,
               result
        ORDER BY m.date DESC
        LIMIT $matches
        """
        return self.db.execute_read_query(query, {"team_id": team_id, "matches": matches})

    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        query = """
        MATCH (p:Player) WITH count(p) as players
        MATCH (t:Team) WITH players, count(t) as teams
        MATCH (m:Match) WITH players, teams, count(m) as matches
        MATCH (g:Goal) WITH players, teams, matches, count(g) as goals
        MATCH (c:Card) WITH players, teams, matches, goals, count(c) as cards
        MATCH (comp:Competition) WITH players, teams, matches, goals, cards, count(comp) as competitions
        MATCH (s:Stadium) WITH players, teams, matches, goals, cards, competitions, count(s) as stadiums
        MATCH (coach:Coach) WITH players, teams, matches, goals, cards, competitions, stadiums, count(coach) as coaches
        MATCH (tr:Transfer) WITH players, teams, matches, goals, cards, competitions, stadiums, coaches, count(tr) as transfers
        MATCH (se:Season) WITH players, teams, matches, goals, cards, competitions, stadiums, coaches, transfers, count(se) as seasons

        RETURN {
            players: players,
            teams: teams,
            matches: matches,
            goals: goals,
            cards: cards,
            competitions: competitions,
            stadiums: stadiums,
            coaches: coaches,
            transfers: transfers,
            seasons: seasons
        } as summary
        """
        result = self.db.execute_read_query(query)
        return result[0]["summary"] if result else {}


# Global query instances for convenience
def get_player_queries() -> PlayerQueries:
    """Get PlayerQueries instance."""
    return PlayerQueries()

def get_team_queries() -> TeamQueries:
    """Get TeamQueries instance."""
    return TeamQueries()

def get_match_queries() -> MatchQueries:
    """Get MatchQueries instance."""
    return MatchQueries()

def get_competition_queries() -> CompetitionQueries:
    """Get CompetitionQueries instance."""
    return CompetitionQueries()

def get_stadium_queries() -> StadiumQueries:
    """Get StadiumQueries instance."""
    return StadiumQueries()

def get_analytics_queries() -> AnalyticsQueries:
    """Get AnalyticsQueries instance."""
    return AnalyticsQueries()

def get_transfer_queries() -> TransferQueries:
    """Get TransferQueries instance."""
    return TransferQueries()

def get_coach_queries() -> CoachQueries:
    """Get CoachQueries instance."""
    return CoachQueries()

def get_query_builder() -> QueryBuilder:
    """Get QueryBuilder instance."""
    return QueryBuilder()


# Common query shortcuts
def search_entity(entity_type: str, name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Generic entity search by name.

    Args:
        entity_type: Type of entity (Player, Team, Stadium, etc.)
        name: Name to search for
        limit: Maximum results to return

    Returns:
        List of matching entities
    """
    query = f"""
    MATCH (e:{entity_type})
    WHERE toLower(e.name) CONTAINS toLower($name)
    RETURN e
    ORDER BY e.name
    LIMIT $limit
    """
    return execute_read_query(query, {"name": name, "limit": limit})


def get_entity_by_id(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """
    Generic entity retrieval by ID.

    Args:
        entity_type: Type of entity (Player, Team, Stadium, etc.)
        entity_id: Entity ID

    Returns:
        Entity data or None if not found
    """
    query = f"""
    MATCH (e:{entity_type} {{id: $entity_id}})
    RETURN e
    """
    result = execute_read_query(query, {"entity_id": entity_id})
    return result[0] if result else None


def get_entity_relationships(entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
    """
    Get all relationships for an entity.

    Args:
        entity_type: Type of entity
        entity_id: Entity ID

    Returns:
        List of relationships
    """
    query = f"""
    MATCH (e:{entity_type} {{id: $entity_id}})
    OPTIONAL MATCH (e)-[r]-(related)
    RETURN type(r) as relationship_type,
           labels(related) as related_entity_type,
           related.id as related_id,
           related.name as related_name
    """
    return execute_read_query(query, {"entity_id": entity_id})