#!/usr/bin/env python3
"""
Load Brazilian Soccer data using the Kaggle data pipeline
"""

import sys
sys.path.insert(0, '/workspaces/demo-brazil')

from src.graph.database import Neo4jDatabase
from src.graph.models import GraphSchema
from src.data_pipeline.kaggle_loader import KaggleLoader
from src.data_pipeline.graph_builder import GraphBuilder

def main():
    print("=" * 60)
    print("LOADING BRAZILIAN SOCCER DATA FROM KAGGLE PIPELINE")
    print("=" * 60)

    # Initialize database connection
    print("\n📡 Connecting to Neo4j...")
    db = Neo4jDatabase(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="neo4j123"
    )
    db.connect()

    # Test connection
    if db.test_connection():
        print("✅ Connected to Neo4j successfully")
    else:
        print("❌ Failed to connect to Neo4j")
        return

    # Clear existing data
    print("\n🗑️ Clearing existing data...")
    db.clear_database()
    print("✅ Database cleared")

    # Create schema
    print("\n📝 Creating database schema...")
    schema = GraphSchema(db)
    schema.create_schema()
    print("✅ Schema created with constraints and indexes")

    # Load data using Kaggle loader
    print("\n📥 Loading data from Kaggle pipeline...")
    loader = KaggleLoader()

    # Generate comprehensive sample data (simulating Kaggle dataset)
    data = loader.generate_sample_data(num_matches=50)  # Generate 50 matches worth of data

    print(f"\n📊 Data loaded from pipeline:")
    print(f"  - Teams: {len(data['teams'])}")
    print(f"  - Players: {len(data['players'])}")
    print(f"  - Competitions: {len(data['competitions'])}")
    print(f"  - Matches: {len(data['matches'])}")

    # Build the graph
    print("\n🔨 Building graph in Neo4j...")
    builder = GraphBuilder(db)
    stats = builder.build_complete_graph(data)

    print("\n✅ Graph built successfully!")
    print(f"\n📈 Build Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    # Verify the data
    print("\n🔍 Verifying loaded data...")
    info = db.get_database_info()
    print(f"\n📊 Final Database Statistics:")
    print(f"  - Total Nodes: {info.get('node_count', 0)}")
    print(f"  - Total Relationships: {info.get('relationship_count', 0)}")
    print(f"  - Node Labels: {', '.join(info.get('labels', []))}")
    print(f"  - Relationship Types: {', '.join(info.get('relationship_types', []))}")

    # Sample the loaded data
    print("\n📝 Sample Data Verification:")

    # Sample teams
    teams = db.execute_read("MATCH (t:Team) RETURN t.name as name LIMIT 5")
    if teams:
        print("\n🏆 Sample Teams:")
        for team in teams:
            print(f"  - {team['name']}")

    # Sample players
    players = db.execute_read("MATCH (p:Player) RETURN p.name as name LIMIT 5")
    if players:
        print("\n⚽ Sample Players:")
        for player in players:
            print(f"  - {player['name']}")

    # Sample matches with relationships
    matches = db.execute_read("""
        MATCH (m:Match)-[:HOME_TEAM]->(h:Team)
        MATCH (m)-[:AWAY_TEAM]->(a:Team)
        RETURN h.name as home, a.name as away, m.date as date, m.home_score as hs, m.away_score as as
        LIMIT 5
    """)
    if matches:
        print("\n🏟️ Sample Matches:")
        for match in matches:
            print(f"  - {match['home']} {match['hs']}-{match['as']} {match['away']} ({match['date']})")

    # Check relationships
    relationships = db.execute_read("""
        MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
        RETURN p.name as player, t.name as team
        LIMIT 5
    """)
    if relationships:
        print("\n🔗 Sample Player-Team Relationships:")
        for rel in relationships:
            print(f"  - {rel['player']} plays for {rel['team']}")

    print("\n" + "=" * 60)
    print("✅ KAGGLE DATA PIPELINE LOADING COMPLETE!")
    print("=" * 60)
    print("\nThe Brazilian Soccer Knowledge Graph is now populated with:")
    print(f"  - {info.get('node_count', 0)} nodes")
    print(f"  - {info.get('relationship_count', 0)} relationships")
    print("\nYou can now query the graph using Cypher or the MCP server.")

    db.close()

if __name__ == "__main__":
    main()