Feature: Graph Construction
  As a data engineer
  I want to build a Brazilian soccer knowledge graph
  So that I can analyze soccer data through graph queries

  Background:
    Given I have a clean Neo4j database
    And I have sample Brazilian soccer data

  Scenario: Create graph schema
    When I create the graph schema
    Then the database should have all required constraints
    And the database should have all required indexes
    And the schema creation should complete without errors

  Scenario: Load team entities
    Given I have Brazilian soccer teams data
    When I load the teams into the graph
    Then all teams should be created as nodes
    And each team should have the correct properties
    And team nodes should have unique IDs

  Scenario: Load player entities
    Given I have Brazilian soccer players data
    When I load the players into the graph
    Then all players should be created as nodes
    And each player should have the correct properties
    And player nodes should have unique IDs

  Scenario: Load match entities
    Given I have Brazilian soccer matches data
    When I load the matches into the graph
    Then all matches should be created as nodes
    And each match should have the correct properties
    And match nodes should have unique IDs

  Scenario: Create team-player relationships
    Given I have teams and players in the graph
    When I create PLAYS_FOR relationships
    Then each player should be connected to a team
    And the relationships should have the correct direction
    And there should be no orphaned players

  Scenario: Create match-team relationships
    Given I have matches and teams in the graph
    When I create match-team relationships
    Then each match should have HOME_TEAM and AWAY_TEAM relationships
    And the relationships should point to valid teams
    And there should be no orphaned matches

  Scenario: Build complete graph
    When I build the complete graph from scratch
    Then the graph should contain all entity types
    And all relationships should be properly created
    And the graph should pass integrity validation
    And the build process should complete successfully

  Scenario: Validate graph integrity
    Given I have a complete graph
    When I validate the graph integrity
    Then there should be no orphaned entities
    And all relationships should be valid
    And there should be no duplicate entities
    And the validation should report success

  Scenario: Get graph statistics
    Given I have a complete graph
    When I request graph statistics
    Then I should get counts for all entity types
    And I should get counts for all relationship types
    And the statistics should be accurate
    And the response should be properly formatted

  Scenario: Handle large datasets
    Given I have a large dataset of Brazilian soccer data
    When I build the graph with batch processing
    Then the build should complete within reasonable time
    And memory usage should remain stable
    And all data should be loaded correctly
    And batch processing should work efficiently