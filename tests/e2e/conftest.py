"""
Brazilian Soccer MCP Knowledge Graph - End-to-End Test Configuration

CONTEXT:
This module configures pytest for end-to-end BDD testing against the real
MCP server and Neo4j database with actual data.

PHASE: 3 - Integration & Testing
PURPOSE: Configure real database and MCP server connections for e2e tests
DATA SOURCES: Live Neo4j database with loaded Brazilian soccer data
DEPENDENCIES: pytest, neo4j, integration.mcp_client

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- MCP Server: http://localhost:3000
- Test Mode: End-to-end with real data
- Testing: Full integration tests against live system
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from integration.mcp_client import RealMCPClient
from src.graph.database import Neo4jDatabase


@pytest.fixture(scope="session")
def neo4j_driver():
    """
    Create a real Neo4j driver for end-to-end testing.

    This connects to the actual Neo4j database with loaded
    Brazilian soccer data.
    """
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "neo4j123"

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Verify connection and data exists
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()["count"]

        if node_count == 0:
            pytest.skip("No data in Neo4j database. Please run load_kaggle_data.py first.")

        print(f"\n✅ Connected to Neo4j with {node_count} nodes")

    yield driver
    driver.close()


@pytest.fixture(scope="session")
def neo4j_db():
    """
    Create a Neo4j database connection using our database module.
    """
    db = Neo4jDatabase(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="neo4j123"
    )
    db.connect()

    # Verify data exists
    info = db.get_database_info()
    if info.get("node_count", 0) == 0:
        pytest.skip("No data in Neo4j database. Please run load_kaggle_data.py first.")

    yield db
    db.close()


@pytest.fixture(scope="session")
def mcp_client():
    """
    Create a real MCP client for end-to-end testing.

    This connects to the actual running MCP server.
    """
    client = RealMCPClient(server_url="http://localhost:3000")

    # Test connection
    response = client.call_tool("test_connection", {})
    if not response.success:
        # If MCP server is not running, try to start it or skip tests
        pytest.skip(f"MCP server not accessible: {response.error}")

    yield client
    client.close()


@pytest.fixture
def test_context():
    """
    Test context for storing results between steps.
    """
    return {}


@pytest.fixture(autouse=True)
def log_test_info(request):
    """
    Log test information for debugging.
    """
    print(f"\n🧪 Running E2E test: {request.node.name}")
    yield
    print(f"✓ Completed: {request.node.name}")


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest for e2e testing."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test against real systems"
    )
    config.addinivalue_line(
        "markers", "requires_mcp: test requires MCP server to be running"
    )
    config.addinivalue_line(
        "markers", "requires_neo4j: test requires Neo4j with data loaded"
    )