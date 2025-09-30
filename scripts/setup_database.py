#!/usr/bin/env python3
"""
Brazilian Soccer MCP Knowledge Graph - Database Setup Script

This script initializes the Neo4j database with the complete schema including
constraints, indexes, and sample data for testing purposes.

Context Block:
- Purpose: Database initialization and schema setup
- Usage: Run once to set up the complete database schema
- Features: Creates constraints, indexes, and optional sample data
- Safety: Includes confirmation prompts for destructive operations
"""

import sys
import os
import argparse
from typing import List, Dict, Any
import yaml
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graph.connection import Neo4jConnection
from graph.schema import GraphSchema
from utils.config import load_config
from utils.logging import setup_logging, get_logger


def load_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """Load sample data for database initialization."""
    return {
        "teams": [
            {
                "team_id": "team_262",
                "name": "Flamengo",
                "short_name": "FLA",
                "founded": 1895,
                "city": "Rio de Janeiro",
                "state": "RJ",
                "country": "Brazil",
                "colors": ["Red", "Black"]
            },
            {
                "team_id": "team_275",
                "name": "Palmeiras",
                "short_name": "PAL",
                "founded": 1914,
                "city": "São Paulo",
                "state": "SP",
                "country": "Brazil",
                "colors": ["Green", "White"]
            },
            {
                "team_id": "team_276",
                "name": "São Paulo",
                "short_name": "SAO",
                "founded": 1930,
                "city": "São Paulo",
                "state": "SP",
                "country": "Brazil",
                "colors": ["Red", "White", "Black"]
            }
        ],
        "players": [
            {
                "player_id": "player_001",
                "name": "Gabriel Barbosa",
                "full_name": "Gabriel Barbosa Almeida",
                "birth_date": "1996-08-30",
                "nationality": "Brazil",
                "position": "Forward",
                "height": 1.78,
                "weight": 70.0,
                "preferred_foot": "Left",
                "market_value": 15000000,
                "jersey_number": 9
            },
            {
                "player_id": "player_002",
                "name": "Raphael Veiga",
                "full_name": "Raphael Cavalcante Veiga",
                "birth_date": "1995-06-19",
                "nationality": "Brazil",
                "position": "Midfielder",
                "height": 1.73,
                "weight": 68.0,
                "preferred_foot": "Left",
                "market_value": 8000000,
                "jersey_number": 23
            }
        ],
        "competitions": [
            {
                "competition_id": "brasileirao_2024",
                "name": "Campeonato Brasileiro Série A",
                "short_name": "Brasileirão",
                "type": "League",
                "level": 1,
                "country": "Brazil",
                "start_date": "2024-04-13",
                "end_date": "2024-12-08",
                "format": "Round Robin"
            }
        ],
        "stadiums": [
            {
                "stadium_id": "maracana",
                "name": "Estádio do Maracanã",
                "capacity": 78838,
                "city": "Rio de Janeiro",
                "state": "RJ",
                "country": "Brazil",
                "latitude": -22.9122,
                "longitude": -43.2302,
                "opened": 1950,
                "surface": "Grass"
            }
        ]
    }


class DatabaseSetup:
    """Database setup and initialization manager."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize database setup manager."""
        self.config = load_config(config_path)
        self.logger = get_logger(__name__)
        self.connection = Neo4jConnection(self.config["database"]["neo4j"])
        self.schema = GraphSchema()

    def check_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            result = self.connection.execute_query("RETURN 1 as test")
            self.logger.info("Database connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def clear_database(self, confirm: bool = False) -> None:
        """Clear all data from the database."""
        if not confirm:
            response = input("This will delete ALL data in the database. Continue? (yes/no): ")
            if response.lower() != 'yes':
                self.logger.info("Database clear cancelled")
                return

        self.logger.info("Clearing database...")
        try:
            # Delete all nodes and relationships
            self.connection.execute_query("MATCH (n) DETACH DELETE n")

            # Drop all constraints
            constraints_result = self.connection.execute_query("SHOW CONSTRAINTS")
            for constraint in constraints_result:
                constraint_name = constraint.get('name')
                if constraint_name:
                    self.connection.execute_query(f"DROP CONSTRAINT {constraint_name}")

            # Drop all indexes
            indexes_result = self.connection.execute_query("SHOW INDEXES")
            for index in indexes_result:
                index_name = index.get('name')
                if index_name and not index_name.startswith('system'):
                    self.connection.execute_query(f"DROP INDEX {index_name}")

            self.logger.info("Database cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")
            raise

    def create_schema(self) -> None:
        """Create database schema with constraints and indexes."""
        self.logger.info("Creating database schema...")

        try:
            schema_queries = self.schema.get_schema_creation_queries()

            for query in schema_queries:
                try:
                    self.connection.execute_query(query)
                    self.logger.debug(f"Executed: {query}")
                except Exception as e:
                    self.logger.warning(f"Query failed (may already exist): {query}")
                    self.logger.debug(f"Error: {e}")

            self.logger.info("Schema created successfully")
        except Exception as e:
            self.logger.error(f"Error creating schema: {e}")
            raise

    def load_sample_data(self) -> None:
        """Load sample data into the database."""
        self.logger.info("Loading sample data...")

        try:
            sample_data = load_sample_data()

            # Create teams
            for team in sample_data["teams"]:
                query = """
                CREATE (t:Team {
                    team_id: $team_id,
                    name: $name,
                    short_name: $short_name,
                    founded: $founded,
                    city: $city,
                    state: $state,
                    country: $country,
                    colors: $colors,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                """
                self.connection.execute_query(query, team)

            # Create players
            for player in sample_data["players"]:
                query = """
                CREATE (p:Player {
                    player_id: $player_id,
                    name: $name,
                    full_name: $full_name,
                    birth_date: date($birth_date),
                    nationality: $nationality,
                    position: $position,
                    height: $height,
                    weight: $weight,
                    preferred_foot: $preferred_foot,
                    market_value: $market_value,
                    jersey_number: $jersey_number,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                """
                self.connection.execute_query(query, player)

            # Create competitions
            for competition in sample_data["competitions"]:
                query = """
                CREATE (c:Competition {
                    competition_id: $competition_id,
                    name: $name,
                    short_name: $short_name,
                    type: $type,
                    level: $level,
                    country: $country,
                    start_date: date($start_date),
                    end_date: date($end_date),
                    format: $format,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                """
                self.connection.execute_query(query, competition)

            # Create stadiums
            for stadium in sample_data["stadiums"]:
                query = """
                CREATE (s:Stadium {
                    stadium_id: $stadium_id,
                    name: $name,
                    capacity: $capacity,
                    city: $city,
                    state: $state,
                    country: $country,
                    latitude: $latitude,
                    longitude: $longitude,
                    opened: $opened,
                    surface: $surface,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                """
                self.connection.execute_query(query, stadium)

            # Create some relationships
            # Gabriel Barbosa plays for Flamengo
            self.connection.execute_query("""
                MATCH (p:Player {player_id: 'player_001'}), (t:Team {team_id: 'team_262'})
                CREATE (p)-[:PLAYS_FOR {
                    start_date: date('2024-01-01'),
                    jersey_number: 9,
                    position: 'Forward',
                    contract_type: 'Professional'
                }]->(t)
            """)

            # Raphael Veiga plays for Palmeiras
            self.connection.execute_query("""
                MATCH (p:Player {player_id: 'player_002'}), (t:Team {team_id: 'team_275'})
                CREATE (p)-[:PLAYS_FOR {
                    start_date: date('2024-01-01'),
                    jersey_number: 23,
                    position: 'Midfielder',
                    contract_type: 'Professional'
                }]->(t)
            """)

            # Teams compete in Brasileirão
            self.connection.execute_query("""
                MATCH (t:Team), (c:Competition {competition_id: 'brasileirao_2024'})
                CREATE (t)-[:COMPETES_IN {
                    season: '2024',
                    matches_played: 0,
                    points: 0,
                    wins: 0,
                    draws: 0,
                    losses: 0,
                    goals_for: 0,
                    goals_against: 0
                }]->(c)
            """)

            self.logger.info("Sample data loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading sample data: {e}")
            raise

    def verify_setup(self) -> bool:
        """Verify that the database setup was successful."""
        self.logger.info("Verifying database setup...")

        try:
            # Check node counts
            node_counts = {}
            for label in ["Player", "Team", "Competition", "Stadium"]:
                result = self.connection.execute_query(f"MATCH (n:{label}) RETURN count(n) as count")
                node_counts[label] = result[0]["count"]

            # Check relationship counts
            rel_result = self.connection.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
            relationship_count = rel_result[0]["count"]

            # Check constraints
            constraints_result = self.connection.execute_query("SHOW CONSTRAINTS")
            constraint_count = len(constraints_result)

            # Check indexes
            indexes_result = self.connection.execute_query("SHOW INDEXES WHERE type = 'BTREE'")
            index_count = len(indexes_result)

            self.logger.info(f"Setup verification results:")
            self.logger.info(f"  Node counts: {node_counts}")
            self.logger.info(f"  Relationships: {relationship_count}")
            self.logger.info(f"  Constraints: {constraint_count}")
            self.logger.info(f"  Indexes: {index_count}")

            # Basic validation
            if all(count > 0 for count in node_counts.values()):
                self.logger.info("✅ Database setup verified successfully")
                return True
            else:
                self.logger.error("❌ Database setup verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Error verifying setup: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


def main():
    """Main function to run database setup."""
    parser = argparse.ArgumentParser(description="Setup Brazilian Soccer Knowledge Graph Database")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before setup")
    parser.add_argument("--no-sample-data", action="store_true", help="Skip loading sample data")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Starting Brazilian Soccer Database Setup")

    try:
        # Initialize setup manager
        setup_manager = DatabaseSetup(args.config)

        # Check connection
        if not setup_manager.check_connection():
            logger.error("Cannot connect to database. Please check your configuration.")
            sys.exit(1)

        if args.verify_only:
            # Only verify existing setup
            success = setup_manager.verify_setup()
            sys.exit(0 if success else 1)

        # Clear database if requested
        if args.clear:
            setup_manager.clear_database(confirm=args.force)

        # Create schema
        setup_manager.create_schema()

        # Load sample data unless skipped
        if not args.no_sample_data:
            setup_manager.load_sample_data()

        # Verify setup
        success = setup_manager.verify_setup()

        if success:
            logger.info("🎉 Database setup completed successfully!")
            logger.info("You can now start the MCP server with: python -m src.mcp_server.server")
        else:
            logger.error("❌ Database setup failed verification")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
    finally:
        if 'setup_manager' in locals():
            setup_manager.close()


if __name__ == "__main__":
    main()