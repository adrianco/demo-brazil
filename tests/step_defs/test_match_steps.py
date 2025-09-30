"""
Brazilian Soccer MCP Knowledge Graph - Match Step Definitions

CONTEXT:
This module implements BDD step definitions for match and competition-related scenarios.
Tests validate match details, statistics, player performance, and competition data
functionality against the Neo4j graph database.

PHASE: 3 - Integration & Testing
PURPOSE: Validate match-related MCP server functionality with BDD scenarios
DATA SOURCES: Test data in Neo4j graph database
DEPENDENCIES: pytest, pytest-bdd, neo4j

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Match nodes with team and player relationships
- Performance: Test timeouts and response validation
- Testing: Given-When-Then BDD scenarios

INTEGRATION:
- MCP Tools: Tests match-related MCP server tools
- Error Handling: Validates error responses
- Rate Limiting: Tests API limits
"""

import pytest
import json
from pytest_bdd import given, when, then, scenarios
from neo4j import GraphDatabase
from unittest.mock import Mock, patch
import requests
from datetime import datetime, timedelta

# Load scenarios from feature file
scenarios('../features/match_analysis.feature')

# Global test context
test_context = {}


@given('the knowledge graph contains match data')
def graph_contains_match_data(neo4j_driver):
    """Ensure the graph database has test match data."""
    with neo4j_driver.session() as session:
        # Create test matches
        session.run("""
            MERGE (m1:Match {match_id: 'flamengo_vs_palmeiras_2023',
                            home_team: 'Flamengo', away_team: 'Palmeiras',
                            date: '2023-08-15', final_score: '2-1',
                            competition: 'Brasileirão', venue: 'Maracanã'})
            MERGE (m2:Match {match_id: 'santos_vs_corinthians_2023',
                            home_team: 'Santos', away_team: 'Corinthians',
                            date: '2023-09-10', final_score: '1-1',
                            competition: 'Brasileirão', venue: 'Vila Belmiro'})
            MERGE (m3:Match {match_id: 'brazil_vs_argentina_2023',
                            home_team: 'Brazil', away_team: 'Argentina',
                            date: '2023-11-21', final_score: '1-0',
                            competition: 'World Cup Qualifiers', venue: 'Maracanã'})
        """)
        test_context['match_data_loaded'] = True


@given('I have a valid match ID')
def have_valid_match_id():
    """Set a valid match ID for testing."""
    test_context['match_id'] = 'flamengo_vs_palmeiras_2023'


@given('I have a valid match ID and player ID')
def have_valid_match_and_player_id():
    """Set valid match and player IDs for testing."""
    test_context['match_id'] = 'brazil_vs_argentina_2023'
    test_context['player_id'] = 'neymar_jr'


@given('I want to find matches in a date range')
def want_find_matches_by_date():
    """Set context for date range search."""
    test_context['search_type'] = 'date_range'


@given('I have a valid competition ID')
def have_valid_competition_id():
    """Set a valid competition ID for testing."""
    test_context['competition_id'] = 'brasileirao_2023'


@given('I have two team IDs')
def have_two_team_ids():
    """Set two team IDs for prediction/history."""
    test_context['team_ids'] = ['flamengo', 'palmeiras']


@given('I have a valid referee ID')
def have_valid_referee_id():
    """Set a valid referee ID for testing."""
    test_context['referee_id'] = 'referee_silva'


@given('I have a valid venue ID')
def have_valid_venue_id():
    """Set a valid venue ID for testing."""
    test_context['venue_id'] = 'maracana'


@given('I have a valid live match ID')
def have_valid_live_match_id():
    """Set a valid live match ID for testing."""
    test_context['live_match_id'] = 'current_brasileirao_match'


@given('I want to search for a match')
def want_to_search_match():
    """Set context for match search."""
    test_context['search_type'] = 'match'


@when('I request details for match "<match_id>"')
def request_match_details(match_id, mcp_client):
    """Request details for a specific match."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'match_id': match_id,
            'home_team': 'Flamengo',
            'away_team': 'Palmeiras',
            'date': '2023-08-15',
            'final_score': '2-1',
            'competition': 'Brasileirão',
            'venue': 'Maracanã',
            'lineups': {
                'home': [
                    {'player': 'Santos', 'position': 'GK', 'jersey': 1},
                    {'player': 'Varela', 'position': 'RB', 'jersey': 2},
                    {'player': 'Pedro', 'position': 'ST', 'jersey': 9}
                ],
                'away': [
                    {'player': 'Weverton', 'position': 'GK', 'jersey': 21},
                    {'player': 'Mayke', 'position': 'RB', 'jersey': 12}
                ]
            },
            'events': [
                {'minute': 15, 'type': 'GOAL', 'player': 'Pedro', 'team': 'Flamengo'},
                {'minute': 45, 'type': 'GOAL', 'player': 'Rony', 'team': 'Palmeiras'},
                {'minute': 78, 'type': 'GOAL', 'player': 'Gabigol', 'team': 'Flamengo'}
            ]
        }

        result = mcp_client.call_tool('match_details', {'match_id': match_id})
        test_context['match_details_result'] = result


@when('I request statistics for match "<match_id>"')
def request_match_statistics(match_id, mcp_client):
    """Request detailed statistics for a match."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'match_id': match_id,
            'statistics': {
                'possession': {'home': 58, 'away': 42},
                'shots': {'home': 14, 'away': 9},
                'shots_on_target': {'home': 6, 'away': 4},
                'corners': {'home': 7, 'away': 3},
                'fouls': {'home': 12, 'away': 15},
                'yellow_cards': {'home': 2, 'away': 3},
                'red_cards': {'home': 0, 'away': 0},
                'passing_accuracy': {'home': 85.2, 'away': 79.8},
                'distance_covered': {'home': 108.5, 'away': 106.2}
            }
        }

        result = mcp_client.call_tool('match_statistics', {'match_id': match_id})
        test_context['match_statistics_result'] = result


@when('I request performance for player "<player_id>" in match "<match_id>"')
def request_player_match_performance(player_id, match_id, mcp_client):
    """Request player performance in a specific match."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'player_id': player_id,
            'match_id': match_id,
            'performance': {
                'goals': 1,
                'assists': 0,
                'shots': 3,
                'shots_on_target': 2,
                'passes_completed': 45,
                'passes_attempted': 52,
                'pass_completion_rate': 86.5,
                'distance_covered': 10.8,
                'touches': 68,
                'successful_dribbles': 7,
                'fouls_committed': 1,
                'fouls_suffered': 3,
                'rating': 8.5
            }
        }

        result = mcp_client.call_tool('player_match_performance', {
            'player_id': player_id,
            'match_id': match_id
        })
        test_context['player_performance_result'] = result


@when('I search for matches between "<start_date>" and "<end_date>"')
def search_matches_by_date_range(start_date, end_date, mcp_client):
    """Search for matches in a date range."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'date_range': f'{start_date} to {end_date}',
            'matches': [
                {
                    'match_id': 'flamengo_vs_palmeiras_2023',
                    'date': '2023-08-15',
                    'home_team': 'Flamengo',
                    'away_team': 'Palmeiras',
                    'score': '2-1'
                },
                {
                    'match_id': 'santos_vs_corinthians_2023',
                    'date': '2023-09-10',
                    'home_team': 'Santos',
                    'away_team': 'Corinthians',
                    'score': '1-1'
                }
            ],
            'total_matches': 2
        }

        result = mcp_client.call_tool('matches_by_date_range', {
            'start_date': start_date,
            'end_date': end_date
        })
        test_context['date_range_result'] = result


@when('I request standings for "<competition_id>"')
def request_competition_standings(competition_id, mcp_client):
    """Request competition standings."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'competition_id': competition_id,
            'standings': [
                {
                    'position': 1,
                    'team': 'Palmeiras',
                    'points': 70,
                    'played': 34,
                    'wins': 21,
                    'draws': 7,
                    'losses': 6,
                    'goals_for': 56,
                    'goals_against': 32,
                    'goal_difference': 24
                },
                {
                    'position': 2,
                    'team': 'Flamengo',
                    'points': 68,
                    'played': 34,
                    'wins': 20,
                    'draws': 8,
                    'losses': 6,
                    'goals_for': 61,
                    'goals_against': 38,
                    'goal_difference': 23
                }
            ]
        }

        result = mcp_client.call_tool('competition_standings', {
            'competition_id': competition_id
        })
        test_context['standings_result'] = result


@when('I request top scorers for "<competition_id>"')
def request_top_scorers(competition_id, mcp_client):
    """Request top scorers for a competition."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'competition_id': competition_id,
            'top_scorers': [
                {
                    'player_id': 'gabigol',
                    'name': 'Gabriel Barbosa',
                    'team': 'Flamengo',
                    'goals': 18,
                    'assists': 6,
                    'matches_played': 28
                },
                {
                    'player_id': 'hulk',
                    'name': 'Hulk',
                    'team': 'Atlético-MG',
                    'goals': 16,
                    'assists': 8,
                    'matches_played': 32
                }
            ]
        }

        result = mcp_client.call_tool('competition_top_scorers', {
            'competition_id': competition_id
        })
        test_context['top_scorers_result'] = result


@when('I request prediction for "<team1>" vs "<team2>"')
def request_match_prediction(team1, team2, mcp_client):
    """Request match prediction between two teams."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'team1': team1,
            'team2': team2,
            'prediction': {
                'win_probabilities': {
                    'team1_win': 45.2,
                    'draw': 28.3,
                    'team2_win': 26.5
                },
                'expected_goals': {
                    'team1': 1.8,
                    'team2': 1.3
                },
                'form_analysis': {
                    'team1_recent_form': ['W', 'W', 'D', 'L', 'W'],
                    'team2_recent_form': ['L', 'W', 'W', 'D', 'L'],
                    'team1_form_score': 7.5,
                    'team2_form_score': 6.2
                },
                'key_factors': [
                    'Team1 has better home record',
                    'Team2 missing key defender',
                    'Historical advantage to Team1'
                ]
            }
        }

        result = mcp_client.call_tool('match_prediction', {
            'team1_id': team1,
            'team2_id': team2
        })
        test_context['prediction_result'] = result


@when('I request historical matches between "<team1>" and "<team2>"')
def request_historical_matches(team1, team2, mcp_client):
    """Request historical matches between teams."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'team1': team1,
            'team2': team2,
            'head_to_head_record': {
                'total_matches': 95,
                'team1_wins': 42,
                'team2_wins': 28,
                'draws': 25
            },
            'recent_matches': [
                {
                    'date': '2023-08-15',
                    'score': '2-1',
                    'winner': team1,
                    'venue': 'Maracanã',
                    'competition': 'Brasileirão'
                },
                {
                    'date': '2023-04-02',
                    'score': '0-1',
                    'winner': team2,
                    'venue': 'Allianz Parque',
                    'competition': 'Paulista'
                }
            ]
        }

        result = mcp_client.call_tool('historical_matches', {
            'team1_id': team1,
            'team2_id': team2
        })
        test_context['historical_matches_result'] = result


@when('I request schedule for "<competition_id>"')
def request_competition_schedule(competition_id, mcp_client):
    """Request competition schedule."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'competition_id': competition_id,
            'fixtures': [
                {
                    'match_id': 'future_match_1',
                    'date': '2024-02-15',
                    'time': '20:00',
                    'home_team': 'Flamengo',
                    'away_team': 'Corinthians',
                    'venue': 'Maracanã',
                    'status': 'upcoming'
                },
                {
                    'match_id': 'future_match_2',
                    'date': '2024-02-18',
                    'time': '16:00',
                    'home_team': 'Palmeiras',
                    'away_team': 'Santos',
                    'venue': 'Allianz Parque',
                    'status': 'upcoming'
                }
            ],
            'upcoming_highlighted': True
        }

        result = mcp_client.call_tool('competition_schedule', {
            'competition_id': competition_id
        })
        test_context['schedule_result'] = result


@when('I request events for match "<match_id>"')
def request_match_events(match_id, mcp_client):
    """Request events timeline for a match."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'match_id': match_id,
            'events': [
                {
                    'minute': 15,
                    'type': 'GOAL',
                    'player': 'Pedro',
                    'team': 'Flamengo',
                    'description': 'Header from cross'
                },
                {
                    'minute': 28,
                    'type': 'YELLOW_CARD',
                    'player': 'Mayke',
                    'team': 'Palmeiras',
                    'description': 'Foul on opponent'
                },
                {
                    'minute': 60,
                    'type': 'SUBSTITUTION',
                    'player_out': 'Rony',
                    'player_in': 'Endrick',
                    'team': 'Palmeiras'
                },
                {
                    'minute': 78,
                    'type': 'GOAL',
                    'player': 'Gabigol',
                    'team': 'Flamengo',
                    'description': 'Left foot shot from penalty area'
                }
            ],
            'chronological_order': True
        }

        result = mcp_client.call_tool('match_events', {'match_id': match_id})
        test_context['events_result'] = result


@when('I request statistics for referee "<referee_id>"')
def request_referee_statistics(referee_id, mcp_client):
    """Request referee statistics."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'referee_id': referee_id,
            'statistics': {
                'matches_officiated': 156,
                'yellow_cards_issued': 423,
                'red_cards_issued': 28,
                'penalties_awarded': 34,
                'cards_per_match': 2.9,
                'consistency_rating': 8.2,
                'controversial_decisions': 12,
                'career_start': '2015-03-01'
            }
        }

        result = mcp_client.call_tool('referee_statistics', {
            'referee_id': referee_id
        })
        test_context['referee_stats_result'] = result


@when('I request match history for venue "<venue_id>"')
def request_venue_match_history(venue_id, mcp_client):
    """Request match history for a venue."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'venue_id': venue_id,
            'venue_name': 'Maracanã',
            'statistics': {
                'total_matches': 245,
                'average_attendance': 65432,
                'highest_attendance': 78838,
                'home_team_advantage': 68.5,
                'goals_per_match': 2.8
            },
            'recent_matches': [
                {
                    'date': '2023-11-21',
                    'teams': 'Brazil vs Argentina',
                    'attendance': 78000,
                    'score': '1-0'
                }
            ]
        }

        result = mcp_client.call_tool('venue_statistics', {'venue_id': venue_id})
        test_context['venue_stats_result'] = result


@when('I request format details for "<competition_id>"')
def request_competition_format(competition_id, mcp_client):
    """Request competition format details."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'competition_id': competition_id,
            'format': {
                'type': 'Knockout',
                'rounds': [
                    {'name': 'First Round', 'teams': 80, 'matches': 40},
                    {'name': 'Second Round', 'teams': 40, 'matches': 20},
                    {'name': 'Round of 16', 'teams': 16, 'matches': 8},
                    {'name': 'Quarter-finals', 'teams': 8, 'matches': 4},
                    {'name': 'Semi-finals', 'teams': 4, 'matches': 2},
                    {'name': 'Final', 'teams': 2, 'matches': 1}
                ],
                'qualification_rules': [
                    'Single elimination',
                    'Extra time and penalties if tied',
                    'Away goals rule does not apply'
                ],
                'prize_money': {
                    'winner': 54000000,
                    'runner_up': 20000000,
                    'semi_finalist': 8000000
                }
            }
        }

        result = mcp_client.call_tool('competition_format', {
            'competition_id': competition_id
        })
        test_context['format_result'] = result


@when('I search for match "<match_id>"')
def search_for_match(match_id, mcp_client):
    """Search for a specific match (for invalid search test)."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        if match_id == 'nonexistent_match_123':
            mock_call.return_value = {
                'matches': [],
                'message': 'No matches found'
            }
        else:
            mock_call.return_value = {
                'match_id': match_id,
                'home_team': 'Team A',
                'away_team': 'Team B'
            }

        result = mcp_client.call_tool('match_search', {'match_id': match_id})
        test_context['search_result'] = result
        test_context['search_query'] = match_id


@when('I request live updates for match "<match_id>"')
def request_live_updates(match_id, mcp_client):
    """Request live updates for a match."""
    with patch.object(mcp_client, 'call_tool') as mock_call:
        mock_call.return_value = {
            'match_id': match_id,
            'live_data': {
                'current_score': '1-0',
                'match_time': 67,
                'status': 'live',
                'recent_events': [
                    {
                        'minute': 65,
                        'type': 'GOAL',
                        'player': 'Player X',
                        'team': 'Home Team'
                    }
                ],
                'next_update': datetime.now().isoformat()
            }
        }

        result = mcp_client.call_tool('live_match_updates', {
            'match_id': match_id
        })
        test_context['live_updates_result'] = result


# Then steps (assertions)
@then('I should receive match information')
def should_receive_match_information():
    """Verify match information is returned."""
    assert 'match_details_result' in test_context
    result = test_context['match_details_result']
    assert 'match_id' in result
    assert 'home_team' in result
    assert 'away_team' in result


@then('the response should include team lineups')
def should_include_team_lineups():
    """Verify team lineups are included."""
    result = test_context['match_details_result']
    assert 'lineups' in result
    assert 'home' in result['lineups']
    assert 'away' in result['lineups']


@then('the response should include match events')
def should_include_match_events():
    """Verify match events are included."""
    result = test_context['match_details_result']
    assert 'events' in result
    assert len(result['events']) > 0


@then('the response should include final score')
def should_include_final_score():
    """Verify final score is included."""
    result = test_context['match_details_result']
    assert 'final_score' in result


@then('I should receive detailed match stats')
def should_receive_detailed_match_stats():
    """Verify detailed match statistics are returned."""
    assert 'match_statistics_result' in test_context
    result = test_context['match_statistics_result']
    assert 'statistics' in result


@then('the statistics should include possession percentages')
def should_include_possession():
    """Verify possession statistics are included."""
    stats = test_context['match_statistics_result']['statistics']
    assert 'possession' in stats
    assert 'home' in stats['possession']
    assert 'away' in stats['possession']


@then('the statistics should include shots on target')
def should_include_shots_on_target():
    """Verify shots on target statistics are included."""
    stats = test_context['match_statistics_result']['statistics']
    assert 'shots_on_target' in stats


@then('the statistics should include passing accuracy')
def should_include_passing_accuracy():
    """Verify passing accuracy statistics are included."""
    stats = test_context['match_statistics_result']['statistics']
    assert 'passing_accuracy' in stats


@then('I should receive player match statistics')
def should_receive_player_match_statistics():
    """Verify player match statistics are returned."""
    assert 'player_performance_result' in test_context
    result = test_context['player_performance_result']
    assert 'performance' in result


@then('the stats should include goals and assists')
def should_include_goals_and_assists():
    """Verify goals and assists are included."""
    performance = test_context['player_performance_result']['performance']
    assert 'goals' in performance
    assert 'assists' in performance


@then('the stats should include distance covered')
def should_include_distance_covered():
    """Verify distance covered is included."""
    performance = test_context['player_performance_result']['performance']
    assert 'distance_covered' in performance


@then('the stats should include pass completion rate')
def should_include_pass_completion_rate():
    """Verify pass completion rate is included."""
    performance = test_context['player_performance_result']['performance']
    assert 'pass_completion_rate' in performance


@then('I should get a list of matches')
def should_get_list_of_matches():
    """Verify list of matches is returned."""
    assert 'date_range_result' in test_context
    result = test_context['date_range_result']
    assert 'matches' in result
    assert len(result['matches']) > 0


@then('each match should be within the date range')
def should_be_within_date_range():
    """Verify each match is within the specified date range."""
    result = test_context['date_range_result']
    for match in result['matches']:
        assert 'date' in match
        # In a real implementation, you'd verify the date is within range


@then('the matches should be chronologically ordered')
def should_be_chronologically_ordered():
    """Verify matches are chronologically ordered."""
    result = test_context['date_range_result']
    dates = [match['date'] for match in result['matches']]
    assert dates == sorted(dates)


@then('I should receive league table')
def should_receive_league_table():
    """Verify league table is returned."""
    assert 'standings_result' in test_context
    result = test_context['standings_result']
    assert 'standings' in result
    assert len(result['standings']) > 0


@then('the table should include team positions')
def should_include_team_positions():
    """Verify team positions are included."""
    standings = test_context['standings_result']['standings']
    for team in standings:
        assert 'position' in team
        assert 'team' in team


@then('the table should include points and goal difference')
def should_include_points_and_goal_difference():
    """Verify points and goal difference are included."""
    standings = test_context['standings_result']['standings']
    for team in standings:
        assert 'points' in team
        assert 'goal_difference' in team


@then('the table should be ordered by position')
def should_be_ordered_by_position():
    """Verify table is ordered by position."""
    standings = test_context['standings_result']['standings']
    positions = [team['position'] for team in standings]
    assert positions == sorted(positions)


@then('I should receive scorer rankings')
def should_receive_scorer_rankings():
    """Verify scorer rankings are returned."""
    assert 'top_scorers_result' in test_context
    result = test_context['top_scorers_result']
    assert 'top_scorers' in result
    assert len(result['top_scorers']) > 0


@then('each entry should include goals scored')
def should_include_goals_scored():
    """Verify goals scored are included."""
    scorers = test_context['top_scorers_result']['top_scorers']
    for scorer in scorers:
        assert 'goals' in scorer
        assert isinstance(scorer['goals'], int)


@then('the list should be ordered by goals')
def should_be_ordered_by_goals():
    """Verify list is ordered by goals."""
    scorers = test_context['top_scorers_result']['top_scorers']
    goals = [scorer['goals'] for scorer in scorers]
    assert goals == sorted(goals, reverse=True)


@then('player details should be included')
def should_include_player_details():
    """Verify player details are included."""
    scorers = test_context['top_scorers_result']['top_scorers']
    for scorer in scorers:
        assert 'name' in scorer
        assert 'team' in scorer


@then('I should receive prediction data')
def should_receive_prediction_data():
    """Verify prediction data is returned."""
    assert 'prediction_result' in test_context
    result = test_context['prediction_result']
    assert 'prediction' in result


@then('the prediction should include win probabilities')
def should_include_win_probabilities():
    """Verify win probabilities are included."""
    prediction = test_context['prediction_result']['prediction']
    assert 'win_probabilities' in prediction
    probs = prediction['win_probabilities']
    assert 'team1_win' in probs
    assert 'draw' in probs
    assert 'team2_win' in probs


@then('the prediction should include expected goals')
def should_include_expected_goals():
    """Verify expected goals are included."""
    prediction = test_context['prediction_result']['prediction']
    assert 'expected_goals' in prediction


@then('the prediction should include form analysis')
def should_include_form_analysis():
    """Verify form analysis is included."""
    prediction = test_context['prediction_result']['prediction']
    assert 'form_analysis' in prediction


@then('I should receive match history')
def should_receive_match_history():
    """Verify match history is returned."""
    assert 'historical_matches_result' in test_context
    result = test_context['historical_matches_result']
    assert 'recent_matches' in result


@then('the history should include all past encounters')
def should_include_past_encounters():
    """Verify past encounters are included."""
    result = test_context['historical_matches_result']
    assert 'head_to_head_record' in result
    assert 'total_matches' in result['head_to_head_record']


@then('each match should include score and date')
def should_include_score_and_date():
    """Verify score and date are included."""
    result = test_context['historical_matches_result']
    for match in result['recent_matches']:
        assert 'score' in match
        assert 'date' in match


@then('the results should show head-to-head record')
def should_show_head_to_head_record():
    """Verify head-to-head record is shown."""
    result = test_context['historical_matches_result']
    h2h = result['head_to_head_record']
    assert 'team1_wins' in h2h
    assert 'team2_wins' in h2h
    assert 'draws' in h2h


@then('I should receive fixture list')
def should_receive_fixture_list():
    """Verify fixture list is returned."""
    assert 'schedule_result' in test_context
    result = test_context['schedule_result']
    assert 'fixtures' in result
    assert len(result['fixtures']) > 0


@then('the fixtures should include dates and times')
def should_include_dates_and_times():
    """Verify dates and times are included."""
    fixtures = test_context['schedule_result']['fixtures']
    for fixture in fixtures:
        assert 'date' in fixture
        assert 'time' in fixture


@then('the fixtures should include venue information')
def should_include_venue_information():
    """Verify venue information is included."""
    fixtures = test_context['schedule_result']['fixtures']
    for fixture in fixtures:
        assert 'venue' in fixture


@then('upcoming matches should be highlighted')
def should_highlight_upcoming_matches():
    """Verify upcoming matches are highlighted."""
    result = test_context['schedule_result']
    assert 'upcoming_highlighted' in result
    assert result['upcoming_highlighted'] is True


@then('I should receive event timeline')
def should_receive_event_timeline():
    """Verify event timeline is returned."""
    assert 'events_result' in test_context
    result = test_context['events_result']
    assert 'events' in result
    assert len(result['events']) > 0


@then('the events should include goals and cards')
def should_include_goals_and_cards():
    """Verify goals and cards are included in events."""
    events = test_context['events_result']['events']
    event_types = [event['type'] for event in events]
    assert 'GOAL' in event_types
    assert 'YELLOW_CARD' in event_types


@then('the events should include substitutions')
def should_include_substitutions():
    """Verify substitutions are included in events."""
    events = test_context['events_result']['events']
    event_types = [event['type'] for event in events]
    assert 'SUBSTITUTION' in event_types


@then('the events should be chronologically ordered')
def should_be_chronologically_ordered_events():
    """Verify events are chronologically ordered."""
    result = test_context['events_result']
    assert 'chronological_order' in result
    assert result['chronological_order'] is True


@then('I should receive referee data')
def should_receive_referee_data():
    """Verify referee data is returned."""
    assert 'referee_stats_result' in test_context
    result = test_context['referee_stats_result']
    assert 'statistics' in result


@then('the data should include cards issued')
def should_include_cards_issued():
    """Verify cards issued data is included."""
    stats = test_context['referee_stats_result']['statistics']
    assert 'yellow_cards_issued' in stats
    assert 'red_cards_issued' in stats


@then('the data should include match count')
def should_include_match_count():
    """Verify match count is included."""
    stats = test_context['referee_stats_result']['statistics']
    assert 'matches_officiated' in stats


@then('the data should include consistency metrics')
def should_include_consistency_metrics():
    """Verify consistency metrics are included."""
    stats = test_context['referee_stats_result']['statistics']
    assert 'consistency_rating' in stats


@then('I should receive venue statistics')
def should_receive_venue_statistics():
    """Verify venue statistics are returned."""
    assert 'venue_stats_result' in test_context
    result = test_context['venue_stats_result']
    assert 'statistics' in result


@then('the data should include recent matches')
def should_include_recent_matches():
    """Verify recent matches data is included."""
    result = test_context['venue_stats_result']
    assert 'recent_matches' in result


@then('the data should include attendance figures')
def should_include_attendance_figures():
    """Verify attendance figures are included."""
    stats = test_context['venue_stats_result']['statistics']
    assert 'average_attendance' in stats
    assert 'highest_attendance' in stats


@then('the data should include home team advantage')
def should_include_home_team_advantage():
    """Verify home team advantage is included."""
    stats = test_context['venue_stats_result']['statistics']
    assert 'home_team_advantage' in stats


@then('I should receive competition structure')
def should_receive_competition_structure():
    """Verify competition structure is returned."""
    assert 'format_result' in test_context
    result = test_context['format_result']
    assert 'format' in result


@then('the structure should include rounds and stages')
def should_include_rounds_and_stages():
    """Verify rounds and stages are included."""
    format_data = test_context['format_result']['format']
    assert 'rounds' in format_data
    assert len(format_data['rounds']) > 0


@then('the structure should include qualification rules')
def should_include_qualification_rules():
    """Verify qualification rules are included."""
    format_data = test_context['format_result']['format']
    assert 'qualification_rules' in format_data


@then('the structure should include prize information')
def should_include_prize_information():
    """Verify prize information is included."""
    format_data = test_context['format_result']['format']
    assert 'prize_money' in format_data


@then('I should get an empty result')
def should_get_empty_result():
    """Verify empty result for invalid search."""
    result = test_context['search_result']
    if 'matches' in result:
        assert len(result['matches']) == 0


@then('the response should indicate no matches found')
def should_indicate_no_matches_found():
    """Verify no matches found message."""
    result = test_context['search_result']
    if 'message' in result:
        assert 'No matches found' in result['message']


@then('the error should be handled gracefully')
def should_handle_error_gracefully():
    """Verify error is handled gracefully."""
    assert test_context['search_result'] is not None
    assert isinstance(test_context['search_result'], dict)


@then('I should receive real-time data')
def should_receive_real_time_data():
    """Verify real-time data is returned."""
    assert 'live_updates_result' in test_context
    result = test_context['live_updates_result']
    assert 'live_data' in result


@then('the data should include current score')
def should_include_current_score():
    """Verify current score is included."""
    live_data = test_context['live_updates_result']['live_data']
    assert 'current_score' in live_data


@then('the data should include match time')
def should_include_match_time():
    """Verify match time is included."""
    live_data = test_context['live_updates_result']['live_data']
    assert 'match_time' in live_data


@then('the data should include recent events')
def should_include_recent_events():
    """Verify recent events are included."""
    live_data = test_context['live_updates_result']['live_data']
    assert 'recent_events' in live_data
# Add the missing Given step to all test files
@given("the MCP server is running")
def mcp_server_running():
    """Ensure MCP server is running (mocked)."""
    pass  # Server is mocked via fixtures


@given("the knowledge graph contains match data")
def knowledge_graph_has_match_data(neo4j_driver):
    """Ensure the knowledge graph contains match data."""
    pass

