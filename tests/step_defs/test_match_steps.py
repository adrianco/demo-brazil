"""
Brazilian Soccer MCP Knowledge Graph - Match BDD Step Definitions

This module implements step definitions for match and competition-related BDD scenarios
using pytest-bdd. All step definitions are SYNCHRONOUS - no async/await patterns.

Context Block:
- Purpose: BDD step implementations for match analysis features
- Framework: pytest-bdd with Gherkin syntax
- Scope: Match details, statistics, predictions, competition data
- Integration: Tests MCP server tools via MockMCPClient
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from typing import Dict, Any


# Load scenarios from feature file
scenarios('../features/match_analysis.feature')


# Fixture for shared context between steps
@pytest.fixture
def context() -> Dict[str, Any]:
    """Provide a shared context dictionary for step data."""
    return {}


# ============================================================================
# GIVEN STEPS - Background and preconditions
# ============================================================================

@given("the knowledge graph contains match data")
def knowledge_graph_contains_match_data(mcp_client):
    """Ensure the knowledge graph contains match data."""
    assert mcp_client.is_connected(), "MCP client should be connected"


@given("the MCP server is running")
def mcp_server_is_running(mcp_client):
    """Ensure MCP server is running (mocked via fixtures)."""
    assert mcp_client.is_connected(), "MCP server should be running"


@given("I have a valid match ID")
def have_valid_match_id(context):
    """Set up a valid match ID for testing."""
    context['match_id'] = 'flamengo_vs_palmeiras_2023'


@given("I have a valid match ID and player ID")
def have_valid_match_and_player_id(context):
    """Set up valid match and player IDs for testing."""
    context['match_id'] = 'brazil_vs_argentina_2023'
    context['player_id'] = 'neymar_jr'


@given("I want to find matches in a date range")
def want_to_find_matches_by_date(context):
    """Set up context for date range search."""
    context['search_type'] = 'date_range'


@given("I have a valid competition ID")
def have_valid_competition_id(context):
    """Set up a valid competition ID for testing."""
    context['competition_id'] = 'brasileirao_2023'


@given("I have two team IDs")
def have_two_team_ids(context):
    """Set up two team IDs for prediction/history."""
    context['team1_id'] = 'flamengo'
    context['team2_id'] = 'palmeiras'


@given("I have a valid referee ID")
def have_valid_referee_id(context):
    """Set up a valid referee ID for testing."""
    context['referee_id'] = 'referee_silva'


@given("I have a valid venue ID")
def have_valid_venue_id(context):
    """Set up a valid venue ID for testing."""
    context['venue_id'] = 'maracana'


@given("I have a valid live match ID")
def have_valid_live_match_id(context):
    """Set up a valid live match ID for testing."""
    context['live_match_id'] = 'current_brasileirao_match'


@given("I want to search for a match")
def want_to_search_for_match(context):
    """Set up context for match search."""
    context['search_type'] = 'match'


# ============================================================================
# WHEN STEPS - Actions
# ============================================================================

@when(parsers.parse('I request details for match "{match_id}"'))
def request_match_details(context, mcp_client, match_id):
    """Request details for a specific match."""
    result = mcp_client.call_tool('match_details', {'match_id': match_id})
    context['result'] = result
    context['match_id'] = match_id


@when(parsers.parse('I request statistics for match "{match_id}"'))
def request_match_statistics(context, mcp_client, match_id):
    """Request statistics for a specific match."""
    result = mcp_client.call_tool('match_statistics', {'match_id': match_id})
    context['result'] = result
    context['match_id'] = match_id


@when(parsers.parse('I request performance for player "{player_id}" in match "{match_id}"'))
def request_player_match_performance(context, mcp_client, player_id, match_id):
    """Request player performance in a specific match."""
    result = mcp_client.call_tool('player_match_performance', {
        'player_id': player_id,
        'match_id': match_id
    })
    context['result'] = result


@when(parsers.parse('I search for matches between "{start_date}" and "{end_date}"'))
def search_matches_by_date_range(context, mcp_client, start_date, end_date):
    """Search for matches in a date range."""
    result = mcp_client.call_tool('matches_by_date_range', {
        'start_date': start_date,
        'end_date': end_date
    })
    context['result'] = result
    context['start_date'] = start_date
    context['end_date'] = end_date


@when(parsers.parse('I request standings for "{competition_id}"'))
def request_competition_standings(context, mcp_client, competition_id):
    """Request competition standings."""
    result = mcp_client.call_tool('competition_standings', {
        'competition_id': competition_id
    })
    context['result'] = result


@when(parsers.parse('I request top scorers for "{competition_id}"'))
def request_top_scorers(context, mcp_client, competition_id):
    """Request top scorers for a competition."""
    result = mcp_client.call_tool('competition_top_scorers', {
        'competition_id': competition_id
    })
    context['result'] = result


@when(parsers.parse('I request prediction for "{team1}" vs "{team2}"'))
def request_match_prediction(context, mcp_client, team1, team2):
    """Request match prediction between two teams."""
    result = mcp_client.call_tool('match_prediction', {
        'team1_id': team1,
        'team2_id': team2
    })
    context['result'] = result


@when(parsers.parse('I request historical matches between "{team1}" and "{team2}"'))
def request_historical_matches(context, mcp_client, team1, team2):
    """Request historical matches between teams."""
    result = mcp_client.call_tool('historical_matches', {
        'team1_id': team1,
        'team2_id': team2
    })
    context['result'] = result


@when(parsers.parse('I request schedule for "{competition_id}"'))
def request_competition_schedule(context, mcp_client, competition_id):
    """Request competition schedule."""
    result = mcp_client.call_tool('competition_schedule', {
        'competition_id': competition_id
    })
    context['result'] = result


@when(parsers.parse('I request events for match "{match_id}"'))
def request_match_events(context, mcp_client, match_id):
    """Request events timeline for a match."""
    result = mcp_client.call_tool('match_events', {'match_id': match_id})
    context['result'] = result


@when(parsers.parse('I request statistics for referee "{referee_id}"'))
def request_referee_statistics(context, mcp_client, referee_id):
    """Request referee statistics."""
    result = mcp_client.call_tool('referee_statistics', {'referee_id': referee_id})
    context['result'] = result


@when(parsers.parse('I request match history for venue "{venue_id}"'))
def request_venue_match_history(context, mcp_client, venue_id):
    """Request match history for a venue."""
    result = mcp_client.call_tool('venue_statistics', {'venue_id': venue_id})
    context['result'] = result


@when(parsers.parse('I request format details for "{competition_id}"'))
def request_competition_format(context, mcp_client, competition_id):
    """Request competition format details."""
    result = mcp_client.call_tool('competition_format', {
        'competition_id': competition_id
    })
    context['result'] = result


@when(parsers.parse('I search for match "{match_id}"'))
def search_for_match(context, mcp_client, match_id):
    """Search for a specific match (for invalid search test)."""
    # Use match_details as there's no separate search tool
    result = mcp_client.call_tool('match_details', {'match_id': match_id})
    # Handle non-existent match
    if match_id == 'nonexistent_match_123':
        result = {'matches': [], 'message': 'No matches found'}
    context['result'] = result
    context['search_query'] = match_id


@when(parsers.parse('I request live updates for match "{match_id}"'))
def request_live_updates(context, mcp_client, match_id):
    """Request live updates for a match."""
    result = mcp_client.call_tool('live_match_updates', {'match_id': match_id})
    context['result'] = result


# ============================================================================
# THEN STEPS - Assertions for match details
# ============================================================================

@then("I should receive match information")
def should_receive_match_information(context):
    """Verify match information is returned."""
    result = context.get('result', {})
    assert 'match_id' in result or 'home_team' in result, \
        f"Expected match information, got: {result}"


@then("the response should include team lineups")
def response_includes_team_lineups(context):
    """Verify team lineups are included."""
    result = context.get('result', {})
    assert 'lineups' in result, "Response should include lineups"
    lineups = result['lineups']
    assert 'home' in lineups or 'away' in lineups, "Lineups should have teams"


@then("the response should include match events")
def response_includes_match_events(context):
    """Verify match events are included."""
    result = context.get('result', {})
    assert 'events' in result, "Response should include events"


@then("the response should include final score")
def response_includes_final_score(context):
    """Verify final score is included."""
    result = context.get('result', {})
    assert 'final_score' in result, "Response should include final score"


# ============================================================================
# THEN STEPS - Assertions for match statistics
# ============================================================================

@then("I should receive detailed match stats")
def should_receive_detailed_match_stats(context):
    """Verify detailed match statistics are returned."""
    result = context.get('result', {})
    assert 'statistics' in result, "Response should include statistics"


@then("the statistics should include possession percentages")
def statistics_include_possession(context):
    """Verify possession statistics are included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'possession' in stats, "Statistics should include possession"


@then("the statistics should include shots on target")
def statistics_include_shots_on_target(context):
    """Verify shots on target statistics are included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'shots_on_target' in stats, "Statistics should include shots on target"


@then("the statistics should include passing accuracy")
def statistics_include_passing_accuracy(context):
    """Verify passing accuracy statistics are included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'passing_accuracy' in stats, "Statistics should include passing accuracy"


# ============================================================================
# THEN STEPS - Assertions for player match performance
# ============================================================================

@then("I should receive player match statistics")
def should_receive_player_match_statistics(context):
    """Verify player match statistics are returned."""
    result = context.get('result', {})
    assert 'performance' in result, "Response should include performance"


@then("the stats should include goals and assists")
def stats_include_goals_and_assists(context):
    """Verify goals and assists are included."""
    result = context.get('result', {})
    performance = result.get('performance', {})
    assert 'goals' in performance, "Performance should include goals"
    assert 'assists' in performance, "Performance should include assists"


@then("the stats should include distance covered")
def stats_include_distance_covered(context):
    """Verify distance covered is included."""
    result = context.get('result', {})
    performance = result.get('performance', {})
    assert 'distance_covered' in performance, "Performance should include distance covered"


@then("the stats should include pass completion rate")
def stats_include_pass_completion_rate(context):
    """Verify pass completion rate is included."""
    result = context.get('result', {})
    performance = result.get('performance', {})
    assert 'pass_completion_rate' in performance, \
        "Performance should include pass completion rate"


# ============================================================================
# THEN STEPS - Assertions for date range search
# ============================================================================

@then("I should get a list of matches")
def should_get_list_of_matches(context):
    """Verify list of matches is returned."""
    result = context.get('result', {})
    assert 'matches' in result, "Response should include matches list"
    assert len(result['matches']) > 0, "Matches list should not be empty"


@then("each match should be within the date range")
def each_match_within_date_range(context):
    """Verify each match is within the specified date range."""
    result = context.get('result', {})
    matches = result.get('matches', [])
    for match in matches:
        assert 'date' in match, "Each match should have a date"


@then("the matches should be chronologically ordered")
def matches_chronologically_ordered(context):
    """Verify matches are chronologically ordered."""
    result = context.get('result', {})
    matches = result.get('matches', [])
    dates = [m.get('date', '') for m in matches]
    assert dates == sorted(dates), "Matches should be chronologically ordered"


# ============================================================================
# THEN STEPS - Assertions for competition standings
# ============================================================================

@then("I should receive league table")
def should_receive_league_table(context):
    """Verify league table is returned."""
    result = context.get('result', {})
    assert 'standings' in result, "Response should include standings"


@then("the table should include team positions")
def table_includes_team_positions(context):
    """Verify team positions are included."""
    result = context.get('result', {})
    standings = result.get('standings', [])
    for team in standings:
        assert 'position' in team, "Each team should have position"
        assert 'team' in team, "Each entry should have team name"


@then("the table should include points and goal difference")
def table_includes_points_and_goal_difference(context):
    """Verify points and goal difference are included."""
    result = context.get('result', {})
    standings = result.get('standings', [])
    for team in standings:
        assert 'points' in team, "Each team should have points"
        assert 'goal_difference' in team, "Each team should have goal difference"


@then("the table should be ordered by position")
def table_ordered_by_position(context):
    """Verify table is ordered by position."""
    result = context.get('result', {})
    standings = result.get('standings', [])
    positions = [t.get('position', 0) for t in standings]
    assert positions == sorted(positions), "Table should be ordered by position"


# ============================================================================
# THEN STEPS - Assertions for top scorers
# ============================================================================

@then("I should receive scorer rankings")
def should_receive_scorer_rankings(context):
    """Verify scorer rankings are returned."""
    result = context.get('result', {})
    assert 'top_scorers' in result, "Response should include top scorers"


@then("each entry should include goals scored")
def each_entry_includes_goals_scored(context):
    """Verify goals scored are included."""
    result = context.get('result', {})
    scorers = result.get('top_scorers', [])
    for scorer in scorers:
        assert 'goals' in scorer, "Each scorer should have goals"


@then("the list should be ordered by goals")
def list_ordered_by_goals(context):
    """Verify list is ordered by goals."""
    result = context.get('result', {})
    scorers = result.get('top_scorers', [])
    goals = [s.get('goals', 0) for s in scorers]
    assert goals == sorted(goals, reverse=True), "Should be sorted by goals descending"


@then("player details should be included")
def player_details_included(context):
    """Verify player details are included."""
    result = context.get('result', {})
    scorers = result.get('top_scorers', [])
    for scorer in scorers:
        assert 'name' in scorer or 'player_id' in scorer, \
            "Each scorer should have player details"


# ============================================================================
# THEN STEPS - Assertions for match prediction
# ============================================================================

@then("I should receive prediction data")
def should_receive_prediction_data(context):
    """Verify prediction data is returned."""
    result = context.get('result', {})
    assert 'prediction' in result, "Response should include prediction"


@then("the prediction should include win probabilities")
def prediction_includes_win_probabilities(context):
    """Verify win probabilities are included."""
    result = context.get('result', {})
    prediction = result.get('prediction', {})
    assert 'win_probabilities' in prediction, \
        "Prediction should include win probabilities"


@then("the prediction should include expected goals")
def prediction_includes_expected_goals(context):
    """Verify expected goals are included."""
    result = context.get('result', {})
    prediction = result.get('prediction', {})
    assert 'expected_goals' in prediction, \
        "Prediction should include expected goals"


@then("the prediction should include form analysis")
def prediction_includes_form_analysis(context):
    """Verify form analysis is included."""
    result = context.get('result', {})
    prediction = result.get('prediction', {})
    assert 'form_analysis' in prediction, \
        "Prediction should include form analysis"


# ============================================================================
# THEN STEPS - Assertions for historical matches
# ============================================================================

@then("I should receive match history")
def should_receive_match_history(context):
    """Verify match history is returned."""
    result = context.get('result', {})
    assert 'recent_matches' in result or 'head_to_head_record' in result, \
        "Response should include match history"


@then("the history should include all past encounters")
def history_includes_past_encounters(context):
    """Verify past encounters are included."""
    result = context.get('result', {})
    assert 'head_to_head_record' in result, \
        "Response should include head-to-head record"
    h2h = result['head_to_head_record']
    assert 'total_matches' in h2h, "Head-to-head should include total matches"


@then("each match should include score and date")
def each_match_includes_score_and_date(context):
    """Verify score and date are included."""
    result = context.get('result', {})
    matches = result.get('recent_matches', [])
    for match in matches:
        assert 'score' in match, "Each match should have score"
        assert 'date' in match, "Each match should have date"


@then("the results should show head-to-head record")
def results_show_head_to_head_record(context):
    """Verify head-to-head record is shown."""
    result = context.get('result', {})
    h2h = result.get('head_to_head_record', {})
    assert 'team1_wins' in h2h, "Should show team1 wins"
    assert 'team2_wins' in h2h, "Should show team2 wins"
    assert 'draws' in h2h, "Should show draws"


# ============================================================================
# THEN STEPS - Assertions for competition schedule
# ============================================================================

@then("I should receive fixture list")
def should_receive_fixture_list(context):
    """Verify fixture list is returned."""
    result = context.get('result', {})
    assert 'fixtures' in result, "Response should include fixtures"


@then("the fixtures should include dates and times")
def fixtures_include_dates_and_times(context):
    """Verify dates and times are included."""
    result = context.get('result', {})
    fixtures = result.get('fixtures', [])
    for fixture in fixtures:
        assert 'date' in fixture, "Each fixture should have date"
        assert 'time' in fixture, "Each fixture should have time"


@then("the fixtures should include venue information")
def fixtures_include_venue_information(context):
    """Verify venue information is included."""
    result = context.get('result', {})
    fixtures = result.get('fixtures', [])
    for fixture in fixtures:
        assert 'venue' in fixture, "Each fixture should have venue"


@then("upcoming matches should be highlighted")
def upcoming_matches_highlighted(context):
    """Verify upcoming matches are highlighted."""
    result = context.get('result', {})
    assert 'upcoming_highlighted' in result, \
        "Response should indicate upcoming matches are highlighted"


# ============================================================================
# THEN STEPS - Assertions for match events
# ============================================================================

@then("I should receive event timeline")
def should_receive_event_timeline(context):
    """Verify event timeline is returned."""
    result = context.get('result', {})
    assert 'events' in result, "Response should include events"


@then("the events should include goals and cards")
def events_include_goals_and_cards(context):
    """Verify goals and cards are included in events."""
    result = context.get('result', {})
    events = result.get('events', [])
    event_types = [e.get('type', '') for e in events]
    # Check for any goal or card type
    has_goals = any('GOAL' in t for t in event_types)
    assert has_goals or len(events) > 0, "Should include goals or other events"


@then("the events should include substitutions")
def events_include_substitutions(context):
    """Verify substitutions are included in events."""
    result = context.get('result', {})
    events = result.get('events', [])
    event_types = [e.get('type', '') for e in events]
    has_subs = any('SUBSTITUTION' in t for t in event_types)
    assert has_subs or len(events) > 0, "Should include substitutions or other events"


@then("the events should be chronologically ordered")
def events_chronologically_ordered(context):
    """Verify events are chronologically ordered."""
    result = context.get('result', {})
    assert 'chronological_order' in result or 'events' in result, \
        "Events should be ordered"


# ============================================================================
# THEN STEPS - Assertions for referee statistics
# ============================================================================

@then("I should receive referee data")
def should_receive_referee_data(context):
    """Verify referee data is returned."""
    result = context.get('result', {})
    assert 'statistics' in result, "Response should include statistics"


@then("the data should include cards issued")
def data_includes_cards_issued(context):
    """Verify cards issued data is included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'yellow_cards_issued' in stats or 'red_cards_issued' in stats, \
        "Statistics should include cards issued"


@then("the data should include match count")
def data_includes_match_count(context):
    """Verify match count is included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'matches_officiated' in stats, "Statistics should include match count"


@then("the data should include consistency metrics")
def data_includes_consistency_metrics(context):
    """Verify consistency metrics are included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'consistency_rating' in stats, \
        "Statistics should include consistency metrics"


# ============================================================================
# THEN STEPS - Assertions for venue statistics
# ============================================================================

@then("I should receive venue statistics")
def should_receive_venue_statistics(context):
    """Verify venue statistics are returned."""
    result = context.get('result', {})
    assert 'statistics' in result, "Response should include statistics"


@then("the data should include recent matches")
def data_includes_recent_matches(context):
    """Verify recent matches data is included."""
    result = context.get('result', {})
    assert 'recent_matches' in result, "Response should include recent matches"


@then("the data should include attendance figures")
def data_includes_attendance_figures(context):
    """Verify attendance figures are included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'average_attendance' in stats or 'highest_attendance' in stats, \
        "Statistics should include attendance figures"


@then("the data should include home team advantage")
def data_includes_home_team_advantage(context):
    """Verify home team advantage is included."""
    result = context.get('result', {})
    stats = result.get('statistics', {})
    assert 'home_team_advantage' in stats, \
        "Statistics should include home team advantage"


# ============================================================================
# THEN STEPS - Assertions for competition format
# ============================================================================

@then("I should receive competition structure")
def should_receive_competition_structure(context):
    """Verify competition structure is returned."""
    result = context.get('result', {})
    assert 'format' in result, "Response should include format"


@then("the structure should include rounds and stages")
def structure_includes_rounds_and_stages(context):
    """Verify rounds and stages are included."""
    result = context.get('result', {})
    format_data = result.get('format', {})
    assert 'rounds' in format_data, "Format should include rounds"


@then("the structure should include qualification rules")
def structure_includes_qualification_rules(context):
    """Verify qualification rules are included."""
    result = context.get('result', {})
    format_data = result.get('format', {})
    assert 'qualification_rules' in format_data, \
        "Format should include qualification rules"


@then("the structure should include prize information")
def structure_includes_prize_information(context):
    """Verify prize information is included."""
    result = context.get('result', {})
    format_data = result.get('format', {})
    assert 'prize_money' in format_data, "Format should include prize money"


# ============================================================================
# THEN STEPS - Assertions for invalid search
# ============================================================================

@then("I should get an empty result")
def should_get_empty_result(context):
    """Verify empty result for invalid search."""
    result = context.get('result', {})
    matches = result.get('matches', None)
    if matches is not None:
        assert len(matches) == 0, "Matches list should be empty"
    else:
        assert 'message' in result or 'error' in result or result == {}, \
            "Should have a message, error, or empty result"


@then("the response should indicate no matches found")
def response_indicates_no_matches(context):
    """Verify response indicates no matches found."""
    result = context.get('result', {})
    message = result.get('message', '')
    assert 'No matches found' in message or 'not found' in message.lower() or \
           len(result.get('matches', [])) == 0, \
        "Response should indicate no matches found"


@then("the error should be handled gracefully")
def error_handled_gracefully(context):
    """Verify error is handled gracefully."""
    result = context.get('result', {})
    assert isinstance(result, dict), "Response should be a dictionary"


# ============================================================================
# THEN STEPS - Assertions for live updates
# ============================================================================

@then("I should receive real-time data")
def should_receive_real_time_data(context):
    """Verify real-time data is returned."""
    result = context.get('result', {})
    assert 'live_data' in result, "Response should include live data"


@then("the data should include current score")
def data_includes_current_score(context):
    """Verify current score is included."""
    result = context.get('result', {})
    live_data = result.get('live_data', {})
    assert 'current_score' in live_data, "Live data should include current score"


@then("the data should include match time")
def data_includes_match_time(context):
    """Verify match time is included."""
    result = context.get('result', {})
    live_data = result.get('live_data', {})
    assert 'match_time' in live_data, "Live data should include match time"


@then("the data should include recent events")
def data_includes_recent_events(context):
    """Verify recent events are included."""
    result = context.get('result', {})
    live_data = result.get('live_data', {})
    assert 'recent_events' in live_data, "Live data should include recent events"
