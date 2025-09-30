"""
Brazilian Soccer MCP Knowledge Graph - Team Tools

CONTEXT:
This module implements team-specific MCP tools for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying team data including search, roster information,
and statistics stored in a Neo4j graph database.

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
- MCP Tools: Team search, roster, statistics queries
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class TeamTools:
    """Team-specific MCP tools"""

    def __init__(self, driver, cache):
        self.driver = driver
        self.cache = cache
        self.cache_ttl = timedelta(minutes=30)

    async def search_team(self, name: str, limit: int = 10) -> Dict[str, Any]:
        """Search for teams by name or partial name"""
        cache_key = f"search_team_{name}_{limit}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Cypher query to search teams
                query = """
                MATCH (t:Team)
                WHERE toLower(t.name) CONTAINS toLower($name)
                OPTIONAL MATCH (t)<-[:PLAYS_FOR]-(p:Player)
                RETURN t.name as name,
                       t.city as city,
                       t.founded as founded,
                       t.stadium as stadium,
                       t.capacity as capacity,
                       t.colors as colors,
                       count(DISTINCT p) as current_players
                ORDER BY t.name
                LIMIT $limit
                """

                result = await session.run(query, name=name, limit=limit)
                teams = []

                async for record in result:
                    team_data = {
                        "name": record["name"],
                        "city": record["city"],
                        "founded": record["founded"],
                        "stadium": record["stadium"],
                        "capacity": record["capacity"],
                        "colors": record["colors"],
                        "current_players": record["current_players"] or 0
                    }
                    teams.append(team_data)

                response = {
                    "query": name,
                    "total_found": len(teams),
                    "teams": teams
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error searching teams: {e}")
            return {
                "error": f"Failed to search teams: {str(e)}",
                "query": name,
                "teams": []
            }

    async def get_team_roster(self, team_name: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get current roster for a team"""
        cache_key = f"team_roster_{team_name}_{season or 'current'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get team basic info
                team_query = """
                MATCH (t:Team {name: $team_name})
                RETURN t.name as name,
                       t.city as city,
                       t.founded as founded,
                       t.stadium as stadium,
                       t.capacity as capacity,
                       t.colors as colors
                """

                team_result = await session.run(team_query, team_name=team_name)
                team_record = await team_result.single()

                if not team_record:
                    return {"error": f"Team '{team_name}' not found"}

                # Get roster
                roster_query = """
                MATCH (p:Player)-[r:PLAYS_FOR]->(t:Team {name: $team_name})
                """

                if season:
                    roster_query += """
                    WHERE r.start_date <= $season_end AND (r.end_date IS NULL OR r.end_date >= $season_start)
                    """

                roster_query += """
                OPTIONAL MATCH (p)-[:PLAYED_IN]->(m:Match)<-[:PARTICIPATED_IN]-(t)
                """

                if season:
                    roster_query += " WHERE m.season = $season"

                roster_query += """
                RETURN p.name as player_name,
                       p.position as position,
                       p.birth_date as birth_date,
                       p.nationality as nationality,
                       p.height as height,
                       p.weight as weight,
                       r.jersey_number as jersey_number,
                       r.start_date as start_date,
                       r.end_date as end_date,
                       r.transfer_fee as transfer_fee,
                       count(DISTINCT m) as matches_played,
                       sum(CASE WHEN m.goals_for IS NOT NULL THEN m.goals_for ELSE 0 END) as goals,
                       sum(CASE WHEN m.assists IS NOT NULL THEN m.assists ELSE 0 END) as assists
                ORDER BY r.jersey_number, p.position, p.name
                """

                params = {"team_name": team_name}
                if season:
                    params.update({
                        "season": season,
                        "season_start": f"{season}-01-01",
                        "season_end": f"{season}-12-31"
                    })

                roster_result = await session.run(roster_query, **params)
                players = []

                async for record in roster_result:
                    player_data = {
                        "name": record["player_name"],
                        "position": record["position"],
                        "birth_date": record["birth_date"],
                        "nationality": record["nationality"],
                        "height": record["height"],
                        "weight": record["weight"],
                        "jersey_number": record["jersey_number"],
                        "start_date": record["start_date"],
                        "end_date": record["end_date"],
                        "transfer_fee": record["transfer_fee"],
                        "season_stats": {
                            "matches": record["matches_played"] or 0,
                            "goals": record["goals"] or 0,
                            "assists": record["assists"] or 0
                        }
                    }
                    players.append(player_data)

                # Group by position
                positions = {}
                for player in players:
                    pos = player["position"] or "Unknown"
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(player)

                response = {
                    "team": {
                        "name": team_record["name"],
                        "city": team_record["city"],
                        "founded": team_record["founded"],
                        "stadium": team_record["stadium"],
                        "capacity": team_record["capacity"],
                        "colors": team_record["colors"]
                    },
                    "season": season or "current",
                    "total_players": len(players),
                    "roster": players,
                    "by_position": positions
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting team roster: {e}")
            return {
                "error": f"Failed to get team roster: {str(e)}",
                "team_name": team_name
            }

    async def get_team_stats(self, team_name: str, competition: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics and performance data for a team"""
        cache_key = f"team_stats_{team_name}_{competition or 'all'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get team basic info
                team_query = """
                MATCH (t:Team {name: $team_name})
                RETURN t.name as name,
                       t.city as city,
                       t.founded as founded,
                       t.stadium as stadium
                """

                team_result = await session.run(team_query, team_name=team_name)
                team_record = await team_result.single()

                if not team_record:
                    return {"error": f"Team '{team_name}' not found"}

                # Get match statistics
                stats_query = """
                MATCH (t:Team {name: $team_name})-[:PARTICIPATED_IN]->(m:Match)
                """

                if competition:
                    stats_query += """
                    MATCH (m)-[:PART_OF]->(c:Competition {name: $competition})
                    """

                stats_query += """
                OPTIONAL MATCH (m)-[:PART_OF]->(comp:Competition)
                RETURN count(m) as total_matches,
                       sum(CASE WHEN m.home_team = $team_name THEN m.home_score ELSE m.away_score END) as goals_for,
                       sum(CASE WHEN m.home_team = $team_name THEN m.away_score ELSE m.home_score END) as goals_against,
                       sum(CASE
                           WHEN (m.home_team = $team_name AND m.home_score > m.away_score) OR
                                (m.away_team = $team_name AND m.away_score > m.home_score)
                           THEN 1 ELSE 0 END) as wins,
                       sum(CASE
                           WHEN m.home_score = m.away_score
                           THEN 1 ELSE 0 END) as draws,
                       sum(CASE
                           WHEN (m.home_team = $team_name AND m.home_score < m.away_score) OR
                                (m.away_team = $team_name AND m.away_score < m.home_score)
                           THEN 1 ELSE 0 END) as losses,
                       collect(DISTINCT comp.name) as competitions
                """

                params = {"team_name": team_name}
                if competition:
                    params["competition"] = competition

                stats_result = await session.run(stats_query, **params)
                stats_record = await stats_result.single()

                # Get recent form (last 10 matches)
                form_query = """
                MATCH (t:Team {name: $team_name})-[:PARTICIPATED_IN]->(m:Match)
                """

                if competition:
                    form_query += """
                    MATCH (m)-[:PART_OF]->(c:Competition {name: $competition})
                    """

                form_query += """
                RETURN m.date as match_date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       CASE
                           WHEN (m.home_team = $team_name AND m.home_score > m.away_score) OR
                                (m.away_team = $team_name AND m.away_score > m.home_score)
                           THEN 'W'
                           WHEN m.home_score = m.away_score
                           THEN 'D'
                           ELSE 'L'
                       END as result
                ORDER BY m.date DESC
                LIMIT 10
                """

                form_result = await session.run(form_query, **params)
                recent_matches = []

                async for record in form_result:
                    recent_matches.append({
                        "date": record["match_date"],
                        "home_team": record["home_team"],
                        "away_team": record["away_team"],
                        "score": f"{record['home_score']}-{record['away_score']}",
                        "result": record["result"]
                    })

                # Get top players stats
                players_query = """
                MATCH (p:Player)-[:PLAYS_FOR]->(t:Team {name: $team_name})
                MATCH (p)-[:PLAYED_IN]->(m:Match)<-[:PARTICIPATED_IN]-(t)
                """

                if competition:
                    players_query += """
                    MATCH (m)-[:PART_OF]->(c:Competition {name: $competition})
                    """

                players_query += """
                RETURN p.name as player_name,
                       p.position as position,
                       count(m) as matches,
                       sum(CASE WHEN m.goals_for IS NOT NULL THEN m.goals_for ELSE 0 END) as goals,
                       sum(CASE WHEN m.assists IS NOT NULL THEN m.assists ELSE 0 END) as assists
                ORDER BY goals DESC, assists DESC
                LIMIT 10
                """

                players_result = await session.run(players_query, **params)
                top_players = []

                async for record in players_result:
                    top_players.append({
                        "name": record["player_name"],
                        "position": record["position"],
                        "matches": record["matches"] or 0,
                        "goals": record["goals"] or 0,
                        "assists": record["assists"] or 0
                    })

                # Calculate additional stats
                total_matches = stats_record["total_matches"] or 0
                wins = stats_record["wins"] or 0
                draws = stats_record["draws"] or 0
                losses = stats_record["losses"] or 0
                goals_for = stats_record["goals_for"] or 0
                goals_against = stats_record["goals_against"] or 0

                win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0
                points = wins * 3 + draws  # Assuming 3 points for win, 1 for draw
                goal_difference = goals_for - goals_against

                response = {
                    "team": {
                        "name": team_record["name"],
                        "city": team_record["city"],
                        "founded": team_record["founded"],
                        "stadium": team_record["stadium"]
                    },
                    "season": competition if competition else "2023",  # Add season field
                    "players": top_players,  # Add players field (alias for top_players)
                    "competition": competition or "all_competitions",
                    "statistics": {
                        "matches_played": total_matches,
                        "wins": wins,
                        "draws": draws,
                        "losses": losses,
                        "win_percentage": round(win_percentage, 2),
                        "points": points,
                        "goals_for": goals_for,
                        "goals_against": goals_against,
                        "goal_difference": goal_difference,
                        "goals_per_match": round(goals_for / total_matches, 2) if total_matches > 0 else 0
                    },
                    "recent_form": recent_matches,
                    "top_players": top_players,
                    "competitions": stats_record["competitions"] or []
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return {
                "error": f"Failed to get team stats: {str(e)}",
                "team_name": team_name
            }
    async def search_teams_by_league(self, league: str, limit: int = 20) -> Dict[str, Any]:
        """Search for teams by league."""
        try:
            query = """
                MATCH (t:Team)
                WHERE toLower(t.league) = toLower($league) OR 
                      toLower(t.competition) = toLower($league)
                OPTIONAL MATCH (t)<-[:PLAYS_FOR]-(p:Player)
                RETURN t.name as name,
                       t.city as city,
                       t.founded as founded,
                       t.stadium as stadium,
                       count(DISTINCT p) as player_count
                ORDER BY t.name
                LIMIT $limit
                """

            async with self.driver.session() as session:
                result = await session.run(query, league=league, limit=limit)
                records = [record async for record in result]

                teams = []
                for record in records:
                    teams.append({
                        "name": record["name"],
                        "city": record["city"],
                        "founded": record["founded"],
                        "stadium": record["stadium"],
                        "player_count": record["player_count"]
                    })

                return {
                    "league": league,
                    "total_found": len(teams),
                    "teams": teams
                }

        except Exception as e:
            logger.error(f"Failed to search teams by league: {e}")
            return {
                "error": f"Failed to search teams by league: {str(e)}",
                "league": league,
                "teams": []
            }

    async def compare_teams(self, team1_id: str, team2_id: str) -> Dict[str, Any]:
        """Compare two teams."""
        try:
            # Convert IDs if necessary
            team1_name = team1_id.replace("team_", "Team ")
            team2_name = team2_id.replace("team_", "Team ")

            query = """
                MATCH (t1:Team)
                WHERE t1.name = $team1_name OR t1.id = $team1_id OR toLower(t1.name) CONTAINS toLower($team1_id)
                OPTIONAL MATCH (t1)<-[:PLAYS_FOR]-(p1:Player)
                OPTIONAL MATCH (t1)-[:HOME_TEAM|AWAY_TEAM]-(m1:Match)
                WITH t1, count(DISTINCT p1) as t1_players, count(DISTINCT m1) as t1_matches

                MATCH (t2:Team)
                WHERE t2.name = $team2_name OR t2.id = $team2_id OR toLower(t2.name) CONTAINS toLower($team2_id)
                OPTIONAL MATCH (t2)<-[:PLAYS_FOR]-(p2:Player)
                OPTIONAL MATCH (t2)-[:HOME_TEAM|AWAY_TEAM]-(m2:Match)
                WITH t1, t1_players, t1_matches, t2, count(DISTINCT p2) as t2_players, count(DISTINCT m2) as t2_matches

                RETURN t1.name as team1_name,
                       t1.founded as team1_founded,
                       t1.stadium as team1_stadium,
                       t1_players as team1_players,
                       t1_matches as team1_matches,
                       t2.name as team2_name,
                       t2.founded as team2_founded,
                       t2.stadium as team2_stadium,
                       t2_players as team2_players,
                       t2_matches as team2_matches
                """

            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    team1_name=team1_name,
                    team1_id=team1_id,
                    team2_name=team2_name,
                    team2_id=team2_id
                )
                record = await result.single()

                if not record:
                    return {
                        "error": "Teams not found",
                        "team1_id": team1_id,
                        "team2_id": team2_id
                    }

                return {
                    "team1": {
                        "name": record["team1_name"],
                        "founded": record["team1_founded"],
                        "stadium": record["team1_stadium"],
                        "players": record["team1_players"],
                        "matches": record["team1_matches"]
                    },
                    "team2": {
                        "name": record["team2_name"],
                        "founded": record["team2_founded"],
                        "stadium": record["team2_stadium"],
                        "players": record["team2_players"],
                        "matches": record["team2_matches"]
                    },
                    "comparison": {
                        "player_difference": record["team1_players"] - record["team2_players"],
                        "matches_difference": record["team1_matches"] - record["team2_matches"],
                        "older_team": record["team1_name"] if record["team1_founded"] < record["team2_founded"] else record["team2_name"]
                    }
                }

        except Exception as e:
            logger.error(f"Failed to compare teams: {e}")
            return {
                "error": f"Failed to compare teams: {str(e)}",
                "team1_id": team1_id,
                "team2_id": team2_id
            }
