"""
Brazilian Soccer MCP Knowledge Graph - Match Tools

CONTEXT:
This module implements match-specific MCP tools for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying match data including details, search,
head-to-head comparisons, and competition standings stored in a Neo4j graph database.

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
- MCP Tools: Match details, search, head-to-head, competition queries
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MatchTools:
    """Match-specific MCP tools"""

    def __init__(self, driver, cache):
        self.driver = driver
        self.cache = cache
        self.cache_ttl = timedelta(minutes=30)

    async def get_match_details(self, match_id: Optional[str] = None,
                               team1: Optional[str] = None,
                               team2: Optional[str] = None,
                               date: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a specific match"""

        # Create cache key based on available parameters
        cache_params = [match_id, team1, team2, date]
        cache_key = f"match_details_{'_'.join(str(p) for p in cache_params if p)}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Build query based on available parameters
                if match_id:
                    query = "MATCH (m:Match {id: $match_id})"
                    params = {"match_id": match_id}
                elif team1 and team2:
                    query = """
                    MATCH (m:Match)
                    WHERE (m.home_team = $team1 AND m.away_team = $team2) OR
                          (m.home_team = $team2 AND m.away_team = $team1)
                    """
                    params = {"team1": team1, "team2": team2}
                    if date:
                        query += " AND m.date = $date"
                        params["date"] = date
                    query += " ORDER BY m.date DESC LIMIT 1"
                else:
                    return {"error": "Must provide either match_id or team1+team2"}

                # Complete the query
                query += """
                OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)
                OPTIONAL MATCH (p:Player)-[:PLAYED_IN]->(m)
                OPTIONAL MATCH (ht:Team {name: m.home_team})
                OPTIONAL MATCH (at:Team {name: m.away_team})
                RETURN m.id as match_id,
                       m.date as date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       m.venue as venue,
                       m.attendance as attendance,
                       m.referee as referee,
                       c.name as competition,
                       c.season as season,
                       ht.city as home_city,
                       at.city as away_city,
                       collect(DISTINCT {
                           player: p.name,
                           position: p.position,
                           team: CASE WHEN exists((p)-[:PLAYS_FOR]->(:Team {name: m.home_team}))
                                     THEN m.home_team ELSE m.away_team END,
                           goals: 0,
                           assists: 0,
                           cards: []
                       }) as player_stats
                """

                result = await session.run(query, **params)
                record = await result.single()

                if not record:
                    return {"error": "Match not found"}

                # Get match events
                events_query = """
                MATCH (m:Match)
                WHERE m.id = $match_id OR
                      (m.home_team = $home_team AND m.away_team = $away_team AND m.date = $date)
                OPTIONAL MATCH (e:Event)-[:OCCURRED_IN]->(m)
                RETURN e.type as event_type,
                       e.minute as minute,
                       e.player as player,
                       e.team as team,
                       e.description as description
                ORDER BY e.minute
                """

                events_params = {
                    "match_id": record["match_id"],
                    "home_team": record["home_team"],
                    "away_team": record["away_team"],
                    "date": record["date"]
                }

                events_result = await session.run(events_query, **events_params)
                events = []

                async for event_record in events_result:
                    if event_record["event_type"]:
                        events.append({
                            "type": event_record["event_type"],
                            "minute": event_record["minute"],
                            "player": event_record["player"],
                            "team": event_record["team"],
                            "description": event_record["description"]
                        })

                # Process player stats
                home_players = []
                away_players = []
                for player_stat in record["player_stats"]:
                    if player_stat["player"]:
                        if player_stat["team"] == record["home_team"]:
                            home_players.append(player_stat)
                        else:
                            away_players.append(player_stat)

                response = {
                    "match": {
                        "id": record["match_id"],
                        "date": record["date"],
                        "venue": record["venue"],
                        "attendance": record["attendance"],
                        "referee": record["referee"]
                    },
                    "competition": {
                        "name": record["competition"],
                        "season": record["season"]
                    },
                    "teams": {
                        "home": {
                            "name": record["home_team"],
                            "city": record["home_city"],
                            "score": record["home_score"]
                        },
                        "away": {
                            "name": record["away_team"],
                            "city": record["away_city"],
                            "score": record["away_score"]
                        }
                    },
                    "result": {
                        "home_score": record["home_score"],
                        "away_score": record["away_score"],
                        "winner": (record["home_team"] if record["home_score"] > record["away_score"]
                                 else record["away_team"] if record["away_score"] > record["home_score"]
                                 else "Draw")
                    },
                    "players": {
                        "home": home_players,
                        "away": away_players
                    },
                    "events": events
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting match details: {e}")
            return {
                "error": f"Failed to get match details: {str(e)}"
            }

    async def search_matches(self, team: Optional[str] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            competition: Optional[str] = None,
                            limit: int = 20) -> Dict[str, Any]:
        """Search for matches by teams, date range, or competition"""

        cache_key = f"search_matches_{team}_{start_date}_{end_date}_{competition}_{limit}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Build query
                query = "MATCH (m:Match)"
                where_conditions = []
                params = {"limit": limit}

                if team:
                    where_conditions.append("(m.home_team = $team OR m.away_team = $team)")
                    params["team"] = team

                if start_date:
                    where_conditions.append("m.date >= $start_date")
                    params["start_date"] = start_date

                if end_date:
                    where_conditions.append("m.date <= $end_date")
                    params["end_date"] = end_date

                if competition:
                    query += " MATCH (m)-[:PART_OF]->(c:Competition)"
                    where_conditions.append("c.name = $competition")
                    params["competition"] = competition

                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)

                query += """
                OPTIONAL MATCH (m)-[:PART_OF]->(comp:Competition)
                RETURN m.id as match_id,
                       m.date as date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       m.venue as venue,
                       comp.name as competition
                ORDER BY m.date DESC
                LIMIT $limit
                """

                result = await session.run(query, **params)
                matches = []

                async for record in result:
                    match_data = {
                        "id": record["match_id"],
                        "date": record["date"],
                        "home_team": record["home_team"],
                        "away_team": record["away_team"],
                        "score": f"{record['home_score']}-{record['away_score']}",
                        "venue": record["venue"],
                        "competition": record["competition"],
                        "result": (record["home_team"] if record["home_score"] > record["away_score"]
                                 else record["away_team"] if record["away_score"] > record["home_score"]
                                 else "Draw")
                    }
                    matches.append(match_data)

                response = {
                    "search_criteria": {
                        "team": team,
                        "date_range": f"{start_date or 'any'} to {end_date or 'any'}",
                        "competition": competition
                    },
                    "total_found": len(matches),
                    "matches": matches
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error searching matches: {e}")
            return {
                "error": f"Failed to search matches: {str(e)}",
                "matches": []
            }

    async def get_head_to_head(self, team1: str, team2: str,
                              competition: Optional[str] = None) -> Dict[str, Any]:
        """Get head-to-head statistics between two teams"""

        cache_key = f"head_to_head_{team1}_{team2}_{competition or 'all'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get all matches between the teams
                query = """
                MATCH (m:Match)
                WHERE (m.home_team = $team1 AND m.away_team = $team2) OR
                      (m.home_team = $team2 AND m.away_team = $team1)
                """

                params = {"team1": team1, "team2": team2}

                if competition:
                    query += """
                    MATCH (m)-[:PART_OF]->(c:Competition {name: $competition})
                    """
                    params["competition"] = competition

                query += """
                OPTIONAL MATCH (m)-[:PART_OF]->(comp:Competition)
                RETURN m.date as date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       m.venue as venue,
                       comp.name as competition,
                       comp.season as season
                ORDER BY m.date DESC
                """

                result = await session.run(query, **params)
                matches = []
                team1_wins = 0
                team2_wins = 0
                draws = 0
                team1_goals = 0
                team2_goals = 0

                async for record in result:
                    home_team = record["home_team"]
                    away_team = record["away_team"]
                    home_score = record["home_score"] or 0
                    away_score = record["away_score"] or 0

                    # Determine result from team1's perspective
                    if home_team == team1:
                        team1_score = home_score
                        team2_score = away_score
                    else:
                        team1_score = away_score
                        team2_score = home_score

                    team1_goals += team1_score
                    team2_goals += team2_score

                    if team1_score > team2_score:
                        team1_wins += 1
                        result_status = "win"
                    elif team2_score > team1_score:
                        team2_wins += 1
                        result_status = "loss"
                    else:
                        draws += 1
                        result_status = "draw"

                    match_data = {
                        "date": record["date"],
                        "home_team": home_team,
                        "away_team": away_team,
                        "score": f"{home_score}-{away_score}",
                        "venue": record["venue"],
                        "competition": record["competition"],
                        "season": record["season"],
                        "result_for_team1": result_status
                    }
                    matches.append(match_data)

                total_matches = len(matches)

                # Get recent form (last 10 matches)
                recent_form = matches[:10]

                # Calculate win percentages
                team1_win_pct = (team1_wins / total_matches * 100) if total_matches > 0 else 0
                team2_win_pct = (team2_wins / total_matches * 100) if total_matches > 0 else 0
                draw_pct = (draws / total_matches * 100) if total_matches > 0 else 0

                # Get competition breakdown
                competitions = {}
                for match in matches:
                    comp = match["competition"] or "Unknown"
                    if comp not in competitions:
                        competitions[comp] = {"matches": 0, "team1_wins": 0, "team2_wins": 0, "draws": 0}
                    competitions[comp]["matches"] += 1
                    if match["result_for_team1"] == "win":
                        competitions[comp]["team1_wins"] += 1
                    elif match["result_for_team1"] == "loss":
                        competitions[comp]["team2_wins"] += 1
                    else:
                        competitions[comp]["draws"] += 1

                response = {
                    "teams": {
                        "team1": team1,
                        "team2": team2
                    },
                    "competition_filter": competition,
                    "overall_record": {
                        "total_matches": total_matches,
                        "team1_wins": team1_wins,
                        "team2_wins": team2_wins,
                        "draws": draws,
                        "team1_win_percentage": round(team1_win_pct, 2),
                        "team2_win_percentage": round(team2_win_pct, 2),
                        "draw_percentage": round(draw_pct, 2)
                    },
                    "goals": {
                        "team1_total": team1_goals,
                        "team2_total": team2_goals,
                        "team1_average": round(team1_goals / total_matches, 2) if total_matches > 0 else 0,
                        "team2_average": round(team2_goals / total_matches, 2) if total_matches > 0 else 0
                    },
                    "recent_form": recent_form,
                    "by_competition": competitions,
                    "all_matches": matches
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting head-to-head: {e}")
            return {
                "error": f"Failed to get head-to-head stats: {str(e)}",
                "teams": {"team1": team1, "team2": team2}
            }

    async def get_competition_standings(self, competition: str,
                                       season: Optional[str] = None) -> Dict[str, Any]:
        """Get current standings for a competition"""

        cache_key = f"competition_standings_{competition}_{season or 'current'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get standings data
                query = """
                MATCH (c:Competition {name: $competition})
                """

                params = {"competition": competition}

                if season:
                    query += " WHERE c.season = $season"
                    params["season"] = season

                query += """
                MATCH (m:Match)-[:PART_OF]->(c)
                MATCH (t:Team)-[:PARTICIPATED_IN]->(m)
                RETURN t.name as team,
                       count(m) as matches_played,
                       sum(CASE WHEN (m.home_team = t.name AND m.home_score > m.away_score) OR
                                     (m.away_team = t.name AND m.away_score > m.home_score) THEN 1 ELSE 0 END) as wins,
                       sum(CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END) as draws,
                       sum(CASE WHEN (m.home_team = t.name AND m.home_score < m.away_score) OR
                                     (m.away_team = t.name AND m.away_score < m.home_score) THEN 1 ELSE 0 END) as losses,
                       sum(CASE WHEN m.home_team = t.name THEN m.home_score ELSE m.away_score END) as goals_for,
                       sum(CASE WHEN m.home_team = t.name THEN m.away_score ELSE m.home_score END) as goals_against
                ORDER BY (wins * 3 + draws) DESC, (goals_for - goals_against) DESC, goals_for DESC
                """

                result = await session.run(query, **params)
                standings = []
                position = 1

                async for record in result:
                    wins = record["wins"] or 0
                    draws = record["draws"] or 0
                    losses = record["losses"] or 0
                    goals_for = record["goals_for"] or 0
                    goals_against = record["goals_against"] or 0
                    matches_played = record["matches_played"] or 0

                    points = wins * 3 + draws
                    goal_difference = goals_for - goals_against

                    team_data = {
                        "position": position,
                        "team": record["team"],
                        "matches_played": matches_played,
                        "wins": wins,
                        "draws": draws,
                        "losses": losses,
                        "goals_for": goals_for,
                        "goals_against": goals_against,
                        "goal_difference": goal_difference,
                        "points": points
                    }
                    standings.append(team_data)
                    position += 1

                response = {
                    "competition": {
                        "name": competition,
                        "season": season or "current"
                    },
                    "last_updated": datetime.now().isoformat(),
                    "standings": standings
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting competition standings: {e}")
            return {
                "error": f"Failed to get competition standings: {str(e)}",
                "competition": competition
            }

    async def get_competition_top_scorers(self, competition: str,
                                         season: Optional[str] = None,
                                         limit: int = 10) -> Dict[str, Any]:
        """Get top scorers for a competition"""

        cache_key = f"competition_top_scorers_{competition}_{season or 'current'}_{limit}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get top scorers
                query = """
                MATCH (c:Competition {name: $competition})
                """

                params = {"competition": competition, "limit": limit}

                if season:
                    query += " WHERE c.season = $season"
                    params["season"] = season

                query += """
                MATCH (m:Match)-[:PART_OF]->(c)
                MATCH (p:Player)-[:PLAYED_IN]->(m)
                MATCH (p)-[:PLAYS_FOR]->(t:Team)
                RETURN p.name as player,
                       p.position as position,
                       t.name as team,
                       sum(CASE WHEN m.goals_for IS NOT NULL THEN m.goals_for ELSE 0 END) as goals,
                       sum(CASE WHEN m.assists IS NOT NULL THEN m.assists ELSE 0 END) as assists,
                       count(DISTINCT m) as matches_played
                ORDER BY goals DESC, assists DESC
                LIMIT $limit
                """

                result = await session.run(query, **params)
                top_scorers = []
                position = 1

                async for record in result:
                    scorer_data = {
                        "position": position,
                        "player": record["player"],
                        "team": record["team"],
                        "player_position": record["position"],
                        "goals": record["goals"] or 0,
                        "assists": record["assists"] or 0,
                        "matches_played": record["matches_played"] or 0,
                        "goals_per_match": round((record["goals"] or 0) / max(record["matches_played"] or 1, 1), 2)
                    }
                    top_scorers.append(scorer_data)
                    position += 1

                response = {
                    "competition": {
                        "name": competition,
                        "season": season or "current"
                    },
                    "last_updated": datetime.now().isoformat(),
                    "top_scorers": top_scorers
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting top scorers: {e}")
            return {
                "error": f"Failed to get top scorers: {str(e)}",
                "competition": competition
            }
    async def search_matches_by_date(self, start_date: str, end_date: str, limit: int = 50) -> Dict[str, Any]:
        """Search for matches within a date range."""
        try:
            query = """
                MATCH (m:Match)
                WHERE m.date >= $start_date AND m.date <= $end_date
                OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)
                RETURN m.id as match_id,
                       m.date as date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       c.name as competition
                ORDER BY m.date DESC
                LIMIT $limit
                """

            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                records = [record async for record in result]

                matches = []
                for record in records:
                    matches.append({
                        "match_id": record["match_id"],
                        "date": str(record["date"]) if record["date"] else None,
                        "home_team": record["home_team"],
                        "away_team": record["away_team"],
                        "home_score": record["home_score"],
                        "away_score": record["away_score"],
                        "competition": record["competition"]
                    })

                return {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_found": len(matches),
                    "matches": matches
                }

        except Exception as e:
            logger.error(f"Failed to search matches by date: {e}")
            return {
                "error": f"Failed to search matches by date: {str(e)}",
                "start_date": start_date,
                "end_date": end_date,
                "matches": []
            }

    async def get_competition_info(self, competition_id: str) -> Dict[str, Any]:
        """Get competition information."""
        try:
            # Handle both ID and name
            comp_name = competition_id.replace("comp_", "Competition ")

            query = """
                MATCH (c:Competition)
                WHERE c.id = $competition_id OR c.name = $comp_name OR toLower(c.name) CONTAINS toLower($competition_id)
                OPTIONAL MATCH (c)<-[:PART_OF]-(m:Match)
                OPTIONAL MATCH (m)<-[:HOME_TEAM|AWAY_TEAM]-(t:Team)
                RETURN c.name as name,
                       c.season as season,
                       c.type as type,
                       count(DISTINCT m) as total_matches,
                       count(DISTINCT t) as total_teams,
                       collect(DISTINCT t.name)[..5] as sample_teams
                """

            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    competition_id=competition_id,
                    comp_name=comp_name
                )
                record = await result.single()

                if not record:
                    return {
                        "error": "Competition not found",
                        "competition_id": competition_id,
                        "info": {}
                    }

                return {
                    "competition_id": competition_id,
                    "info": {
                        "name": record["name"],
                        "season": record["season"],
                        "type": record["type"],
                        "total_matches": record["total_matches"],
                        "total_teams": record["total_teams"],
                        "sample_teams": record["sample_teams"]
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get competition info: {e}")
            return {
                "error": f"Failed to get competition info: {str(e)}",
                "competition_id": competition_id,
                "info": {}
            }
