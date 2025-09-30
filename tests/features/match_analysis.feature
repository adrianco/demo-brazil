Feature: Match Analysis
  As a Brazilian soccer enthusiast
  I want to analyze match data and competition information
  So that I can understand game statistics and tournament results

  Background:
    Given the knowledge graph contains match data
    And the MCP server is running

  Scenario: Get match details
    Given I have a valid match ID
    When I request details for match "flamengo_vs_palmeiras_2023"
    Then I should receive match information
    And the response should include team lineups
    And the response should include match events
    And the response should include final score

  Scenario: Analyze match statistics
    Given I have a valid match ID
    When I request statistics for match "santos_vs_corinthians_2023"
    Then I should receive detailed match stats
    And the statistics should include possession percentages
    And the statistics should include shots on target
    And the statistics should include passing accuracy

  Scenario: Get player performance in match
    Given I have a valid match ID and player ID
    When I request performance for player "neymar_jr" in match "brazil_vs_argentina_2023"
    Then I should receive player match statistics
    And the stats should include goals and assists
    And the stats should include distance covered
    And the stats should include pass completion rate

  Scenario: Search matches by date range
    Given I want to find matches in a date range
    When I search for matches between "2023-01-01" and "2023-12-31"
    Then I should get a list of matches
    And each match should be within the date range
    And the matches should be chronologically ordered

  Scenario: Competition standings
    Given I have a valid competition ID
    When I request standings for "brasileirao_2023"
    Then I should receive league table
    And the table should include team positions
    And the table should include points and goal difference
    And the table should be ordered by position

  Scenario: Top scorer in competition
    Given I have a valid competition ID
    When I request top scorers for "copa_libertadores_2023"
    Then I should receive scorer rankings
    And each entry should include goals scored
    And the list should be ordered by goals
    And player details should be included

  Scenario: Match prediction analysis
    Given I have two team IDs
    When I request prediction for "flamengo" vs "palmeiras"
    Then I should receive prediction data
    And the prediction should include win probabilities
    And the prediction should include expected goals
    And the prediction should include form analysis

  Scenario: Historical match results
    Given I have two team IDs
    When I request historical matches between "corinthians" and "são_paulo"
    Then I should receive match history
    And the history should include all past encounters
    And each match should include score and date
    And the results should show head-to-head record

  Scenario: Competition schedule
    Given I have a valid competition ID
    When I request schedule for "brasileirao_2024"
    Then I should receive fixture list
    And the fixtures should include dates and times
    And the fixtures should include venue information
    And upcoming matches should be highlighted

  Scenario: Match events timeline
    Given I have a valid match ID
    When I request events for match "final_libertadores_2023"
    Then I should receive event timeline
    And the events should include goals and cards
    And the events should include substitutions
    And the events should be chronologically ordered

  Scenario: Referee statistics
    Given I have a valid referee ID
    When I request statistics for referee "referee_silva"
    Then I should receive referee data
    And the data should include cards issued
    And the data should include match count
    And the data should include consistency metrics

  Scenario: Venue match history
    Given I have a valid venue ID
    When I request match history for venue "maracana"
    Then I should receive venue statistics
    And the data should include recent matches
    And the data should include attendance figures
    And the data should include home team advantage

  Scenario: Competition format analysis
    Given I have a valid competition ID
    When I request format details for "copa_do_brasil_2023"
    Then I should receive competition structure
    And the structure should include rounds and stages
    And the structure should include qualification rules
    And the structure should include prize information

  Scenario: Invalid match search
    Given I want to search for a match
    When I search for match "nonexistent_match_123"
    Then I should get an empty result
    And the response should indicate no matches found
    And the error should be handled gracefully

  Scenario: Live match updates
    Given I have a valid live match ID
    When I request live updates for match "current_brasileirao_match"
    Then I should receive real-time data
    And the data should include current score
    And the data should include match time
    And the data should include recent events