Feature: Team Queries
  As a Brazilian soccer enthusiast
  I want to query team information and statistics
  So that I can analyze team performance and history

  Background:
    Given the knowledge graph contains team data
    And the MCP server is running

  Scenario: Search for a famous Brazilian club
    Given I want to search for a team
    When I search for "Flamengo"
    Then I should get team details
    And the response should include team history
    And the response should include current squad
    And the response should include stadium information

  Scenario: Get team roster
    Given I have a valid team ID
    When I request roster for team "flamengo"
    Then I should receive the current squad
    And each player should have position information
    And each player should have contract details
    And the roster should be organized by position

  Scenario: Team performance statistics
    Given I have a valid team ID
    When I request statistics for team "palmeiras"
    Then I should receive team performance data
    And the statistics should include wins, draws, losses
    And the statistics should include goals scored and conceded
    And the statistics should include home and away records

  Scenario: Search teams by league
    Given I want to find teams by competition
    When I search for teams in "Série A"
    Then I should get a list of teams
    And each team should be in "Série A"
    And the results should include team rankings

  Scenario: Team head-to-head comparison
    Given I have two valid team IDs
    When I compare "flamengo" and "corinthians"
    Then I should get head-to-head statistics
    And the comparison should include historical match results
    And the comparison should show win percentages
    And the comparison should include recent form

  Scenario: Team transfer history
    Given I have a valid team ID
    When I request transfer history for "santos"
    Then I should get transfer records
    And the records should include incoming transfers
    And the records should include outgoing transfers
    And the records should show transfer fees

  Scenario: Team financial information
    Given I have a valid team ID
    When I request financial data for "flamengo"
    Then I should get financial statistics
    And the data should include revenue information
    And the data should include player values
    And the data should include debt information

  Scenario: Team achievement history
    Given I have a valid team ID
    When I request achievements for "pelé_santos"
    Then I should get trophy history
    And the achievements should include championship titles
    And the achievements should include international trophies
    And the achievements should be chronologically ordered

  Scenario: Team youth academy
    Given I have a valid team ID
    When I request youth academy information for "são_paulo"
    Then I should get academy details
    And the data should include young player prospects
    And the data should include academy facilities
    And the data should include development programs

  Scenario: Invalid team search
    Given I want to search for a team
    When I search for "NonExistentTeam123"
    Then I should get an empty result
    And the response should indicate no matches found
    And the error should be handled gracefully

  Scenario: Team coaching staff
    Given I have a valid team ID
    When I request coaching staff for "internacional"
    Then I should get staff information
    And the data should include head coach details
    And the data should include assistant coaches
    And the data should include technical staff

  Scenario: Team stadium and facilities
    Given I have a valid team ID
    When I request facility information for "grêmio"
    Then I should get stadium details
    And the data should include stadium capacity
    And the data should include facility amenities
    And the data should include location information

  Scenario: Team rivalry information
    Given I have a valid team ID
    When I request rivalry data for "flamengo"
    Then I should get rivalry information
    And the data should include historic rivals
    And the data should include rivalry statistics
    And the data should include memorable matches

  Scenario: Team social media engagement
    Given I have a valid team ID
    When I request social media data for "corinthians"
    Then I should get engagement metrics
    And the data should include follower counts
    And the data should include fan interaction rates
    And the data should show growth trends