#!/usr/bin/env python3
"""
Load real Kaggle Brazilian football datasets into Neo4j.

This script loads four real Kaggle datasets:
- BR-Football-Dataset.csv: 10,297 matches with detailed statistics
- Brasileirao_Matches.csv: 4,181 league matches (2012+)
- Brazilian_Cup_Matches.csv: 1,338 cup matches
- Libertadores_Matches.csv: 1,256 continental matches
"""

import pandas as pd
from neo4j import GraphDatabase
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealKaggleDataLoader:
    """Load real Kaggle Brazilian football data into Neo4j."""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "neo4j123"):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.data_dir = Path("data/kaggle")

        # Track unique teams across all datasets
        self.all_teams: Set[str] = set()

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    def clear_database(self):
        """Clear all existing data from Neo4j."""
        logger.info("Clearing existing data from Neo4j...")

        with self.driver.session() as session:
            # Delete all relationships first
            session.run("MATCH ()-[r]-() DELETE r")
            # Then delete all nodes
            session.run("MATCH (n) DELETE n")

        logger.info("Database cleared successfully")

    def create_constraints(self):
        """Create uniqueness constraints for nodes."""
        logger.info("Creating constraints...")

        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT team_id IF NOT EXISTS FOR (t:Team) REQUIRE t.team_id IS UNIQUE",
                "CREATE CONSTRAINT match_id IF NOT EXISTS FOR (m:Match) REQUIRE m.match_id IS UNIQUE",
                "CREATE CONSTRAINT competition_name IF NOT EXISTS FOR (c:Competition) REQUIRE c.name IS UNIQUE"
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint creation warning: {e}")

        logger.info("Constraints created")

    def normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to handle variations."""
        if pd.isna(team_name):
            return None

        # Remove state codes (e.g., "Palmeiras-SP" -> "Palmeiras")
        team_name = str(team_name).strip()
        if '-' in team_name:
            # For Brasileirao format: "Palmeiras-SP"
            parts = team_name.split('-')
            if len(parts) == 2 and len(parts[1]) == 2:
                team_name = parts[0]

        # Normalize common variations
        normalizations = {
            "Sao Paulo": "São Paulo",
            "Atletico MG": "Atlético-MG",
            "Athletico Paranaense": "Athletico-PR",
            "Athletico-PR": "Athletico Paranaense",
            "America MG": "América-MG",
        }

        return normalizations.get(team_name, team_name)

    def create_team(self, session, team_name: str):
        """Create a team node if it doesn't exist."""
        normalized_name = self.normalize_team_name(team_name)
        if not normalized_name:
            return

        self.all_teams.add(normalized_name)

        # Create team_id from normalized name
        team_id = normalized_name.lower().replace(" ", "_").replace("-", "_")

        session.run("""
            MERGE (t:Team {team_id: $team_id})
            SET t.name = $name
        """, team_id=team_id, name=normalized_name)

    def create_competition(self, session, competition_name: str, competition_type: str):
        """Create a competition node."""
        session.run("""
            MERGE (c:Competition {name: $name})
            SET c.type = $type,
                c.country = 'Brazil'
        """, name=competition_name, type=competition_type)

    def load_br_football_dataset(self):
        """Load BR-Football-Dataset.csv with detailed match statistics."""
        logger.info("Loading BR-Football-Dataset.csv...")

        csv_file = self.data_dir / "BR-Football-Dataset.csv"
        df = pd.read_csv(csv_file)

        logger.info(f"Found {len(df)} matches in BR-Football-Dataset")

        with self.driver.session() as session:
            # Create competitions
            competitions = df['tournament'].unique()
            for comp in competitions:
                comp_type = "cup" if "Copa" in str(comp) or "Cup" in str(comp) else "league"
                self.create_competition(session, str(comp), comp_type)

            # Process matches in batches
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for idx, row in batch.iterrows():
                    # Create teams
                    self.create_team(session, row['home'])
                    self.create_team(session, row['away'])

                    # Normalize team names
                    home_team = self.normalize_team_name(row['home'])
                    away_team = self.normalize_team_name(row['away'])

                    if not home_team or not away_team:
                        continue

                    # Create match_id from date and teams
                    date_str = str(row['date'])
                    match_id = f"{date_str}_{home_team}_{away_team}".lower().replace(" ", "_").replace("-", "_")

                    # Create match with all statistics
                    session.run("""
                        MATCH (c:Competition {name: $competition})
                        MATCH (home:Team {name: $home_team})
                        MATCH (away:Team {name: $away_team})

                        MERGE (m:Match {match_id: $match_id})
                        SET m.date = $date,
                            m.time = $time,
                            m.home_score = $home_goal,
                            m.away_score = $away_goal,
                            m.home_corners = $home_corner,
                            m.away_corners = $away_corner,
                            m.home_attacks = $home_attack,
                            m.away_attacks = $away_attack,
                            m.home_shots = $home_shots,
                            m.away_shots = $away_shots,
                            m.total_corners = $total_corners,
                            m.ht_result = $ht_result,
                            m.at_result = $at_result

                        MERGE (home)-[:HOME_TEAM]->(m)
                        MERGE (away)-[:AWAY_TEAM]->(m)
                        MERGE (m)-[:PART_OF]->(c)
                    """,
                        competition=str(row['tournament']),
                        home_team=home_team,
                        away_team=away_team,
                        match_id=match_id,
                        date=date_str,
                        time=str(row['time']) if pd.notna(row['time']) else None,
                        home_goal=float(row['home_goal']) if pd.notna(row['home_goal']) else 0,
                        away_goal=float(row['away_goal']) if pd.notna(row['away_goal']) else 0,
                        home_corner=float(row['home_corner']) if pd.notna(row['home_corner']) else 0,
                        away_corner=float(row['away_corner']) if pd.notna(row['away_corner']) else 0,
                        home_attack=float(row['home_attack']) if pd.notna(row['home_attack']) else 0,
                        away_attack=float(row['away_attack']) if pd.notna(row['away_attack']) else 0,
                        home_shots=float(row['home_shots']) if pd.notna(row['home_shots']) else 0,
                        away_shots=float(row['away_shots']) if pd.notna(row['away_shots']) else 0,
                        total_corners=float(row['total_corners']) if pd.notna(row['total_corners']) else 0,
                        ht_result=str(row['ht_result']) if pd.notna(row['ht_result']) else None,
                        at_result=str(row['at_result']) if pd.notna(row['at_result']) else None
                    )

                if (i + batch_size) % 1000 == 0:
                    logger.info(f"Processed {i + batch_size} matches from BR-Football-Dataset")

        logger.info(f"Loaded {len(df)} matches from BR-Football-Dataset")

    def load_brasileirao_matches(self):
        """Load Brasileirao_Matches.csv league matches."""
        logger.info("Loading Brasileirao_Matches.csv...")

        csv_file = self.data_dir / "Brasileirao_Matches.csv"
        df = pd.read_csv(csv_file)

        logger.info(f"Found {len(df)} matches in Brasileirao dataset")

        with self.driver.session() as session:
            # Create Brasileirao competition
            self.create_competition(session, "Brasileirão Série A", "league")

            # Process matches in batches
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for idx, row in batch.iterrows():
                    # Create teams
                    self.create_team(session, row['home_team'])
                    self.create_team(session, row['away_team'])

                    # Normalize team names
                    home_team = self.normalize_team_name(row['home_team'])
                    away_team = self.normalize_team_name(row['away_team'])

                    if not home_team or not away_team:
                        continue

                    # Create match_id from datetime and teams
                    datetime_str = str(row['datetime'])
                    match_id = f"brasileirao_{datetime_str}_{home_team}_{away_team}".lower().replace(" ", "_").replace("-", "_").replace(":", "_")

                    # Create match
                    session.run("""
                        MATCH (c:Competition {name: 'Brasileirão Série A'})
                        MATCH (home:Team {name: $home_team})
                        MATCH (away:Team {name: $away_team})

                        MERGE (m:Match {match_id: $match_id})
                        SET m.datetime = $datetime,
                            m.season = $season,
                            m.round = $round,
                            m.home_score = $home_goal,
                            m.away_score = $away_goal,
                            m.home_state = $home_state,
                            m.away_state = $away_state

                        MERGE (home)-[:HOME_TEAM]->(m)
                        MERGE (away)-[:AWAY_TEAM]->(m)
                        MERGE (m)-[:PART_OF]->(c)
                    """,
                        home_team=home_team,
                        away_team=away_team,
                        match_id=match_id,
                        datetime=datetime_str,
                        season=int(row['season']) if pd.notna(row['season']) else None,
                        round=int(row['round']) if pd.notna(row['round']) else None,
                        home_goal=int(row['home_goal']) if pd.notna(row['home_goal']) else 0,
                        away_goal=int(row['away_goal']) if pd.notna(row['away_goal']) else 0,
                        home_state=str(row['home_team_state']) if pd.notna(row['home_team_state']) else None,
                        away_state=str(row['away_team_state']) if pd.notna(row['away_team_state']) else None
                    )

                if (i + batch_size) % 1000 == 0:
                    logger.info(f"Processed {i + batch_size} matches from Brasileirao")

        logger.info(f"Loaded {len(df)} matches from Brasileirao")

    def load_brazilian_cup_matches(self):
        """Load Brazilian_Cup_Matches.csv cup matches."""
        logger.info("Loading Brazilian_Cup_Matches.csv...")

        csv_file = self.data_dir / "Brazilian_Cup_Matches.csv"
        df = pd.read_csv(csv_file)

        logger.info(f"Found {len(df)} matches in Brazilian Cup dataset")

        with self.driver.session() as session:
            # Create Copa do Brasil competition
            self.create_competition(session, "Copa do Brasil", "cup")

            # Process matches in batches
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for idx, row in batch.iterrows():
                    # Create teams
                    self.create_team(session, row['home_team'])
                    self.create_team(session, row['away_team'])

                    # Normalize team names
                    home_team = self.normalize_team_name(row['home_team'])
                    away_team = self.normalize_team_name(row['away_team'])

                    if not home_team or not away_team:
                        continue

                    # Create match_id
                    datetime_str = str(row['datetime'])
                    match_id = f"copa_{datetime_str}_{home_team}_{away_team}".lower().replace(" ", "_").replace("-", "_").replace(":", "_")

                    # Create match
                    session.run("""
                        MATCH (c:Competition {name: 'Copa do Brasil'})
                        MATCH (home:Team {name: $home_team})
                        MATCH (away:Team {name: $away_team})

                        MERGE (m:Match {match_id: $match_id})
                        SET m.datetime = $datetime,
                            m.season = $season,
                            m.round = $round,
                            m.home_score = $home_goal,
                            m.away_score = $away_goal

                        MERGE (home)-[:HOME_TEAM]->(m)
                        MERGE (away)-[:AWAY_TEAM]->(m)
                        MERGE (m)-[:PART_OF]->(c)
                    """,
                        home_team=home_team,
                        away_team=away_team,
                        match_id=match_id,
                        datetime=datetime_str,
                        season=int(row['season']) if pd.notna(row['season']) else None,
                        round=str(row['round']) if pd.notna(row['round']) else None,
                        home_goal=int(row['home_goal']) if pd.notna(row['home_goal']) else 0,
                        away_goal=int(row['away_goal']) if pd.notna(row['away_goal']) else 0
                    )

                if (i + batch_size) % 500 == 0:
                    logger.info(f"Processed {i + batch_size} matches from Copa do Brasil")

        logger.info(f"Loaded {len(df)} matches from Copa do Brasil")

    def load_libertadores_matches(self):
        """Load Libertadores_Matches.csv continental matches."""
        logger.info("Loading Libertadores_Matches.csv...")

        csv_file = self.data_dir / "Libertadores_Matches.csv"
        df = pd.read_csv(csv_file)

        logger.info(f"Found {len(df)} matches in Libertadores dataset")

        with self.driver.session() as session:
            # Create Libertadores competition
            self.create_competition(session, "Copa Libertadores", "continental")

            # Process matches in batches
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for idx, row in batch.iterrows():
                    # Create teams (may include non-Brazilian teams)
                    self.create_team(session, row['home_team'])
                    self.create_team(session, row['away_team'])

                    # Normalize team names
                    home_team = self.normalize_team_name(row['home_team'])
                    away_team = self.normalize_team_name(row['away_team'])

                    if not home_team or not away_team:
                        continue

                    # Create match_id
                    datetime_str = str(row['datetime'])
                    match_id = f"libertadores_{datetime_str}_{home_team}_{away_team}".lower().replace(" ", "_").replace("-", "_").replace(":", "_")

                    # Parse goals (handle '-' or missing values)
                    try:
                        home_goal = int(row['home_goal']) if pd.notna(row['home_goal']) and str(row['home_goal']) != '-' else None
                    except (ValueError, TypeError):
                        home_goal = None

                    try:
                        away_goal = int(row['away_goal']) if pd.notna(row['away_goal']) and str(row['away_goal']) != '-' else None
                    except (ValueError, TypeError):
                        away_goal = None

                    # Create match
                    session.run("""
                        MATCH (c:Competition {name: 'Copa Libertadores'})
                        MATCH (home:Team {name: $home_team})
                        MATCH (away:Team {name: $away_team})

                        MERGE (m:Match {match_id: $match_id})
                        SET m.datetime = $datetime,
                            m.season = $season,
                            m.stage = $stage,
                            m.home_score = $home_goal,
                            m.away_score = $away_goal

                        MERGE (home)-[:HOME_TEAM]->(m)
                        MERGE (away)-[:AWAY_TEAM]->(m)
                        MERGE (m)-[:PART_OF]->(c)
                    """,
                        home_team=home_team,
                        away_team=away_team,
                        match_id=match_id,
                        datetime=datetime_str,
                        season=int(row['season']) if pd.notna(row['season']) else None,
                        stage=str(row['stage']) if pd.notna(row['stage']) else None,
                        home_goal=home_goal,
                        away_goal=away_goal
                    )

                if (i + batch_size) % 500 == 0:
                    logger.info(f"Processed {i + batch_size} matches from Libertadores")

        logger.info(f"Loaded {len(df)} matches from Copa Libertadores")

    def print_summary(self):
        """Print database summary statistics."""
        logger.info("\n" + "="*60)
        logger.info("DATABASE SUMMARY")
        logger.info("="*60)

        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (t:Team) RETURN count(t) as count")
            teams = result.single()['count']

            result = session.run("MATCH (m:Match) RETURN count(m) as count")
            matches = result.single()['count']

            result = session.run("MATCH (c:Competition) RETURN count(c) as count")
            competitions = result.single()['count']

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            relationships = result.single()['count']

            logger.info(f"Teams: {teams}")
            logger.info(f"Matches: {matches}")
            logger.info(f"Competitions: {competitions}")
            logger.info(f"Total Relationships: {relationships}")
            logger.info("="*60 + "\n")

    def load_all(self):
        """Load all Kaggle datasets into Neo4j."""
        logger.info("Starting real Kaggle data loading process...")

        # Clear existing data
        self.clear_database()

        # Create constraints
        self.create_constraints()

        # Load all datasets
        self.load_br_football_dataset()
        self.load_brasileirao_matches()
        self.load_brazilian_cup_matches()
        self.load_libertadores_matches()

        # Print summary
        self.print_summary()

        logger.info("Real Kaggle data loading complete!")


def main():
    """Main execution function."""
    loader = RealKaggleDataLoader()

    try:
        loader.load_all()
    finally:
        loader.close()


if __name__ == "__main__":
    main()
