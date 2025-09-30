"""
Brazilian Soccer MCP Knowledge Graph - Analysis Tools

CONTEXT:
This module implements complex analysis MCP tools for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for advanced queries including common teammates analysis,
rivalry statistics, and other complex relationship queries stored in a Neo4j graph database.

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
- MCP Tools: Complex analysis queries for relationships
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AnalysisTools:
    """Complex analysis MCP tools"""

    def __init__(self, driver, cache):
        self.driver = driver
        self.cache = cache
        self.cache_ttl = timedelta(minutes=30)

    async def find_common_teammates(self, players: List[str],
                                   team: Optional[str] = None) -> Dict[str, Any]:
        """Find players who were teammates with specific players"""

        cache_key = f"common_teammates_{'_'.join(sorted(players))}_{team or 'any'}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                if len(players) < 2:
                    return {"error": "Need at least 2 players to find common teammates"}

                # Build query to find common teammates
                query = """
                // Find all players who played for the same teams as ALL specified players
                MATCH (p1:Player)-[:PLAYS_FOR]->(t:Team)<-[:PLAYS_FOR]-(common:Player)
                WHERE p1.name IN $players
                """

                params = {"players": players}

                if team:
                    query += " AND t.name = $team"
                    params["team"] = team

                query += """
                // Ensure the common player played with ALL specified players
                WITH common, t, collect(DISTINCT p1.name) as connected_players
                WHERE size(connected_players) = size($players)
                AND NOT common.name IN $players

                // Get overlap periods and match details
                MATCH (common)-[r1:PLAYS_FOR]->(t)
                OPTIONAL MATCH (specified:Player)-[r2:PLAYS_FOR]->(t)
                WHERE specified.name IN $players

                RETURN common.name as teammate_name,
                       common.position as position,
                       t.name as team_name,
                       r1.start_date as start_date,
                       r1.end_date as end_date,
                       collect(DISTINCT {
                           player: specified.name,
                           overlap_start: CASE
                               WHEN r1.start_date > r2.start_date THEN r1.start_date
                               ELSE r2.start_date
                           END,
                           overlap_end: CASE
                               WHEN r1.end_date IS NULL AND r2.end_date IS NULL THEN null
                               WHEN r1.end_date IS NULL THEN r2.end_date
                               WHEN r2.end_date IS NULL THEN r1.end_date
                               WHEN r1.end_date < r2.end_date THEN r1.end_date
                               ELSE r2.end_date
                           END
                       }) as overlaps
                ORDER BY teammate_name, team_name
                """

                result = await session.run(query, **params)
                teammates = []

                async for record in result:
                    # Calculate total overlap periods
                    overlaps = record["overlaps"]
                    valid_overlaps = []

                    for overlap in overlaps:
                        if overlap["player"] and overlap["overlap_start"]:
                            # Check if overlap is valid (start <= end)
                            if (overlap["overlap_end"] is None or
                                overlap["overlap_start"] <= overlap["overlap_end"]):
                                valid_overlaps.append(overlap)

                    if valid_overlaps:  # Only include if there are valid overlaps
                        teammate_data = {
                            "name": record["teammate_name"],
                            "position": record["position"],
                            "team": record["team_name"],
                            "period": {
                                "start": record["start_date"],
                                "end": record["end_date"]
                            },
                            "overlaps_with": valid_overlaps,
                            "overlap_count": len(valid_overlaps)
                        }
                        teammates.append(teammate_data)

                # Get match statistics for common teammates
                if teammates:
                    stats_query = """
                    MATCH (common:Player)-[:PLAYED_IN]->(m:Match)
                    WHERE common.name IN $teammate_names
                    MATCH (specified:Player)-[:PLAYED_IN]->(m)
                    WHERE specified.name IN $players

                    RETURN common.name as teammate,
                           specified.name as played_with,
                           count(m) as matches_together,
                           sum(CASE WHEN m.result = 'win' THEN 1 ELSE 0 END) as wins_together
                    ORDER BY teammate, played_with
                    """

                    teammate_names = [t["name"] for t in teammates]
                    stats_result = await session.run(stats_query,
                                                   teammate_names=teammate_names,
                                                   players=players)

                    # Add match stats to teammates
                    match_stats = {}
                    async for stats_record in stats_result:
                        teammate = stats_record["teammate"]
                        if teammate not in match_stats:
                            match_stats[teammate] = []
                        match_stats[teammate].append({
                            "played_with": stats_record["played_with"],
                            "matches_together": stats_record["matches_together"] or 0,
                            "wins_together": stats_record["wins_together"] or 0
                        })

                    for teammate in teammates:
                        teammate["match_statistics"] = match_stats.get(teammate["name"], [])

                # Group by team for better organization
                teams_analysis = {}
                for teammate in teammates:
                    team = teammate["team"]
                    if team not in teams_analysis:
                        teams_analysis[team] = []
                    teams_analysis[team].append(teammate)

                response = {
                    "search_criteria": {
                        "players": players,
                        "team_filter": team,
                        "total_players_searched": len(players)
                    },
                    "summary": {
                        "total_common_teammates": len(teammates),
                        "teams_involved": len(teams_analysis),
                        "teams_list": list(teams_analysis.keys())
                    },
                    "common_teammates": teammates,
                    "by_team": teams_analysis
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error finding common teammates: {e}")
            return {
                "error": f"Failed to find common teammates: {str(e)}",
                "players": players
            }

    async def get_rivalry_stats(self, team1: str, team2: str,
                               years: int = 10) -> Dict[str, Any]:
        """Get detailed rivalry statistics and history"""

        cache_key = f"rivalry_stats_{team1}_{team2}_{years}"

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data

        try:
            async with self.driver.session() as session:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date.replace(year=end_date.year - years)

                # Get comprehensive rivalry data
                query = """
                MATCH (m:Match)
                WHERE (m.home_team = $team1 AND m.away_team = $team2) OR
                      (m.home_team = $team2 AND m.away_team = $team1)
                AND m.date >= $start_date

                OPTIONAL MATCH (m)-[:PART_OF]->(c:Competition)

                // Get match details with goals and cards
                OPTIONAL MATCH (p:Player)-[:PLAYED_IN]->(m)
                OPTIONAL MATCH (p)-[:PLAYS_FOR]->(t:Team)
                WHERE t.name IN [$team1, $team2]

                RETURN m.date as date,
                       m.home_team as home_team,
                       m.away_team as away_team,
                       m.home_score as home_score,
                       m.away_score as away_score,
                       m.venue as venue,
                       m.attendance as attendance,
                       c.name as competition,
                       c.season as season,
                       collect(DISTINCT {
                           player: p.name,
                           team: t.name,
                           goals: COALESCE(p.goals_in_match, 0),
                           cards: COALESCE(p.cards_in_match, [])
                       }) as player_stats
                ORDER BY m.date DESC
                """

                params = {
                    "team1": team1,
                    "team2": team2,
                    "start_date": start_date.strftime("%Y-%m-%d")
                }

                result = await session.run(query, **params)
                matches = []
                team1_stats = {"wins": 0, "goals": 0, "home_wins": 0, "away_wins": 0}
                team2_stats = {"wins": 0, "goals": 0, "home_wins": 0, "away_wins": 0}
                draws = 0
                total_goals = 0
                total_attendance = 0
                competitions = set()
                venues = {}

                async for record in result:
                    home_team = record["home_team"]
                    away_team = record["away_team"]
                    home_score = record["home_score"] or 0
                    away_score = record["away_score"] or 0

                    total_goals += home_score + away_score
                    if record["attendance"]:
                        total_attendance += record["attendance"]

                    venue = record["venue"]
                    if venue:
                        venues[venue] = venues.get(venue, 0) + 1

                    if record["competition"]:
                        competitions.add(record["competition"])

                    # Calculate stats from team1's perspective
                    if home_team == team1:
                        team1_goals = home_score
                        team2_goals = away_score
                        is_team1_home = True
                    else:
                        team1_goals = away_score
                        team2_goals = home_score
                        is_team1_home = False

                    team1_stats["goals"] += team1_goals
                    team2_stats["goals"] += team2_goals

                    # Determine winner
                    if team1_goals > team2_goals:
                        team1_stats["wins"] += 1
                        if is_team1_home:
                            team1_stats["home_wins"] += 1
                        else:
                            team1_stats["away_wins"] += 1
                        winner = team1
                    elif team2_goals > team1_goals:
                        team2_stats["wins"] += 1
                        if not is_team1_home:
                            team2_stats["home_wins"] += 1
                        else:
                            team2_stats["away_wins"] += 1
                        winner = team2
                    else:
                        draws += 1
                        winner = "Draw"

                    # Process player stats
                    top_scorers = []
                    cards_given = []
                    for player_stat in record["player_stats"]:
                        if player_stat["goals"] and player_stat["goals"] > 0:
                            top_scorers.append({
                                "player": player_stat["player"],
                                "team": player_stat["team"],
                                "goals": player_stat["goals"]
                            })
                        if player_stat["cards"] and len(player_stat["cards"]) > 0:
                            cards_given.extend([{
                                "player": player_stat["player"],
                                "team": player_stat["team"],
                                "cards": player_stat["cards"]
                            }])

                    match_data = {
                        "date": record["date"],
                        "home_team": home_team,
                        "away_team": away_team,
                        "score": f"{home_score}-{away_score}",
                        "winner": winner,
                        "venue": venue,
                        "attendance": record["attendance"],
                        "competition": record["competition"],
                        "season": record["season"],
                        "goal_scorers": top_scorers,
                        "cards": cards_given
                    }
                    matches.append(match_data)

                # Calculate additional statistics
                total_matches = len(matches)
                if total_matches > 0:
                    team1_win_pct = team1_stats["wins"] / total_matches * 100
                    team2_win_pct = team2_stats["wins"] / total_matches * 100
                    draw_pct = draws / total_matches * 100
                    avg_goals_per_match = total_goals / total_matches
                    avg_attendance = total_attendance / total_matches if total_attendance > 0 else 0
                else:
                    team1_win_pct = team2_win_pct = draw_pct = avg_goals_per_match = avg_attendance = 0

                # Get head-to-head records by competition
                competition_breakdown = {}
                for match in matches:
                    comp = match["competition"] or "Unknown"
                    if comp not in competition_breakdown:
                        competition_breakdown[comp] = {
                            "matches": 0, "team1_wins": 0, "team2_wins": 0, "draws": 0
                        }

                    competition_breakdown[comp]["matches"] += 1
                    if match["winner"] == team1:
                        competition_breakdown[comp]["team1_wins"] += 1
                    elif match["winner"] == team2:
                        competition_breakdown[comp]["team2_wins"] += 1
                    else:
                        competition_breakdown[comp]["draws"] += 1

                # Analyze trends (wins by year)
                yearly_trends = {}
                for match in matches:
                    year = match["date"][:4] if match["date"] else "Unknown"
                    if year not in yearly_trends:
                        yearly_trends[year] = {"team1_wins": 0, "team2_wins": 0, "draws": 0}

                    if match["winner"] == team1:
                        yearly_trends[year]["team1_wins"] += 1
                    elif match["winner"] == team2:
                        yearly_trends[year]["team2_wins"] += 1
                    else:
                        yearly_trends[year]["draws"] += 1

                # Most common venues
                top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:5]

                response = {
                    "rivalry": {
                        "team1": team1,
                        "team2": team2,
                        "period": f"{start_date.year}-{end_date.year}",
                        "years_analyzed": years
                    },
                    "overall_record": {
                        "total_matches": total_matches,
                        "team1_wins": team1_stats["wins"],
                        "team2_wins": team2_stats["wins"],
                        "draws": draws,
                        "team1_win_percentage": round(team1_win_pct, 2),
                        "team2_win_percentage": round(team2_win_pct, 2),
                        "draw_percentage": round(draw_pct, 2)
                    },
                    "goals_analysis": {
                        "total_goals": total_goals,
                        "team1_goals": team1_stats["goals"],
                        "team2_goals": team2_stats["goals"],
                        "average_goals_per_match": round(avg_goals_per_match, 2),
                        "team1_avg_goals": round(team1_stats["goals"] / max(total_matches, 1), 2),
                        "team2_avg_goals": round(team2_stats["goals"] / max(total_matches, 1), 2)
                    },
                    "home_away_analysis": {
                        "team1_home_wins": team1_stats["home_wins"],
                        "team1_away_wins": team1_stats["away_wins"],
                        "team2_home_wins": team2_stats["home_wins"],
                        "team2_away_wins": team2_stats["away_wins"]
                    },
                    "competition_breakdown": competition_breakdown,
                    "yearly_trends": yearly_trends,
                    "venue_analysis": {
                        "total_venues": len(venues),
                        "average_attendance": round(avg_attendance, 0),
                        "most_common_venues": top_venues
                    },
                    "competitions_involved": list(competitions),
                    "recent_matches": matches[:10],  # Last 10 matches
                    "all_matches": matches
                }

                # Cache the result
                self.cache[cache_key] = (response, datetime.now())
                return response

        except Exception as e:
            logger.error(f"Error getting rivalry stats: {e}")
            return {
                "error": f"Failed to get rivalry stats: {str(e)}",
                "teams": {"team1": team1, "team2": team2}
            }