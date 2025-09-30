#!/usr/bin/env python3
"""
Load Kaggle dataset into Neo4j database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KaggleDataLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "neo4j123")
        )

    def clear_database(self):
        """Clear all existing data."""
        with self.driver.session() as session:
            logger.info("Clearing existing database...")
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")

    def create_constraints(self):
        """Create uniqueness constraints."""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Player) REQUIRE p.player_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Team) REQUIRE t.team_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Match) REQUIRE m.match_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Competition) REQUIRE c.competition_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (co:Coach) REQUIRE co.coach_id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Stadium) REQUIRE s.name IS UNIQUE"
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint[:50]}...")
                except Exception as e:
                    logger.debug(f"Constraint might already exist: {e}")

    def load_teams(self):
        """Load teams data."""
        df = pd.read_csv("data/kaggle/teams.csv")

        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (t:Team {team_id: $team_id})
                    SET t.name = $name,
                        t.city = $city,
                        t.state = $state,
                        t.founded = $founded,
                        t.stadium = $stadium,
                        t.capacity = $capacity

                    MERGE (s:Stadium {name: $stadium})
                    SET s.capacity = $capacity,
                        s.city = $city

                    MERGE (t)-[:HOME_STADIUM]->(s)
                """, **row.to_dict())

            logger.info(f"Loaded {len(df)} teams")

    def load_players(self):
        """Load players data."""
        df = pd.read_csv("data/kaggle/players.csv")

        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (p:Player {player_id: $player_id})
                    SET p.name = $name,
                        p.full_name = $full_name,
                        p.position = $position,
                        p.birth_date = $birth_date,
                        p.nationality = $nationality,
                        p.height = $height,
                        p.weight = $weight
                """, **row.to_dict())

            logger.info(f"Loaded {len(df)} players")

    def load_competitions(self):
        """Load competitions data."""
        df = pd.read_csv("data/kaggle/competitions.csv")

        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (c:Competition {competition_id: $competition_id})
                    SET c.name = $name,
                        c.type = $type,
                        c.country = $country,
                        c.level = $level
                """, **row.to_dict())

            logger.info(f"Loaded {len(df)} competitions")

    def load_coaches(self):
        """Load coaches data."""
        df = pd.read_csv("data/kaggle/coaches.csv")

        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (c:Coach {coach_id: $coach_id})
                    SET c.name = $name,
                        c.full_name = $full_name,
                        c.birth_date = $birth_date,
                        c.nationality = $nationality
                """, **row.to_dict())

            logger.info(f"Loaded {len(df)} coaches")

    def load_matches(self):
        """Load matches data."""
        df = pd.read_csv("data/kaggle/matches.csv")

        with self.driver.session() as session:
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for _, row in batch.iterrows():
                    session.run("""
                        MATCH (ht:Team {team_id: $home_team})
                        MATCH (at:Team {team_id: $away_team})
                        MATCH (c:Competition {competition_id: $competition})

                        MERGE (m:Match {match_id: $match_id})
                        SET m.date = $date,
                            m.time = $time,
                            m.home_score = $home_score,
                            m.away_score = $away_score,
                            m.stadium = $stadium,
                            m.attendance = $attendance,
                            m.referee = $referee,
                            m.round = $round

                        MERGE (m)-[:HOME_TEAM]->(ht)
                        MERGE (m)-[:AWAY_TEAM]->(at)
                        MERGE (m)-[:PART_OF]->(c)

                        WITH m, $stadium as stadium_name
                        MATCH (s:Stadium {name: stadium_name})
                        MERGE (m)-[:HOSTED_AT]->(s)
                    """, **row.to_dict())

                logger.info(f"Loaded matches {i+1} to {min(i+batch_size, len(df))}")

            logger.info(f"Total matches loaded: {len(df)}")

    def load_player_stats(self):
        """Load player statistics."""
        df = pd.read_csv("data/kaggle/player_stats.csv")

        with self.driver.session() as session:
            batch_size = 200
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                for _, row in batch.iterrows():
                    # Create PLAYED_IN relationship
                    session.run("""
                        MATCH (p:Player {player_id: $player_id})
                        MATCH (m:Match {match_id: $match_id})
                        MATCH (t:Team {team_id: $team_id})

                        MERGE (p)-[r:PLAYED_IN]->(m)
                        SET r.minutes = $minutes_played,
                            r.rating = $rating,
                            r.team = $team_id

                        MERGE (p)-[:PLAYS_FOR]->(t)
                    """, **row.to_dict())

                    # Create SCORED_IN relationships for goals
                    if row['goals'] > 0:
                        session.run("""
                            MATCH (p:Player {player_id: $player_id})
                            MATCH (m:Match {match_id: $match_id})

                            MERGE (p)-[r:SCORED_IN]->(m)
                            SET r.goals = $goals
                        """, player_id=row['player_id'],
                            match_id=row['match_id'],
                            goals=row['goals'])

                    # Create ASSISTED_IN relationships
                    if row['assists'] > 0:
                        session.run("""
                            MATCH (p:Player {player_id: $player_id})
                            MATCH (m:Match {match_id: $match_id})

                            MERGE (p)-[r:ASSISTED_IN]->(m)
                            SET r.assists = $assists
                        """, player_id=row['player_id'],
                            match_id=row['match_id'],
                            assists=row['assists'])

                if (i + batch_size) % 1000 == 0:
                    logger.info(f"Loaded player stats {i+1} to {min(i+batch_size, len(df))}")

            logger.info(f"Total player stats loaded: {len(df)}")

    def load_transfers(self):
        """Load transfer data."""
        df = pd.read_csv("data/kaggle/transfers.csv")

        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (p:Player {player_id: $player_id})
                    MATCH (from:Team {team_id: $from_team})
                    MATCH (to:Team {team_id: $to_team})

                    CREATE (t:Transfer {
                        transfer_id: $transfer_id,
                        date: $date,
                        fee: $fee,
                        type: $type
                    })

                    MERGE (p)-[:TRANSFERRED]->(t)
                    MERGE (t)-[:FROM_TEAM]->(from)
                    MERGE (t)-[:TO_TEAM]->(to)
                """, **row.to_dict())

            logger.info(f"Loaded {len(df)} transfers")

    def verify_load(self):
        """Verify data was loaded correctly."""
        with self.driver.session() as session:
            # Count nodes
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)

            print("\n" + "=" * 60)
            print("DATABASE STATISTICS")
            print("=" * 60)
            print("\nNode counts:")
            total_nodes = 0
            for record in result:
                print(f"  {record['label']}: {record['count']:,}")
                total_nodes += record['count']

            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)

            print("\nRelationship counts:")
            total_rels = 0
            for record in result:
                print(f"  {record['type']}: {record['count']:,}")
                total_rels += record['count']

            print(f"\nTotal nodes: {total_nodes:,}")
            print(f"Total relationships: {total_rels:,}")

            return total_nodes, total_rels

    def close(self):
        """Close database connection."""
        self.driver.close()

    def run(self):
        """Run the complete data load process."""
        try:
            print("Starting Kaggle data load into Neo4j...")
            print("=" * 60)

            self.clear_database()
            self.create_constraints()

            print("\nLoading data...")
            self.load_teams()
            self.load_players()
            self.load_competitions()
            self.load_coaches()
            self.load_matches()
            self.load_player_stats()
            self.load_transfers()

            nodes, rels = self.verify_load()

            print("\n" + "=" * 60)
            print("DATA LOAD COMPLETE!")
            print("=" * 60)

            return nodes, rels

        finally:
            self.close()


if __name__ == "__main__":
    loader = KaggleDataLoader()
    loader.run()