"""
Brazilian Soccer MCP Knowledge Graph - Extended Player Tools

CONTEXT:
This module adds missing player tool methods to complete the MCP implementation.

PHASE: 3 - Integration & Testing
PURPOSE: Complete player tool implementation
DATA SOURCES: Neo4j graph database
DEPENDENCIES: neo4j, asyncio

TECHNICAL DETAILS:
- Adds search_players_by_position method
- Adds compare_players method
- Async operations with Neo4j
"""

from typing import Dict, Any, List, Optional
from neo4j import AsyncDriver
import logging

logger = logging.getLogger(__name__)


class PlayerToolsExtensions:
    """Extensions for player tools."""

    async def search_players_by_position(self, position: str, limit: int = 20) -> Dict[str, Any]:
        """Search for players by position."""
        try:
            query = """
                MATCH (p:Player)
                WHERE toLower(p.position) = toLower($position)
                OPTIONAL MATCH (p)-[:PLAYS_FOR]->(t:Team)
                RETURN p.name as name,
                       p.position as position,
                       p.birth_date as birth_date,
                       p.nationality as nationality,
                       collect(DISTINCT t.name) as teams
                ORDER BY p.name
                LIMIT $limit
                """

            async with self.driver.session() as session:
                result = await session.run(query, position=position, limit=limit)
                records = await result.fetch_all()

                players = []
                for record in records:
                    players.append({
                        "name": record["name"],
                        "position": record["position"],
                        "birth_date": str(record["birth_date"]) if record["birth_date"] else None,
                        "nationality": record["nationality"],
                        "teams": record["teams"] if record["teams"] else []
                    })

                return {
                    "position": position,
                    "total_found": len(players),
                    "players": players
                }

        except Exception as e:
            logger.error(f"Failed to search players by position: {e}")
            return {
                "error": f"Failed to search players by position: {str(e)}",
                "position": position,
                "players": []
            }

    async def compare_players(self, player1_id: str, player2_id: str) -> Dict[str, Any]:
        """Compare two players."""
        try:
            # If IDs are like "player_0", extract the name or use as-is
            player1_name = player1_id.replace("player_", "Player ")
            player2_name = player2_id.replace("player_", "Player ")

            query = """
                MATCH (p1:Player)
                WHERE toLower(p1.name) CONTAINS toLower($player1_name) OR p1.id = $player1_id
                OPTIONAL MATCH (p1)-[:SCORED_IN]->(m1:Match)
                OPTIONAL MATCH (p1)-[:PLAYS_FOR]->(t1:Team)
                WITH p1, count(DISTINCT m1) as p1_goals, collect(DISTINCT t1.name) as p1_teams

                MATCH (p2:Player)
                WHERE toLower(p2.name) CONTAINS toLower($player2_name) OR p2.id = $player2_id
                OPTIONAL MATCH (p2)-[:SCORED_IN]->(m2:Match)
                OPTIONAL MATCH (p2)-[:PLAYS_FOR]->(t2:Team)
                WITH p1, p1_goals, p1_teams, p2, count(DISTINCT m2) as p2_goals, collect(DISTINCT t2.name) as p2_teams

                RETURN p1.name as player1_name,
                       p1.position as player1_position,
                       p1.nationality as player1_nationality,
                       p1_goals as player1_goals,
                       p1_teams as player1_teams,
                       p2.name as player2_name,
                       p2.position as player2_position,
                       p2.nationality as player2_nationality,
                       p2_goals as player2_goals,
                       p2_teams as player2_teams
                """

            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    player1_name=player1_name,
                    player1_id=player1_id,
                    player2_name=player2_name,
                    player2_id=player2_id
                )
                record = await result.single()

                if not record:
                    return {
                        "error": "Players not found",
                        "player1_id": player1_id,
                        "player2_id": player2_id
                    }

                return {
                    "player1": {
                        "name": record["player1_name"],
                        "position": record["player1_position"],
                        "nationality": record["player1_nationality"],
                        "goals": record["player1_goals"],
                        "teams": record["player1_teams"]
                    },
                    "player2": {
                        "name": record["player2_name"],
                        "position": record["player2_position"],
                        "nationality": record["player2_nationality"],
                        "goals": record["player2_goals"],
                        "teams": record["player2_teams"]
                    },
                    "comparison": {
                        "goals_difference": record["player1_goals"] - record["player2_goals"],
                        "both_same_position": record["player1_position"] == record["player2_position"],
                        "both_same_nationality": record["player1_nationality"] == record["player2_nationality"]
                    }
                }

        except Exception as e:
            logger.error(f"Failed to compare players: {e}")
            return {
                "error": f"Failed to compare players: {str(e)}",
                "player1_id": player1_id,
                "player2_id": player2_id
            }