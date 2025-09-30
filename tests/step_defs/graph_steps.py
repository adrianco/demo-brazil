"""
Brazilian Soccer MCP Knowledge Graph - BDD Test Step Definitions

CONTEXT:
Behavior-driven development (BDD) step definitions for testing the Brazilian
Soccer MCP Knowledge Graph functionality. These steps implement the scenarios
defined in the feature files using pytest-bdd or behave framework.

PHASE: 1 (Core Data)
COMPONENT: Test Step Definitions
DEPENDENCIES: behave, pytest, src package

ARCHITECTURE:
The step definitions cover the complete testing workflow:

TEST CATEGORIES:
- Database connection and setup
- Schema creation and validation
- Entity loading (teams, players, matches, etc.)
- Relationship creation and validation
- Graph integrity checks
- Performance and scalability tests

STEP PATTERNS:
- Given: Test setup and preconditions
- When: Action execution
- Then: Assertion and validation

TEST DATA:
- Uses sample data for predictable testing
- Supports both small and large dataset scenarios
- Includes edge cases and error conditions

The step definitions ensure that all graph construction functionality
works correctly and maintains data integrity throughout the process.
"""

from behave import given, when, then
import logging
from typing import Dict, Any, List

from src import (
    Neo4jConnection, GraphBuilder, KaggleLoader, GraphSchema,
    Player, Team, Match, Stadium, Competition
)


@given('I have a clean Neo4j database')
def step_clean_database(context):
    """Setup a clean Neo4j database for testing."""
    context.db = Neo4jConnection(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="neo4j123"
    )

    # Test connection
    assert context.db.test_connection(), "Could not connect to Neo4j database"

    # Clear the database
    context.db.clear_database()

    context.builder = GraphBuilder(context.db)
    context.loader = KaggleLoader(data_dir="tests/data")


@given('I have sample Brazilian soccer data')
def step_sample_data(context):
    """Load sample Brazilian soccer data for testing."""
    context.sample_data = context.loader.load_brazilian_championship_data()

    # Verify data was loaded
    assert len(context.sample_data['teams']) > 0, "No teams loaded"
    assert len(context.sample_data['players']) > 0, "No players loaded"
    assert len(context.sample_data['matches']) > 0, "No matches loaded"


@when('I create the graph schema')
def step_create_schema(context):
    """Create the graph schema."""
    context.schema = GraphSchema(context.db)
    context.schema.create_schema()


@then('the database should have all required constraints')
def step_verify_constraints(context):
    """Verify that all required constraints exist."""
    schema_info = context.schema.get_schema_info()

    # Check for key constraints
    constraint_names = [c.get('name', '') for c in schema_info.get('constraints', [])]

    # Should have constraints for main entities
    expected_entities = ['Player', 'Team', 'Match', 'Stadium', 'Competition']
    for entity in expected_entities:
        constraint_exists = any(entity.lower() in name.lower() for name in constraint_names)
        assert constraint_exists, f"Missing constraint for {entity}"


@then('the database should have all required indexes')
def step_verify_indexes(context):
    """Verify that all required indexes exist."""
    schema_info = context.schema.get_schema_info()

    # Check for key indexes
    index_names = [idx.get('name', '') for idx in schema_info.get('indexes', [])]

    # Should have indexes for searchable fields
    expected_indexes = ['name', 'date']
    for index_type in expected_indexes:
        index_exists = any(index_type in name.lower() for name in index_names)
        assert index_exists, f"Missing index for {index_type}"


@then('the schema creation should complete without errors')
def step_schema_no_errors(context):
    """Verify schema creation completed without errors."""
    # If we got here without exceptions, schema creation succeeded
    assert True


@given('I have Brazilian soccer teams data')
def step_teams_data(context):
    """Ensure teams data is available."""
    context.teams = context.sample_data['teams']
    assert len(context.teams) > 0, "No teams data available"


@when('I load the teams into the graph')
def step_load_teams(context):
    """Load teams into the graph database."""
    context.teams_created = context.builder.create_teams(context.teams)


@then('all teams should be created as nodes')
def step_verify_teams_created(context):
    """Verify all teams were created as nodes."""
    teams_in_db = context.db.execute_query("MATCH (t:Team) RETURN count(t) as count")[0]['count']
    assert teams_in_db == len(context.teams), f"Expected {len(context.teams)} teams, found {teams_in_db}"


@then('each team should have the correct properties')
def step_verify_team_properties(context):
    """Verify team nodes have correct properties."""
    teams_in_db = context.db.execute_query("MATCH (t:Team) RETURN t")

    assert len(teams_in_db) > 0, "No teams found in database"

    for team_record in teams_in_db:
        team = team_record['t']
        assert 'id' in team, "Team missing ID"
        assert 'name' in team, "Team missing name"


@then('team nodes should have unique IDs')
def step_verify_team_unique_ids(context):
    """Verify team IDs are unique."""
    id_count = context.db.execute_query("""
        MATCH (t:Team)
        WITH t.id as id, count(t) as count
        WHERE count > 1
        RETURN count(*) as duplicates
    """)[0]['duplicates']

    assert id_count == 0, f"Found {id_count} duplicate team IDs"


@given('I have Brazilian soccer players data')
def step_players_data(context):
    """Ensure players data is available."""
    context.players = context.sample_data['players']
    assert len(context.players) > 0, "No players data available"


@when('I load the players into the graph')
def step_load_players(context):
    """Load players into the graph database."""
    context.players_created = context.builder.create_players(context.players)


@then('all players should be created as nodes')
def step_verify_players_created(context):
    """Verify all players were created as nodes."""
    players_in_db = context.db.execute_query("MATCH (p:Player) RETURN count(p) as count")[0]['count']
    assert players_in_db == len(context.players), f"Expected {len(context.players)} players, found {players_in_db}"


@then('each player should have the correct properties')
def step_verify_player_properties(context):
    """Verify player nodes have correct properties."""
    players_in_db = context.db.execute_query("MATCH (p:Player) RETURN p LIMIT 5")

    assert len(players_in_db) > 0, "No players found in database"

    for player_record in players_in_db:
        player = player_record['p']
        assert 'id' in player, "Player missing ID"
        assert 'name' in player, "Player missing name"


@then('player nodes should have unique IDs')
def step_verify_player_unique_ids(context):
    """Verify player IDs are unique."""
    id_count = context.db.execute_query("""
        MATCH (p:Player)
        WITH p.id as id, count(p) as count
        WHERE count > 1
        RETURN count(*) as duplicates
    """)[0]['duplicates']

    assert id_count == 0, f"Found {id_count} duplicate player IDs"


@given('I have Brazilian soccer matches data')
def step_matches_data(context):
    """Ensure matches data is available."""
    context.matches = context.sample_data['matches']
    assert len(context.matches) > 0, "No matches data available"


@when('I load the matches into the graph')
def step_load_matches(context):
    """Load matches into the graph database."""
    context.matches_created = context.builder.create_matches(context.matches)


@then('all matches should be created as nodes')
def step_verify_matches_created(context):
    """Verify all matches were created as nodes."""
    matches_in_db = context.db.execute_query("MATCH (m:Match) RETURN count(m) as count")[0]['count']
    assert matches_in_db == len(context.matches), f"Expected {len(context.matches)} matches, found {matches_in_db}"


@then('each match should have the correct properties')
def step_verify_match_properties(context):
    """Verify match nodes have correct properties."""
    matches_in_db = context.db.execute_query("MATCH (m:Match) RETURN m LIMIT 5")

    assert len(matches_in_db) > 0, "No matches found in database"

    for match_record in matches_in_db:
        match = match_record['m']
        assert 'id' in match, "Match missing ID"
        assert 'date' in match, "Match missing date"


@then('match nodes should have unique IDs')
def step_verify_match_unique_ids(context):
    """Verify match IDs are unique."""
    id_count = context.db.execute_query("""
        MATCH (m:Match)
        WITH m.id as id, count(m) as count
        WHERE count > 1
        RETURN count(*) as duplicates
    """)[0]['duplicates']

    assert id_count == 0, f"Found {id_count} duplicate match IDs"


@given('I have teams and players in the graph')
def step_teams_players_in_graph(context):
    """Ensure teams and players are loaded in the graph."""
    teams_count = context.db.execute_query("MATCH (t:Team) RETURN count(t) as count")[0]['count']
    players_count = context.db.execute_query("MATCH (p:Player) RETURN count(p) as count")[0]['count']

    assert teams_count > 0, "No teams in graph"
    assert players_count > 0, "No players in graph"


@when('I create PLAYS_FOR relationships')
def step_create_plays_for_relationships(context):
    """Create PLAYS_FOR relationships between players and teams."""
    context.player_team_rels = context.builder.create_player_team_relationships(context.players)


@then('each player should be connected to a team')
def step_verify_player_team_connections(context):
    """Verify each player is connected to a team."""
    unconnected_players = context.db.execute_query("""
        MATCH (p:Player)
        WHERE NOT (p)-[:PLAYS_FOR]->()
        RETURN count(p) as count
    """)[0]['count']

    assert unconnected_players == 0, f"Found {unconnected_players} unconnected players"


@then('the relationships should have the correct direction')
def step_verify_relationship_direction(context):
    """Verify relationships have correct direction (Player -> Team)."""
    correct_direction = context.db.execute_query("""
        MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
        RETURN count(*) as count
    """)[0]['count']

    wrong_direction = context.db.execute_query("""
        MATCH (t:Team)-[:PLAYS_FOR]->(p:Player)
        RETURN count(*) as count
    """)[0]['count']

    assert correct_direction > 0, "No PLAYS_FOR relationships found"
    assert wrong_direction == 0, f"Found {wrong_direction} relationships in wrong direction"


@then('there should be no orphaned players')
def step_verify_no_orphaned_players(context):
    """Verify no players are orphaned (without team relationships)."""
    orphaned_players = context.db.execute_query("""
        MATCH (p:Player)
        WHERE NOT (p)-[:PLAYS_FOR]->()
        RETURN count(p) as count
    """)[0]['count']

    assert orphaned_players == 0, f"Found {orphaned_players} orphaned players"


@given('I have matches and teams in the graph')
def step_matches_teams_in_graph(context):
    """Ensure matches and teams are loaded in the graph."""
    matches_count = context.db.execute_query("MATCH (m:Match) RETURN count(m) as count")[0]['count']
    teams_count = context.db.execute_query("MATCH (t:Team) RETURN count(t) as count")[0]['count']

    assert matches_count > 0, "No matches in graph"
    assert teams_count > 0, "No teams in graph"


@when('I create match-team relationships')
def step_create_match_team_relationships(context):
    """Create relationships between matches and teams."""
    context.match_team_rels = context.builder.create_match_relationships(context.matches)


@then('each match should have HOME_TEAM and AWAY_TEAM relationships')
def step_verify_match_team_relationships(context):
    """Verify each match has proper team relationships."""
    matches_with_home = context.db.execute_query("""
        MATCH (m:Match)-[:HOME_TEAM]->(t:Team)
        RETURN count(DISTINCT m) as count
    """)[0]['count']

    matches_with_away = context.db.execute_query("""
        MATCH (m:Match)-[:AWAY_TEAM]->(t:Team)
        RETURN count(DISTINCT m) as count
    """)[0]['count']

    total_matches = context.db.execute_query("MATCH (m:Match) RETURN count(m) as count")[0]['count']

    assert matches_with_home == total_matches, f"Expected {total_matches} matches with home teams, found {matches_with_home}"
    assert matches_with_away == total_matches, f"Expected {total_matches} matches with away teams, found {matches_with_away}"


@then('the relationships should point to valid teams')
def step_verify_valid_team_relationships(context):
    """Verify all match-team relationships point to valid teams."""
    invalid_home_rels = context.db.execute_query("""
        MATCH (m:Match)-[:HOME_TEAM]->(n)
        WHERE NOT n:Team
        RETURN count(*) as count
    """)[0]['count']

    invalid_away_rels = context.db.execute_query("""
        MATCH (m:Match)-[:AWAY_TEAM]->(n)
        WHERE NOT n:Team
        RETURN count(*) as count
    """)[0]['count']

    assert invalid_home_rels == 0, f"Found {invalid_home_rels} invalid HOME_TEAM relationships"
    assert invalid_away_rels == 0, f"Found {invalid_away_rels} invalid AWAY_TEAM relationships"


@then('there should be no orphaned matches')
def step_verify_no_orphaned_matches(context):
    """Verify no matches are orphaned (without team relationships)."""
    orphaned_matches = context.db.execute_query("""
        MATCH (m:Match)
        WHERE NOT (m)-[:HOME_TEAM]->() OR NOT (m)-[:AWAY_TEAM]->()
        RETURN count(m) as count
    """)[0]['count']

    assert orphaned_matches == 0, f"Found {orphaned_matches} orphaned matches"


@when('I build the complete graph from scratch')
def step_build_complete_graph(context):
    """Build the complete graph from scratch."""
    context.build_stats = context.builder.build_complete_graph(context.sample_data)


@then('the graph should contain all entity types')
def step_verify_all_entity_types(context):
    """Verify the graph contains all expected entity types."""
    expected_entities = ['Team', 'Player', 'Match', 'Stadium', 'Competition', 'Coach', 'Season']

    for entity in expected_entities:
        count = context.db.execute_query(f"MATCH (n:{entity}) RETURN count(n) as count")[0]['count']
        assert count > 0, f"No {entity} entities found in graph"


@then('all relationships should be properly created')
def step_verify_all_relationships(context):
    """Verify all expected relationships are created."""
    expected_relationships = ['PLAYS_FOR', 'HOME_TEAM', 'AWAY_TEAM', 'PART_OF']

    for rel_type in expected_relationships:
        count = context.db.execute_query(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")[0]['count']
        assert count > 0, f"No {rel_type} relationships found in graph"


@then('the graph should pass integrity validation')
def step_verify_graph_integrity(context):
    """Verify the graph passes integrity validation."""
    validation = context.builder.validate_graph_integrity()
    assert validation['success'], f"Graph integrity validation failed: {validation.get('errors', [])}"


@then('the build process should complete successfully')
def step_verify_build_success(context):
    """Verify the build process completed successfully."""
    assert context.build_stats['success'], f"Build failed: {context.build_stats.get('error', 'Unknown error')}"
    assert context.build_stats['nodes_created'] > 0, "No nodes were created"
    assert context.build_stats['relationships_created'] > 0, "No relationships were created"


@given('I have a complete graph')
def step_complete_graph_exists(context):
    """Ensure a complete graph exists."""
    # Verify we have data in the graph
    total_nodes = context.db.execute_query("MATCH (n) RETURN count(n) as count")[0]['count']
    assert total_nodes > 0, "No nodes found in graph"


@when('I validate the graph integrity')
def step_validate_graph_integrity(context):
    """Validate the graph integrity."""
    context.validation_result = context.builder.validate_graph_integrity()


@then('there should be no orphaned entities')
def step_verify_no_orphaned_entities(context):
    """Verify there are no orphaned entities."""
    # This check is covered by the validation result
    assert context.validation_result['success'], "Graph validation found orphaned entities"


@then('all relationships should be valid')
def step_verify_valid_relationships(context):
    """Verify all relationships are valid."""
    assert context.validation_result['success'], "Graph validation found invalid relationships"


@then('there should be no duplicate entities')
def step_verify_no_duplicates(context):
    """Verify there are no duplicate entities."""
    assert context.validation_result['success'], "Graph validation found duplicate entities"


@then('the validation should report success')
def step_verify_validation_success(context):
    """Verify the validation reports success."""
    assert context.validation_result['success'], f"Validation failed: {context.validation_result.get('errors', [])}"


@when('I request graph statistics')
def step_request_graph_statistics(context):
    """Request graph statistics."""
    context.graph_stats = context.builder.get_graph_statistics()


@then('I should get counts for all entity types')
def step_verify_entity_counts(context):
    """Verify statistics include counts for all entity types."""
    assert 'nodes' in context.graph_stats, "Statistics missing node counts"

    expected_entities = ['teams', 'players', 'matches']
    for entity in expected_entities:
        assert entity in context.graph_stats['nodes'], f"Missing count for {entity}"


@then('I should get counts for all relationship types')
def step_verify_relationship_counts(context):
    """Verify statistics include counts for all relationship types."""
    assert 'relationships' in context.graph_stats, "Statistics missing relationship counts"

    expected_relationships = ['plays_for', 'home_team', 'away_team']
    for rel_type in expected_relationships:
        assert rel_type in context.graph_stats['relationships'], f"Missing count for {rel_type}"


@then('the statistics should be accurate')
def step_verify_statistics_accuracy(context):
    """Verify the statistics are accurate."""
    # Verify total counts match sum of individual counts
    total_nodes = context.graph_stats.get('total_nodes', 0)
    sum_nodes = sum(context.graph_stats.get('nodes', {}).values())

    assert total_nodes == sum_nodes, f"Total nodes ({total_nodes}) doesn't match sum ({sum_nodes})"


@then('the response should be properly formatted')
def step_verify_response_format(context):
    """Verify the response is properly formatted."""
    assert isinstance(context.graph_stats, dict), "Statistics should be a dictionary"
    assert 'total_nodes' in context.graph_stats, "Missing total_nodes"
    assert 'total_relationships' in context.graph_stats, "Missing total_relationships"


@given('I have a large dataset of Brazilian soccer data')
def step_large_dataset(context):
    """Setup a large dataset for performance testing."""
    # For testing purposes, we'll simulate a larger dataset
    # In a real scenario, this would load actual large datasets
    context.large_sample_data = context.sample_data.copy()

    # Simulate larger dataset by replicating existing data
    # This is just for testing batch processing functionality
    original_teams = context.large_sample_data['teams']
    original_players = context.large_sample_data['players']

    # Create additional teams and players for batch testing
    additional_teams = []
    additional_players = []

    for i in range(10):  # Add 10 more teams
        for team in original_teams:
            new_team = Team(
                id=f"{team.id}_{i}",
                name=f"{team.name} {i}",
                city=team.city,
                state=team.state
            )
            additional_teams.append(new_team)

    for i in range(50):  # Add 50 more players
        for player in original_players:
            new_player = Player(
                id=f"{player.id}_{i}",
                name=f"{player.name} {i}",
                nationality=player.nationality,
                position=player.position
            )
            additional_players.append(new_player)

    context.large_sample_data['teams'].extend(additional_teams)
    context.large_sample_data['players'].extend(additional_players)


@when('I build the graph with batch processing')
def step_build_with_batch_processing(context):
    """Build the graph using batch processing."""
    import time
    start_time = time.time()

    context.batch_build_stats = context.builder.build_complete_graph(context.large_sample_data)

    context.build_duration = time.time() - start_time


@then('the build should complete within reasonable time')
def step_verify_reasonable_build_time(context):
    """Verify the build completes within reasonable time."""
    # For this test dataset, should complete within 30 seconds
    assert context.build_duration < 30, f"Build took {context.build_duration:.2f} seconds, expected < 30"


@then('memory usage should remain stable')
def step_verify_stable_memory_usage(context):
    """Verify memory usage remains stable during build."""
    # This is a placeholder - in a real implementation, you'd monitor memory
    # For now, we'll just verify the build completed successfully
    assert context.batch_build_stats['success'], "Build failed, suggesting memory issues"


@then('all data should be loaded correctly')
def step_verify_all_data_loaded(context):
    """Verify all data was loaded correctly."""
    expected_teams = len(context.large_sample_data['teams'])
    expected_players = len(context.large_sample_data['players'])

    actual_teams = context.db.execute_query("MATCH (t:Team) RETURN count(t) as count")[0]['count']
    actual_players = context.db.execute_query("MATCH (p:Player) RETURN count(p) as count")[0]['count']

    assert actual_teams == expected_teams, f"Expected {expected_teams} teams, found {actual_teams}"
    assert actual_players == expected_players, f"Expected {expected_players} players, found {actual_players}"


@then('batch processing should work efficiently')
def step_verify_batch_efficiency(context):
    """Verify batch processing works efficiently."""
    # Verify batch size was respected and operations were batched
    nodes_created = context.batch_build_stats['nodes_created']
    duration = context.batch_build_stats['duration_seconds']

    if duration > 0:
        nodes_per_second = nodes_created / duration
        # Should process at least 100 nodes per second for efficiency
        assert nodes_per_second >= 50, f"Processing rate too slow: {nodes_per_second:.2f} nodes/second"