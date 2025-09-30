"""
Brazilian Soccer MCP Knowledge Graph - Database Connection Module

CONTEXT:
This module implements Neo4j database connection and session management for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for querying player, team, match, and competition data
stored in a Neo4j graph database.

PHASE: 1 - Core Data
PURPOSE: Database connection, session management, and query execution
DATA SOURCES: Kaggle Brazilian Football Matches
DEPENDENCIES: neo4j, py2neo

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition, Stadium, Coach nodes with relationships
- Performance: Connection pooling, session management, query optimization
- Testing: BDD scenarios for database operations

INTEGRATION:
- MCP Tools: Database backend for all query tools
- Error Handling: Comprehensive exception handling
- Rate Limiting: N/A for local database
"""

import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager
import neo4j
from neo4j import GraphDatabase, Driver, Session, Result
from neo4j.exceptions import ServiceUnavailable, AuthError, ConfigurationError

# Set up logging
logger = logging.getLogger(__name__)


class Neo4jConnectionError(Exception):
    """Custom exception for Neo4j connection issues"""
    pass


class Neo4jQueryError(Exception):
    """Custom exception for Neo4j query execution issues"""
    pass


class Neo4jDatabase:
    """
    Neo4j database connection and session management class

    Provides connection pooling, session management, and query execution
    with comprehensive error handling for the Brazilian Soccer Knowledge Graph.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "neo4j123",
        max_connection_lifetime: int = 30 * 60,  # 30 minutes
        max_connection_pool_size: int = 50,
        connection_acquisition_timeout: int = 60,  # 60 seconds
        encrypted: bool = False
    ):
        """
        Initialize Neo4j database connection

        Args:
            uri: Neo4j database URI
            user: Database username
            password: Database password
            max_connection_lifetime: Maximum connection lifetime in seconds
            max_connection_pool_size: Maximum connections in pool
            connection_acquisition_timeout: Timeout for acquiring connection
            encrypted: Whether to use encrypted connection
        """
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[Driver] = None

        # Connection configuration
        self._config = {
            "max_connection_lifetime": max_connection_lifetime,
            "max_connection_pool_size": max_connection_pool_size,
            "connection_acquisition_timeout": connection_acquisition_timeout,
            "encrypted": encrypted,
            "trust": neo4j.TRUST_ALL_CERTIFICATES if not encrypted else neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
        }

        # Initialize connection
        self._connect()

    def _connect(self) -> None:
        """
        Establish connection to Neo4j database

        Raises:
            Neo4jConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to Neo4j at {self.uri}")
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                **self._config
            )

            # Test connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise Neo4jConnectionError("Connection test failed")

            logger.info("Successfully connected to Neo4j database")

        except (ServiceUnavailable, AuthError, ConfigurationError) as e:
            error_msg = f"Failed to connect to Neo4j: {str(e)}"
            logger.error(error_msg)
            raise Neo4jConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to Neo4j: {str(e)}"
            logger.error(error_msg)
            raise Neo4jConnectionError(error_msg) from e

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return status

        Returns:
            Dict with connection status and database info
        """
        try:
            with self.session() as session:
                # Test basic connectivity
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]

                # Get database info
                db_info = session.run("""
                    CALL dbms.components() YIELD name, versions, edition
                    RETURN name, versions[0] as version, edition
                """).single()

                # Get node/relationship counts
                stats = session.run("""
                    MATCH (n)
                    RETURN count(n) as node_count
                """).single()

                rel_stats = session.run("""
                    MATCH ()-[r]->()
                    RETURN count(r) as relationship_count
                """).single()

                return {
                    "status": "connected",
                    "test_result": test_value,
                    "database": {
                        "name": db_info["name"] if db_info else "Unknown",
                        "version": db_info["version"] if db_info else "Unknown",
                        "edition": db_info["edition"] if db_info else "Unknown"
                    },
                    "statistics": {
                        "nodes": stats["node_count"] if stats else 0,
                        "relationships": rel_stats["relationship_count"] if rel_stats else 0
                    },
                    "uri": self.uri
                }

        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "uri": self.uri
            }

    @contextmanager
    def session(self, database: str = None, access_mode: str = neo4j.WRITE_ACCESS):
        """
        Context manager for Neo4j sessions

        Args:
            database: Target database name (None for default)
            access_mode: Session access mode (READ_ACCESS or WRITE_ACCESS)

        Yields:
            Neo4j session object

        Raises:
            Neo4jConnectionError: If session creation fails
        """
        if not self._driver:
            raise Neo4jConnectionError("Database driver not initialized")

        session = None
        try:
            session_config = {"default_access_mode": access_mode}
            if database:
                session_config["database"] = database

            session = self._driver.session(**session_config)
            yield session

        except Exception as e:
            logger.error(f"Session error: {str(e)}")
            raise Neo4jConnectionError(f"Session creation failed: {str(e)}") from e
        finally:
            if session:
                session.close()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = None,
        access_mode: str = neo4j.WRITE_ACCESS
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Target database name
            access_mode: Session access mode

        Returns:
            List of result records as dictionaries

        Raises:
            Neo4jQueryError: If query execution fails
        """
        if parameters is None:
            parameters = {}

        try:
            with self.session(database=database, access_mode=access_mode) as session:
                logger.debug(f"Executing query: {query[:100]}...")
                result = session.run(query, parameters)
                records = [record.data() for record in result]
                logger.debug(f"Query returned {len(records)} records")
                return records

        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(f"{error_msg}\nQuery: {query}\nParameters: {parameters}")
            raise Neo4jQueryError(error_msg) from e

    def execute_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query (CREATE, UPDATE, DELETE, MERGE)

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Target database name

        Returns:
            List of result records as dictionaries
        """
        return self.execute_query(query, parameters, database, neo4j.WRITE_ACCESS)

    def execute_read_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read-only query (MATCH, RETURN)

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Target database name

        Returns:
            List of result records as dictionaries
        """
        return self.execute_query(query, parameters, database, neo4j.READ_ACCESS)

    def execute_transaction(
        self,
        queries: List[Dict[str, Any]],
        database: str = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple queries in a single transaction

        Args:
            queries: List of query dictionaries with 'query' and optional 'parameters'
            database: Target database name

        Returns:
            List of result lists for each query

        Raises:
            Neo4jQueryError: If transaction fails
        """
        try:
            with self.session(database=database, access_mode=neo4j.WRITE_ACCESS) as session:
                def execute_queries(tx):
                    results = []
                    for query_dict in queries:
                        query = query_dict["query"]
                        parameters = query_dict.get("parameters", {})
                        result = tx.run(query, parameters)
                        results.append([record.data() for record in result])
                    return results

                logger.debug(f"Executing transaction with {len(queries)} queries")
                results = session.execute_write(execute_queries)
                logger.debug("Transaction completed successfully")
                return results

        except Exception as e:
            error_msg = f"Transaction execution failed: {str(e)}"
            logger.error(error_msg)
            raise Neo4jQueryError(error_msg) from e

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get database schema information

        Returns:
            Dictionary with schema details
        """
        try:
            schema_info = {}

            with self.session(access_mode=neo4j.READ_ACCESS) as session:
                # Get node labels
                labels_result = session.run("CALL db.labels()")
                schema_info["labels"] = [record["label"] for record in labels_result]

                # Get relationship types
                rel_types_result = session.run("CALL db.relationshipTypes()")
                schema_info["relationship_types"] = [record["relationshipType"] for record in rel_types_result]

                # Get property keys
                props_result = session.run("CALL db.propertyKeys()")
                schema_info["property_keys"] = [record["propertyKey"] for record in props_result]

                # Get constraints
                constraints_result = session.run("CALL db.constraints()")
                schema_info["constraints"] = [record.data() for record in constraints_result]

                # Get indexes
                indexes_result = session.run("CALL db.indexes()")
                schema_info["indexes"] = [record.data() for record in indexes_result]

            return schema_info

        except Exception as e:
            logger.error(f"Failed to get schema info: {str(e)}")
            return {"error": str(e)}

    def close(self) -> None:
        """
        Close database connection
        """
        if self._driver:
            logger.info("Closing Neo4j database connection")
            self._driver.close()
            self._driver = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Destructor"""
        self.close()


# Global database instance
_db_instance: Optional[Neo4jDatabase] = None


def get_database() -> Neo4jDatabase:
    """
    Get global database instance (singleton pattern)

    Returns:
        Neo4jDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Neo4jDatabase()
    return _db_instance


def close_database() -> None:
    """
    Close global database instance
    """
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None


# Convenience functions
def execute_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    database: str = None,
    access_mode: str = neo4j.WRITE_ACCESS
) -> List[Dict[str, Any]]:
    """
    Execute query using global database instance

    Args:
        query: Cypher query string
        parameters: Query parameters
        database: Target database name
        access_mode: Session access mode

    Returns:
        List of result records as dictionaries
    """
    db = get_database()
    return db.execute_query(query, parameters, database, access_mode)


def execute_read_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    database: str = None
) -> List[Dict[str, Any]]:
    """
    Execute read-only query using global database instance
    """
    db = get_database()
    return db.execute_read_query(query, parameters, database)


def execute_write_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    database: str = None
) -> List[Dict[str, Any]]:
    """
    Execute write query using global database instance
    """
    db = get_database()
    return db.execute_write_query(query, parameters, database)


def test_connection() -> Dict[str, Any]:
    """
    Test database connection using global instance
    """
    db = get_database()
    return db.test_connection()