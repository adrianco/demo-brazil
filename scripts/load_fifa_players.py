#!/usr/bin/env python3
"""
Load FIFA player data into Neo4j, focusing on Brazilian players in Serie A.

This script loads player data from FIFA CSV files and creates:
- Player nodes with detailed attributes (overall rating, positions, stats)
- PLAYS_FOR relationships linking players to their clubs
"""

import pandas as pd
from neo4j import GraphDatabase
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FIFAPlayerLoader:
    """Load FIFA player data into Neo4j."""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "neo4j123"):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.data_dir = Path("data/kaggle")

        # Team name normalization mapping
        self.team_name_mapping = {
            # FIFA name -> Neo4j team name (match exact names from Neo4j)
            "Grêmio": "Grêmio",
            "RB Bragantino": "Bragantino",
            "Clube Atlético Mineiro": "Atlético - MG",  # Note the spaces
            "Sport Club Corinthians Paulista": "Corinthians",
            "Flamengo": "Flamengo",
            "Fluminense": "Fluminense",
            "Internacional": "Internacional",
            "Fortaleza": "Fortaleza",
            "Santos": "Santos",
            "São Paulo": "São Paulo",
            "Palmeiras": "Palmeiras",
            "Ceará Sporting Club": "Ceará - CE",
            "Club Athletico Paranaense": "Athletico Paranaense - PR",
            "Juventude": "Juventude",
            "Bahia": "Bahia",
            "Atlético Clube Goianiense": "Atlético - GO",
            "Cuiabá": "Cuiabá - MT",
            "Associação Chapecoense de Futebol": "Chapecoense",
            # Additional variations
            "Athletico-PR": "Athletico Paranaense - PR",
            "Atlético Mineiro": "Atlético - MG",
            "America MG": "América-MG",
            "América-MG": "América-MG",
        }

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    def create_player_constraint(self):
        """Create uniqueness constraint for players."""
        logger.info("Creating player constraint...")

        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT player_sofifa_id IF NOT EXISTS FOR (p:Player) REQUIRE p.sofifa_id IS UNIQUE")
                logger.info("Player constraint created")
            except Exception as e:
                logger.warning(f"Constraint creation warning: {e}")

    def normalize_team_name(self, fifa_club_name: str) -> Optional[str]:
        """Normalize FIFA club names to match Neo4j team names."""
        if pd.isna(fifa_club_name):
            return None

        # Check direct mapping
        if fifa_club_name in self.team_name_mapping:
            return self.team_name_mapping[fifa_club_name]

        # Try partial matches
        fifa_lower = fifa_club_name.lower()
        for fifa_name, neo4j_name in self.team_name_mapping.items():
            if fifa_name.lower() in fifa_lower or fifa_lower in fifa_name.lower():
                return neo4j_name

        # Return original if no mapping found
        return fifa_club_name

    def check_team_exists(self, session, team_name: str) -> bool:
        """Check if a team exists in Neo4j."""
        result = session.run("""
            MATCH (t:Team {name: $name})
            RETURN count(t) > 0 as exists
        """, name=team_name)
        return result.single()['exists']

    def load_fifa_players(self, fifa_year: int = 22, nationality_filter: str = "Brazil", league_filter: str = "Campeonato Brasileiro Série A"):
        """
        Load FIFA players into Neo4j.

        Args:
            fifa_year: FIFA version year (15-22)
            nationality_filter: Filter by nationality (default: Brazil)
            league_filter: Filter by league (default: Serie A)
        """
        logger.info(f"Loading FIFA {fifa_year} players...")

        csv_file = self.data_dir / f"players_{fifa_year}.csv"
        if not csv_file.exists():
            logger.error(f"File not found: {csv_file}")
            return

        # Load and filter data
        df = pd.read_csv(csv_file, low_memory=False)

        # Apply filters
        if nationality_filter:
            df = df[df['nationality_name'] == nationality_filter]
            logger.info(f"Filtered to {len(df)} {nationality_filter} players")

        if league_filter:
            df = df[df['league_name'] == league_filter]
            logger.info(f"Filtered to {len(df)} players in {league_filter}")

        if len(df) == 0:
            logger.warning("No players found matching filters")
            return

        logger.info(f"Processing {len(df)} players from FIFA {fifa_year}...")

        players_added = 0
        players_skipped = 0
        teams_not_found = set()

        with self.driver.session() as session:
            for idx, row in df.iterrows():
                # Normalize team name
                fifa_club = row.get('club_name')
                if pd.isna(fifa_club):
                    players_skipped += 1
                    continue

                neo4j_team = self.normalize_team_name(fifa_club)

                # Check if team exists in Neo4j
                if not self.check_team_exists(session, neo4j_team):
                    teams_not_found.add(f"{fifa_club} -> {neo4j_team}")
                    players_skipped += 1
                    continue

                # Parse positions (can be multiple, e.g., "RW, ST, CF")
                positions_str = str(row.get('player_positions', ''))
                positions = [p.strip() for p in positions_str.split(',') if p.strip()]

                # Create player node with FIFA attributes
                try:
                    session.run("""
                        MATCH (t:Team {name: $team_name})

                        MERGE (p:Player {sofifa_id: $sofifa_id})
                        SET p.short_name = $short_name,
                            p.long_name = $long_name,
                            p.positions = $positions,
                            p.primary_position = $primary_position,
                            p.overall = $overall,
                            p.potential = $potential,
                            p.age = $age,
                            p.dob = $dob,
                            p.height_cm = $height_cm,
                            p.weight_kg = $weight_kg,
                            p.nationality = $nationality,
                            p.preferred_foot = $preferred_foot,
                            p.weak_foot = $weak_foot,
                            p.skill_moves = $skill_moves,
                            p.work_rate = $work_rate,
                            p.pace = $pace,
                            p.shooting = $shooting,
                            p.passing = $passing,
                            p.dribbling = $dribbling,
                            p.defending = $defending,
                            p.physic = $physic,
                            p.fifa_year = $fifa_year

                        MERGE (p)-[:PLAYS_FOR]->(t)
                    """,
                        sofifa_id=int(row['sofifa_id']),
                        short_name=str(row.get('short_name', '')),
                        long_name=str(row.get('long_name', '')),
                        positions=positions,
                        primary_position=positions[0] if positions else None,
                        overall=int(row['overall']) if pd.notna(row.get('overall')) else None,
                        potential=int(row['potential']) if pd.notna(row.get('potential')) else None,
                        age=int(row['age']) if pd.notna(row.get('age')) else None,
                        dob=str(row['dob']) if pd.notna(row.get('dob')) else None,
                        height_cm=int(row['height_cm']) if pd.notna(row.get('height_cm')) else None,
                        weight_kg=int(row['weight_kg']) if pd.notna(row.get('weight_kg')) else None,
                        nationality=str(row.get('nationality_name', '')),
                        preferred_foot=str(row.get('preferred_foot', '')) if pd.notna(row.get('preferred_foot')) else None,
                        weak_foot=int(row['weak_foot']) if pd.notna(row.get('weak_foot')) else None,
                        skill_moves=int(row['skill_moves']) if pd.notna(row.get('skill_moves')) else None,
                        work_rate=str(row.get('work_rate', '')) if pd.notna(row.get('work_rate')) else None,
                        pace=int(row['pace']) if pd.notna(row.get('pace')) else None,
                        shooting=int(row['shooting']) if pd.notna(row.get('shooting')) else None,
                        passing=int(row['passing']) if pd.notna(row.get('passing')) else None,
                        dribbling=int(row['dribbling']) if pd.notna(row.get('dribbling')) else None,
                        defending=int(row['defending']) if pd.notna(row.get('defending')) else None,
                        physic=int(row['physic']) if pd.notna(row.get('physic')) else None,
                        team_name=neo4j_team,
                        fifa_year=fifa_year
                    )
                    players_added += 1

                    if (players_added % 50) == 0:
                        logger.info(f"Processed {players_added} players...")

                except Exception as e:
                    logger.error(f"Error adding player {row.get('short_name')}: {e}")
                    players_skipped += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"FIFA {fifa_year} Player Import Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Players added: {players_added}")
        logger.info(f"Players skipped: {players_skipped}")

        if teams_not_found:
            logger.warning(f"\nTeams not found in Neo4j ({len(teams_not_found)}):")
            for team in sorted(teams_not_found):
                logger.warning(f"  - {team}")

    def print_summary(self):
        """Print database summary with player statistics."""
        logger.info("\n" + "="*60)
        logger.info("DATABASE SUMMARY")
        logger.info("="*60)

        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (p:Player) RETURN count(p) as count")
            players = result.single()['count']

            result = session.run("MATCH (t:Team) RETURN count(t) as count")
            teams = result.single()['count']

            result = session.run("MATCH (m:Match) RETURN count(m) as count")
            matches = result.single()['count']

            # Count PLAYS_FOR relationships
            result = session.run("MATCH (:Player)-[r:PLAYS_FOR]->(:Team) RETURN count(r) as count")
            plays_for = result.single()['count']

            # Get top rated players
            result = session.run("""
                MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
                RETURN p.short_name as name, t.name as team, p.overall as rating, p.positions as positions
                ORDER BY p.overall DESC
                LIMIT 10
            """)
            top_players = list(result)

            logger.info(f"Teams: {teams}")
            logger.info(f"Players: {players}")
            logger.info(f"Matches: {matches}")
            logger.info(f"PLAYS_FOR relationships: {plays_for}")

            if top_players:
                logger.info("\nTop 10 Players by Overall Rating:")
                for player in top_players:
                    positions = ', '.join(player['positions']) if player['positions'] else 'N/A'
                    logger.info(f"  {player['name']:20} ({player['team']:20}) - {player['rating']} - {positions}")

            logger.info("="*60 + "\n")


def main():
    """Main execution function."""
    loader = FIFAPlayerLoader()

    try:
        # Create constraint
        loader.create_player_constraint()

        # Load FIFA 22 players (Brazilian players in Serie A)
        loader.load_fifa_players(
            fifa_year=22,
            nationality_filter="Brazil",
            league_filter="Campeonato Brasileiro Série A"
        )

        # Print summary
        loader.print_summary()

    finally:
        loader.close()


if __name__ == "__main__":
    main()
