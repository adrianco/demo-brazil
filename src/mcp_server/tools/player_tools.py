"""
Brazilian Soccer MCP Knowledge Graph - Player Tools

CONTEXT:
This module implements player-specific MCP tools for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying player data including search, statistics,
and career information stored in a Neo4j graph database.

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
- MCP Tools: Player search, stats, career queries
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class PlayerTools:
    """Player-specific MCP tools"""

    def __init__(self, driver, cache):
        self.driver = driver
        self.cache = cache
        self.cache_ttl = timedelta(minutes=30)

    async def search_player(self, name: str, limit: int = 10) -> Dict[str, Any]:
        """Search for players by name or partial name"""
        cache_key = f"search_player_{name}_{limit}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Cypher query to search players
                query = """
                MATCH (p:Player)
                WHERE toLower(p.name) CONTAINS toLower($name)
                OPTIONAL MATCH (p)-[:PLAYS_FOR]->(t:Team)
                RETURN DISTINCT p.name as name,
                       p.position as position,
                       p.birth_date as birth_date,
                       p.nationality as nationality,
                       collect(DISTINCT t.name) as current_teams
                ORDER BY p.name
                LIMIT $limit
                """

                result = await session.run(query, name=name, limit=limit)
                players = []

                async for record in result:
                    player_data = {
                        "name": record["name"],
                        "position": record["position"],
                        "birth_date": record["birth_date"],
                        "nationality": record["nationality"],
                        "current_teams": record["current_teams"] or []
                    }
                    players.append(player_data)

                response = {
                    "query": name,
                    "total_found": len(players),
                    "players": players
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error searching players: {e}")
            return {
                "error": f"Failed to search players: {str(e)}",
                "query": name,
                "players": []
            }

    async def get_player_stats(self, player_name: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed statistics for a specific player"""
        cache_key = f"player_stats_{player_name}_{season or 'all'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Base query for player info
                player_query = """
                MATCH (p:Player {name: $player_name})
                RETURN p.name as name,
                       p.position as position,
                       p.birth_date as birth_date,
                       p.nationality as nationality,
                       p.height as height,
                       p.weight as weight
                """

                player_result = await session.run(player_query, player_name=player_name)
                player_record = await player_result.single()

                if not player_record:
                    return {"error": f"Player '{player_name}' not found"}

                # Get match statistics
                stats_query = """
                MATCH (p:Player {name: $player_name})-[:PLAYED_IN]->(m:Match)
                """

                if season:
                    stats_query += " WHERE m.season = $season"

                stats_query += """
                OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)
                RETURN count(m) as matches_played,
                       sum(CASE WHEN m.goals_for IS NOT NULL THEN m.goals_for ELSE 0 END) as total_goals,
                       sum(CASE WHEN m.assists IS NOT NULL THEN m.assists ELSE 0 END) as total_assists,
                       sum(CASE WHEN m.yellow_cards IS NOT NULL THEN m.yellow_cards ELSE 0 END) as yellow_cards,
                       sum(CASE WHEN m.red_cards IS NOT NULL THEN m.red_cards ELSE 0 END) as red_cards,
                       collect(DISTINCT c.name) as competitions
                """

                params = {"player_name": player_name}
                if season:
                    params["season"] = season

                stats_result = await session.run(stats_query, **params)
                stats_record = await stats_result.single()

                # Get team history
                team_query = """
                MATCH (p:Player {name: $player_name})-[r:PLAYS_FOR]->(t:Team)
                RETURN t.name as team_name,
                       r.start_date as start_date,
                       r.end_date as end_date,
                       r.jersey_number as jersey_number
                ORDER BY r.start_date DESC
                """

                team_result = await session.run(team_query, player_name=player_name)
                teams = []
                async for record in team_result:
                    teams.append({
                        "team": record["team_name"],
                        "start_date": record["start_date"],
                        "end_date": record["end_date"],
                        "jersey_number": record["jersey_number"]
                    })

                # Compile response
                response = {
                    "player": {
                        "name": player_record["name"],
                        "position": player_record["position"],
                        "birth_date": player_record["birth_date"],
                        "nationality": player_record["nationality"],
                        "height": player_record["height"],
                        "weight": player_record["weight"]
                    },
                    "statistics": {
                        "matches_played": stats_record["matches_played"] or 0,
                        "goals": stats_record["total_goals"] or 0,
                        "assists": stats_record["total_assists"] or 0,
                        "yellow_cards": stats_record["yellow_cards"] or 0,
                        "red_cards": stats_record["red_cards"] or 0,
                        "competitions": stats_record["competitions"] or []
                    },
                    "teams": teams,
                    "season": season or "all_time"
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {
                "error": f"Failed to get player stats: {str(e)}",
                "player_name": player_name
            }

    async def get_player_career(self, player_name: str) -> Dict[str, Any]:
        """Get career history and teams for a player"""
        cache_key = f"player_career_{player_name}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Get player basic info
                player_query = """
                MATCH (p:Player {name: $player_name})
                RETURN p.name as name,
                       p.position as position,
                       p.birth_date as birth_date,
                       p.nationality as nationality
                """

                player_result = await session.run(player_query, player_name=player_name)
                player_record = await player_result.single()

                if not player_record:
                    return {"error": f"Player '{player_name}' not found"}

                # Get detailed career history
                career_query = """
                MATCH (p:Player {name: $player_name})-[r:PLAYS_FOR]->(t:Team)
                OPTIONAL MATCH (p)-[:PLAYED_IN]->(m:Match)<-[:PARTICIPATED_IN]-(t)
                OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)
                RETURN t.name as team_name,
                       t.city as team_city,
                       r.start_date as start_date,
                       r.end_date as end_date,
                       r.jersey_number as jersey_number,
                       r.transfer_fee as transfer_fee,
                       count(DISTINCT m) as matches_played,
                       sum(CASE WHEN m.goals_for IS NOT NULL THEN m.goals_for ELSE 0 END) as goals,
                       collect(DISTINCT c.name) as competitions
                ORDER BY r.start_date DESC
                """

                career_result = await session.run(career_query, player_name=player_name)
                career_history = []

                async for record in career_result:
                    career_entry = {
                        "team": record["team_name"],
                        "city": record["team_city"],
                        "period": {
                            "start": record["start_date"],
                            "end": record["end_date"]
                        },
                        "jersey_number": record["jersey_number"],
                        "transfer_fee": record["transfer_fee"],
                        "performance": {
                            "matches": record["matches_played"] or 0,
                            "goals": record["goals"] or 0
                        },
                        "competitions": record["competitions"] or []
                    }
                    career_history.append(career_entry)

                # Get achievements and honors
                achievements_query = """
                MATCH (p:Player {name: $player_name})-[:PLAYED_IN]->(m:Match)-[:PART_OF]->(c:Competition)
                WHERE m.result = 'win' OR c.type = 'championship'
                RETURN c.name as competition,
                       c.season as season,
                       count(m) as appearances
                ORDER BY c.season DESC
                """

                achievements_result = await session.run(achievements_query, player_name=player_name)
                achievements = []

                async for record in achievements_result:
                    achievements.append({
                        "competition": record["competition"],
                        "season": record["season"],
                        "appearances": record["appearances"]
                    })

                # Calculate career totals
                total_matches = sum(entry["performance"]["matches"] for entry in career_history)
                total_goals = sum(entry["performance"]["goals"] for entry in career_history)
                total_teams = len(career_history)

                response = {
                    "player": {
                        "name": player_record["name"],
                        "position": player_record["position"],
                        "birth_date": player_record["birth_date"],
                        "nationality": player_record["nationality"]
                    },
                    "career_summary": {
                        "total_teams": total_teams,
                        "total_matches": total_matches,
                        "total_goals": total_goals,
                        "career_span": {
                            "start": min((entry["period"]["start"] for entry in career_history if entry["period"]["start"]), default=None),
                            "end": max((entry["period"]["end"] for entry in career_history if entry["period"]["end"]), default="Present")
                        }
                    },
                    "career_history": career_history,
                    "achievements": achievements
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting player career: {e}")
            return {
                "error": f"Failed to get player career: {str(e)}",
                "player_name": player_name
            }