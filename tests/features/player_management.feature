Feature: Player Management
  As a Brazilian soccer enthusiast
  I want to search for players and get their statistics
  So that I can analyze player performance and career data

  Background:
    Given the knowledge graph contains player data
    And the MCP server is running

  Scenario: Search for a famous Brazilian player
    Given I want to search for a player
    When I search for "Neymar Jr"
    Then I should get player details
    And the response should include career information
    And the response should include current team
    And the response should include national team caps

  Scenario: Get player statistics
    Given I have a valid player ID
    When I request statistics for player "neymar_jr"
    Then I should receive detailed statistics
    And the statistics should include goals scored
    And the statistics should include assists
    And the statistics should include matches played
    And the statistics should include performance metrics

  Scenario: Search for player by position
    Given I want to find players by position
    When I search for players with position "Forward"
    Then I should get a list of forwards
    And each player should have position "Forward"
    And the results should be properly formatted

  Scenario: Player career history
    Given I have a valid player ID
    When I request career history for "ronaldinho"
    Then I should get chronological career data
    And the history should include club transfers
    And the history should include achievement dates
    And the history should include contract periods

  Scenario: Invalid player search
    Given I want to search for a player
    When I search for "NonExistentPlayer123"
    Then I should get an empty result
    And the response should indicate no matches found
    And the error should be handled gracefully

  Scenario: Player comparison
    Given I have two valid player IDs
    When I compare "neymar_jr" and "vinicius_jr"
    Then I should get comparative statistics
    And the comparison should include goals per game
    And the comparison should include assist ratios
    And the comparison should highlight strengths

  Scenario: Search players by age range
    Given I want to filter players by age
    When I search for players aged between 20 and 25
    Then I should get players in that age range
    And each player's age should be within the range
    And the results should be sorted by age

  Scenario: Player injury history
    Given I have a valid player ID
    When I request injury history for "neymar_jr"
    Then I should get injury records
    And the records should include injury types
    And the records should include recovery periods
    And the records should show impact on performance

  Scenario: Top scorers query
    Given I want to find top scoring players
    When I request top 10 goal scorers
    Then I should get 10 players maximum
    And they should be ranked by goals scored
    And each entry should show goal count
    And the list should include both club and international goals

  Scenario: Player social media presence
    Given I have a valid player ID
    When I request social media data for "neymar_jr"
    Then I should get social media statistics
    And the data should include follower counts
    And the data should include engagement metrics
    And the data should be current