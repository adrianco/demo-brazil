#!/usr/bin/env python3
"""
Simple test to verify MCP server and Neo4j are working.
"""

import requests
import json
from neo4j import GraphDatabase

def test_neo4j():
    """Test Neo4j connection."""
    print("Testing Neo4j connection...")
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j123"))

    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        print(f"✅ Neo4j: {count} nodes found")

        # Get players
        result = session.run("MATCH (p:Player) RETURN p.name as name LIMIT 5")
        print("Sample players:")
        for record in result:
            print(f"  - {record['name']}")

    driver.close()

def test_mcp_server():
    """Test MCP server."""
    print("\nTesting MCP server...")

    # Test health endpoint
    response = requests.get("http://localhost:3000/health")
    print(f"✅ Health check: {response.json()}")

    # Test search_player
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/search_player",
        "params": {"name": "Neymar"}
    }

    response = requests.post("http://localhost:3000/mcp", json=request)
    result = response.json()

    if "result" in result:
        print(f"✅ Player search result: {json.dumps(result['result'], indent=2)}")
    else:
        print(f"❌ Error: {result}")

    # Test search_team
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/search_team",
        "params": {"name": "Flamengo"}
    }

    response = requests.post("http://localhost:3000/mcp", json=request)
    result = response.json()

    if "result" in result:
        print(f"✅ Team search result: {json.dumps(result['result'], indent=2)}")
    else:
        print(f"❌ Error: {result}")

if __name__ == "__main__":
    test_neo4j()
    test_mcp_server()