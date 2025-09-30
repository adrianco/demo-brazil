#!/usr/bin/env python3
"""
Check what data is currently in Neo4j database
"""

from neo4j import GraphDatabase

# Connect to Neo4j
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4j123"))

def check_database():
    with driver.session() as session:
        print("=" * 60)
        print("NEO4J DATABASE CONTENT SUMMARY")
        print("=" * 60)

        # Count all nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        total_nodes = result.single()["count"]
        print(f"\n📊 Total Nodes: {total_nodes}")

        if total_nodes == 0:
            print("\n⚠️ The database is empty!")
            print("No data has been loaded into Neo4j yet.")
            return

        # Count nodes by label
        print("\n🏷️ Nodes by Label:")
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  - {record['label']}: {record['count']}")

        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        total_rels = result.single()["count"]
        print(f"\n🔗 Total Relationships: {total_rels}")

        if total_rels > 0:
            # Count relationships by type
            print("\n📎 Relationships by Type:")
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            for record in result:
                print(f"  - {record['type']}: {record['count']}")

        # Sample some data
        print("\n📝 Sample Data:")

        # Sample teams
        result = session.run("MATCH (t:Team) RETURN t.name as name LIMIT 5")
        teams = [r["name"] for r in result if r["name"]]
        if teams:
            print(f"\n🏆 Sample Teams:")
            for team in teams:
                print(f"  - {team}")

        # Sample players
        result = session.run("MATCH (p:Player) RETURN p.name as name LIMIT 5")
        players = [r["name"] for r in result if r["name"]]
        if players:
            print(f"\n⚽ Sample Players:")
            for player in players:
                print(f"  - {player}")

        # Sample matches
        result = session.run("""
            MATCH (m:Match)
            RETURN m.home_team as home, m.away_team as away, m.date as date
            LIMIT 5
        """)
        matches = list(result)
        if matches:
            print(f"\n🏟️ Sample Matches:")
            for match in matches:
                if match["home"] and match["away"]:
                    print(f"  - {match['home']} vs {match['away']} ({match['date']})")

        # Check for competitions
        result = session.run("MATCH (c:Competition) RETURN c.name as name LIMIT 5")
        competitions = [r["name"] for r in result if r["name"]]
        if competitions:
            print(f"\n🏅 Sample Competitions:")
            for comp in competitions:
                print(f"  - {comp}")

# Load sample data if empty
def load_sample_data():
    print("\n" + "=" * 60)
    print("LOADING SAMPLE DATA")
    print("=" * 60)

    with driver.session() as session:
        # Create sample teams
        session.run("""
            CREATE (flamengo:Team {name: 'Flamengo', city: 'Rio de Janeiro', founded: 1895})
            CREATE (palmeiras:Team {name: 'Palmeiras', city: 'São Paulo', founded: 1914})
            CREATE (corinthians:Team {name: 'Corinthians', city: 'São Paulo', founded: 1910})
            CREATE (santos:Team {name: 'Santos', city: 'Santos', founded: 1912})
            CREATE (gremio:Team {name: 'Grêmio', city: 'Porto Alegre', founded: 1903})
        """)
        print("✅ Created 5 Brazilian teams")

        # Create sample players
        session.run("""
            CREATE (p1:Player {name: 'Gabriel Barbosa', position: 'Forward', team: 'Flamengo'})
            CREATE (p2:Player {name: 'Dudu', position: 'Forward', team: 'Palmeiras'})
            CREATE (p3:Player {name: 'Yuri Alberto', position: 'Forward', team: 'Corinthians'})
            CREATE (p4:Player {name: 'Neymar Jr', position: 'Forward', team: 'Al-Hilal', former_team: 'Santos'})
            CREATE (p5:Player {name: 'Suárez', position: 'Forward', team: 'Grêmio'})
        """)
        print("✅ Created 5 players")

        # Create sample competition
        session.run("""
            CREATE (c:Competition {name: 'Brasileirão 2023', type: 'League', year: 2023})
        """)
        print("✅ Created competition")

        # Create sample matches
        session.run("""
            CREATE (m1:Match {home_team: 'Flamengo', away_team: 'Palmeiras', date: '2023-08-15', score: '2-1'})
            CREATE (m2:Match {home_team: 'Corinthians', away_team: 'Santos', date: '2023-09-10', score: '1-1'})
            CREATE (m3:Match {home_team: 'Grêmio', away_team: 'Flamengo', date: '2023-10-22', score: '0-2'})
        """)
        print("✅ Created 3 matches")

        # Create relationships
        session.run("""
            MATCH (p:Player), (t:Team)
            WHERE p.team = t.name
            CREATE (p)-[:PLAYS_FOR]->(t)
        """)
        print("✅ Created PLAYS_FOR relationships")

        session.run("""
            MATCH (m:Match), (c:Competition)
            WHERE c.name = 'Brasileirão 2023'
            CREATE (m)-[:PART_OF]->(c)
        """)
        print("✅ Created PART_OF relationships")

try:
    # Check current data
    check_database()

    # If empty, ask to load sample data
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        if result.single()["count"] == 0:
            response = input("\n🤔 Database is empty. Load sample data? (y/n): ")
            if response.lower() == 'y':
                load_sample_data()
                print("\n" + "=" * 60)
                print("UPDATED DATABASE CONTENT")
                print("=" * 60)
                check_database()

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure Neo4j is running and accessible at bolt://localhost:7687")
    print("Credentials: neo4j / neo4j123")

finally:
    driver.close()