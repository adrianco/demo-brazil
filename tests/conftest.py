"""
Brazilian Soccer MCP Knowledge Graph - Pytest Configuration

CONTEXT:
This module provides pytest fixtures and configuration for the Brazilian Soccer
Knowledge Graph BDD test suite. It sets up test environment, database connections,
and mock MCP client for comprehensive testing.

PHASE: 3 - Integration & Testing
PURPOSE: Configure test environment and provide shared fixtures
DATA SOURCES: Test Neo4j database and mock MCP server
DEPENDENCIES: pytest, pytest-bdd, neo4j, mock

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Test Database: Isolated test instance
- MCP Client: Mock implementation for testing
- Test Coverage: All 13 MCP server tools

INTEGRATION:
- BDD Framework: pytest-bdd with Given-When-Then scenarios
- Mock Services: Mock MCP client and Neo4j driver
- Test Data: Automated test data setup and teardown
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from neo4j import GraphDatabase
from typing import Dict, Any, Optional


# Test configuration
TEST_CONFIG = {
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'username': 'neo4j',
        'password': 'neo4j123',
        'database': 'neo4j'
    },
    'mcp_server': {
        'host': 'localhost',
        'port': 8000,
        'timeout': 30
    },
    'test_data': {
        'players': {
            'neymar_jr': {
                'name': 'Neymar Jr',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '1992-02-05',
                'current_team': 'PSG',
                'market_value': 90000000
            },
            'vinicius_jr': {
                'name': 'Vinicius Jr',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '2000-07-12',
                'current_team': 'Real Madrid',
                'market_value': 100000000
            },
            'ronaldinho': {
                'name': 'Ronaldinho',
                'position': 'Attacking Midfielder',
                'nationality': 'Brazil',
                'birth_date': '1980-03-21',
                'current_team': 'Retired',
                'market_value': 0
            }
        },
        'teams': {
            'flamengo': {
                'name': 'Flamengo',
                'league': 'Série A',
                'founded': 1895,
                'stadium': 'Maracanã',
                'capacity': 78838,
                'city': 'Rio de Janeiro'
            },
            'palmeiras': {
                'name': 'Palmeiras',
                'league': 'Série A',
                'founded': 1914,
                'stadium': 'Allianz Parque',
                'capacity': 43713,
                'city': 'São Paulo'
            }
        },
        'matches': {
            'flamengo_vs_palmeiras_2023': {
                'home_team': 'Flamengo',
                'away_team': 'Palmeiras',
                'date': '2023-08-15',
                'final_score': '2-1',
                'competition': 'Brasileirão',
                'venue': 'Maracanã'
            }
        }
    }
}


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self, test_config: Dict[str, Any]):
        self.config = test_config
        self.connected = False
        self.call_count = 0
        self.last_call = None

    def connect(self) -> bool:
        """Mock connection to MCP server."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Mock disconnection from MCP server."""
        self.connected = False

    def is_connected(self) -> bool:
        """Check if mock client is connected."""
        return self.connected

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool call with predefined responses."""
        self.call_count += 1
        self.last_call = {'tool': tool_name, 'args': arguments}

        # Default responses for different tools
        responses = {
            'player_search': self._mock_player_search(arguments),
            'player_statistics': self._mock_player_statistics(arguments),
            'players_by_position': self._mock_players_by_position(arguments),
            'player_career_history': self._mock_player_career_history(arguments),
            'player_comparison': self._mock_player_comparison(arguments),
            'players_by_age_range': self._mock_players_by_age_range(arguments),
            'player_injury_history': self._mock_player_injury_history(arguments),
            'top_goal_scorers': self._mock_top_goal_scorers(arguments),
            'player_social_media': self._mock_player_social_media(arguments),
            'team_search': self._mock_team_search(arguments),
            'team_roster': self._mock_team_roster(arguments),
            'team_statistics': self._mock_team_statistics(arguments),
            'teams_by_competition': self._mock_teams_by_competition(arguments),
            'team_comparison': self._mock_team_comparison(arguments),
            'team_transfers': self._mock_team_transfers(arguments),
            'team_finances': self._mock_team_finances(arguments),
            'team_achievements': self._mock_team_achievements(arguments),
            'team_youth_academy': self._mock_team_youth_academy(arguments),
            'team_coaching_staff': self._mock_team_coaching_staff(arguments),
            'team_facilities': self._mock_team_facilities(arguments),
            'team_rivalries': self._mock_team_rivalries(arguments),
            'team_social_media': self._mock_team_social_media(arguments),
            'match_details': self._mock_match_details(arguments),
            'match_statistics': self._mock_match_statistics(arguments),
            'player_match_performance': self._mock_player_match_performance(arguments),
            'matches_by_date_range': self._mock_matches_by_date_range(arguments),
            'competition_standings': self._mock_competition_standings(arguments),
            'competition_top_scorers': self._mock_competition_top_scorers(arguments),
            'match_prediction': self._mock_match_prediction(arguments),
            'historical_matches': self._mock_historical_matches(arguments),
            'competition_schedule': self._mock_competition_schedule(arguments),
            'match_events': self._mock_match_events(arguments),
            'referee_statistics': self._mock_referee_statistics(arguments),
            'venue_statistics': self._mock_venue_statistics(arguments),
            'competition_format': self._mock_competition_format(arguments),
            'live_match_updates': self._mock_live_match_updates(arguments)
        }

        return responses.get(tool_name, {'error': f'Unknown tool: {tool_name}'})

    def _mock_player_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player search response."""
        name = args.get('name', '').lower()
        if 'neymar' in name:
            return {
                'player_id': 'neymar_jr',
                'name': 'Neymar Jr',
                'position': 'Forward',
                'nationality': 'Brazil',
                'current_team': 'PSG',
                'national_caps': 128,
                'career_info': {'clubs': ['Santos', 'Barcelona', 'PSG']},
                'birth_date': '1992-02-05'
            }
        elif 'nonexistent' in name:
            return {'players': [], 'message': 'No players found'}
        else:
            return {'error': 'Player not found'}

    def _mock_player_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player statistics response."""
        return {
            'player_id': args.get('player_id'),
            'statistics': {
                'goals': 85,
                'assists': 76,
                'matches_played': 245,
                'goals_per_game': 0.35,
                'assists_per_game': 0.31,
                'minutes_played': 19800,
                'performance_rating': 8.2
            }
        }

    def _mock_players_by_position(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock players by position response."""
        position = args.get('position')
        return {
            'players': [
                {'player_id': 'neymar_jr', 'name': 'Neymar Jr', 'position': position},
                {'player_id': 'vinicius_jr', 'name': 'Vinicius Jr', 'position': position}
            ],
            'total_count': 2
        }

    def _mock_player_career_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player career history response."""
        return {
            'player_id': args.get('player_id'),
            'career_history': [
                {
                    'team': 'Santos',
                    'period': '2009-2013',
                    'achievements': ['Copa Libertadores 2011'],
                    'contract_value': 1500000
                },
                {
                    'team': 'Barcelona',
                    'period': '2003-2008',
                    'achievements': ['Champions League 2006'],
                    'contract_value': 25000000
                }
            ]
        }

    def _mock_player_comparison(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player comparison response."""
        return {
            'comparison': {
                'player1': {
                    'id': args.get('player1_id'),
                    'goals_per_game': 0.35,
                    'assists_per_game': 0.31,
                    'strengths': ['Dribbling', 'Free kicks']
                },
                'player2': {
                    'id': args.get('player2_id'),
                    'goals_per_game': 0.42,
                    'assists_per_game': 0.28,
                    'strengths': ['Speed', 'Finishing']
                }
            }
        }

    def _mock_players_by_age_range(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock players by age range response."""
        return {
            'players': [
                {'player_id': 'vinicius_jr', 'name': 'Vinicius Jr', 'age': 23},
                {'player_id': 'endrick', 'name': 'Endrick', 'age': 17}
            ],
            'age_range': f"{args.get('min_age')}-{args.get('max_age')}"
        }

    def _mock_player_injury_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player injury history response."""
        return {
            'player_id': args.get('player_id'),
            'injury_history': [
                {
                    'injury_type': 'Ankle sprain',
                    'date': '2023-03-15',
                    'recovery_period': '6 weeks',
                    'impact': 'Missed 8 matches'
                }
            ]
        }

    def _mock_top_goal_scorers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock top goal scorers response."""
        return {
            'top_scorers': [
                {'player_id': 'neymar_jr', 'name': 'Neymar Jr', 'goals': 85, 'club_goals': 65, 'international_goals': 20},
                {'player_id': 'vinicius_jr', 'name': 'Vinicius Jr', 'goals': 78, 'club_goals': 73, 'international_goals': 5}
            ],
            'limit': args.get('limit', 10)
        }

    def _mock_player_social_media(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player social media response."""
        return {
            'player_id': args.get('player_id'),
            'social_media': {
                'instagram_followers': 175000000,
                'twitter_followers': 48000000,
                'engagement_rate': 8.5,
                'last_updated': datetime.now().isoformat()
            }
        }

    def _mock_team_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team search response."""
        name = args.get('name', '').lower()
        if 'flamengo' in name:
            return {
                'team_id': 'flamengo',
                'name': 'Flamengo',
                'league': 'Série A',
                'founded': 1895,
                'stadium': 'Maracanã',
                'capacity': 78838,
                'city': 'Rio de Janeiro',
                'history': {
                    'titles': ['Brasileirão 2019, 2020'],
                    'notable_players': ['Zico', 'Ronaldinho']
                },
                'current_squad': [
                    {'player_id': 'pedro_flamengo', 'name': 'Pedro', 'position': 'Forward'}
                ]
            }
        else:
            return {'teams': [], 'message': 'No teams found'}

    def _mock_team_roster(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team roster response."""
        return {
            'team_id': args.get('team_id'),
            'roster': [
                {
                    'player_id': 'pedro_flamengo',
                    'name': 'Pedro',
                    'position': 'Forward',
                    'jersey_number': 9,
                    'contract_until': '2025-12-31',
                    'market_value': 25000000
                }
            ],
            'positions': {
                'Goalkeeper': 3,
                'Defender': 8,
                'Midfielder': 6,
                'Forward': 4
            }
        }

    def _mock_team_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team statistics response."""
        return {
            'team_id': args.get('team_id'),
            'statistics': {
                'wins': 18,
                'draws': 8,
                'losses': 6,
                'goals_scored': 52,
                'goals_conceded': 28,
                'goal_difference': 24,
                'home_record': {'wins': 12, 'draws': 3, 'losses': 1},
                'away_record': {'wins': 6, 'draws': 5, 'losses': 5},
                'win_percentage': 56.25
            }
        }

    def _mock_teams_by_competition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock teams by competition response."""
        return {
            'competition': args.get('competition'),
            'teams': [
                {'team_id': 'flamengo', 'name': 'Flamengo', 'position': 1, 'points': 68},
                {'team_id': 'palmeiras', 'name': 'Palmeiras', 'position': 2, 'points': 65}
            ],
            'total_teams': 20
        }

    def _mock_team_comparison(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team comparison response."""
        return {
            'team1': {
                'id': args.get('team1_id'),
                'wins': 45,
                'draws': 23,
                'losses': 32,
                'win_percentage': 45.0,
                'recent_form': ['W', 'W', 'D', 'L', 'W']
            },
            'team2': {
                'id': args.get('team2_id'),
                'wins': 32,
                'draws': 23,
                'losses': 45,
                'win_percentage': 32.0,
                'recent_form': ['L', 'D', 'W', 'L', 'D']
            },
            'head_to_head': {
                'total_matches': 100,
                'team1_wins': 45,
                'team2_wins': 32,
                'draws': 23
            }
        }

    def _mock_team_transfers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team transfers response."""
        return {
            'team_id': args.get('team_id'),
            'transfer_history': {
                'incoming': [
                    {
                        'player': 'Pedro',
                        'from_team': 'Fiorentina',
                        'date': '2020-01-15',
                        'fee': 14000000,
                        'type': 'Permanent'
                    }
                ],
                'outgoing': [
                    {
                        'player': 'Lucas Paquetá',
                        'to_team': 'West Ham',
                        'date': '2022-08-30',
                        'fee': 51000000,
                        'type': 'Permanent'
                    }
                ]
            }
        }

    def _mock_team_finances(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team finances response."""
        return {
            'team_id': args.get('team_id'),
            'financial_data': {
                'revenue': 245000000,
                'expenses': 198000000,
                'profit': 47000000,
                'squad_value': 180000000,
                'debt': 23000000,
                'revenue_sources': {
                    'sponsorship': 95000000,
                    'broadcasting': 80000000,
                    'matchday': 35000000,
                    'transfers': 35000000
                }
            }
        }

    def _mock_team_achievements(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team achievements response."""
        return {
            'team_id': args.get('team_id'),
            'achievements': [
                {
                    'title': 'Copa Libertadores',
                    'year': 2019,
                    'type': 'International',
                    'importance': 'High'
                },
                {
                    'title': 'Campeonato Brasileiro',
                    'year': 2020,
                    'type': 'National',
                    'importance': 'High'
                }
            ],
            'total_titles': 65,
            'international_titles': 8,
            'national_titles': 57
        }

    def _mock_team_youth_academy(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team youth academy response."""
        return {
            'team_id': args.get('team_id'),
            'youth_academy': {
                'name': 'Ninho do Urubu',
                'established': 1998,
                'facilities': {
                    'training_pitches': 8,
                    'indoor_facilities': 2,
                    'accommodation': True,
                    'medical_center': True
                },
                'prospects': [
                    {
                        'player': 'Lorran',
                        'age': 17,
                        'position': 'Midfielder',
                        'potential_rating': 85
                    }
                ],
                'programs': ['U-15', 'U-17', 'U-20', 'Professional Development']
            }
        }

    def _mock_team_coaching_staff(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team coaching staff response."""
        return {
            'team_id': args.get('team_id'),
            'coaching_staff': {
                'head_coach': {
                    'name': 'Jorge Sampaoli',
                    'nationality': 'Argentina',
                    'appointment_date': '2023-05-15',
                    'contract_until': '2025-12-31',
                    'previous_clubs': ['Marseille', 'Atletico Mineiro']
                },
                'assistant_coaches': [
                    {'name': 'Claudio Ubeda', 'role': 'Assistant Coach'}
                ],
                'technical_staff': [
                    {'name': 'Dr. Márcio Tannure', 'role': 'Head of Medical'}
                ]
            }
        }

    def _mock_team_facilities(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team facilities response."""
        return {
            'team_id': args.get('team_id'),
            'facilities': {
                'stadium': {
                    'name': 'Arena do Grêmio',
                    'capacity': 55662,
                    'opened': 2012,
                    'location': 'Porto Alegre, RS',
                    'surface': 'Natural grass',
                    'roof': 'Retractable'
                },
                'training_center': {
                    'name': 'CT Luiz Carvalho',
                    'pitches': 6,
                    'indoor_facilities': True,
                    'gym': True,
                    'medical_center': True
                },
                'amenities': ['VIP boxes', 'Restaurants', 'Museum']
            }
        }

    def _mock_team_rivalries(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team rivalries response."""
        return {
            'team_id': args.get('team_id'),
            'rivalries': [
                {
                    'rival': 'Vasco da Gama',
                    'rivalry_name': 'Clássico dos Milhões',
                    'intensity': 'High',
                    'head_to_head': {'wins': 145, 'draws': 89, 'losses': 132},
                    'memorable_matches': [
                        {
                            'date': '2011-05-15',
                            'score': '5-4',
                            'competition': 'Brasileirão',
                            'significance': 'Historic comeback'
                        }
                    ]
                }
            ]
        }

    def _mock_team_social_media(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock team social media response."""
        return {
            'team_id': args.get('team_id'),
            'social_media': {
                'instagram_followers': 12500000,
                'twitter_followers': 8200000,
                'facebook_likes': 15800000,
                'youtube_subscribers': 2100000,
                'engagement_metrics': {
                    'average_likes_per_post': 85000,
                    'average_comments_per_post': 3200,
                    'growth_rate_monthly': 2.5
                },
                'fan_demographics': {
                    'brazil': 78,
                    'international': 22,
                    'age_18_35': 62
                }
            }
        }

    def _mock_match_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock match details response."""
        return {
            'match_id': args.get('match_id'),
            'home_team': 'Flamengo',
            'away_team': 'Palmeiras',
            'date': '2023-08-15',
            'final_score': '2-1',
            'competition': 'Brasileirão',
            'venue': 'Maracanã',
            'lineups': {
                'home': [
                    {'player': 'Santos', 'position': 'GK', 'jersey': 1},
                    {'player': 'Pedro', 'position': 'ST', 'jersey': 9}
                ],
                'away': [
                    {'player': 'Weverton', 'position': 'GK', 'jersey': 21}
                ]
            },
            'events': [
                {'minute': 15, 'type': 'GOAL', 'player': 'Pedro', 'team': 'Flamengo'},
                {'minute': 78, 'type': 'GOAL', 'player': 'Gabigol', 'team': 'Flamengo'}
            ]
        }

    def _mock_match_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock match statistics response."""
        return {
            'match_id': args.get('match_id'),
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

    def _mock_player_match_performance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock player match performance response."""
        return {
            'player_id': args.get('player_id'),
            'match_id': args.get('match_id'),
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

    def _mock_matches_by_date_range(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock matches by date range response."""
        return {
            'date_range': f"{args.get('start_date')} to {args.get('end_date')}",
            'matches': [
                {
                    'match_id': 'flamengo_vs_palmeiras_2023',
                    'date': '2023-08-15',
                    'home_team': 'Flamengo',
                    'away_team': 'Palmeiras',
                    'score': '2-1'
                }
            ],
            'total_matches': 1
        }

    def _mock_competition_standings(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock competition standings response."""
        return {
            'competition_id': args.get('competition_id'),
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

    def _mock_competition_top_scorers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock competition top scorers response."""
        return {
            'competition_id': args.get('competition_id'),
            'top_scorers': [
                {
                    'player_id': 'gabigol',
                    'name': 'Gabriel Barbosa',
                    'team': 'Flamengo',
                    'goals': 18,
                    'assists': 6,
                    'matches_played': 28
                }
            ]
        }

    def _mock_match_prediction(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock match prediction response."""
        return {
            'team1': args.get('team1_id'),
            'team2': args.get('team2_id'),
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
                }
            }
        }

    def _mock_historical_matches(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock historical matches response."""
        return {
            'team1': args.get('team1_id'),
            'team2': args.get('team2_id'),
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
                    'winner': args.get('team1_id'),
                    'venue': 'Maracanã',
                    'competition': 'Brasileirão'
                }
            ]
        }

    def _mock_competition_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock competition schedule response."""
        return {
            'competition_id': args.get('competition_id'),
            'fixtures': [
                {
                    'match_id': 'future_match_1',
                    'date': '2024-02-15',
                    'time': '20:00',
                    'home_team': 'Flamengo',
                    'away_team': 'Corinthians',
                    'venue': 'Maracanã',
                    'status': 'upcoming'
                }
            ],
            'upcoming_highlighted': True
        }

    def _mock_match_events(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock match events response."""
        return {
            'match_id': args.get('match_id'),
            'events': [
                {
                    'minute': 15,
                    'type': 'GOAL',
                    'player': 'Pedro',
                    'team': 'Flamengo',
                    'description': 'Header from cross'
                },
                {
                    'minute': 60,
                    'type': 'SUBSTITUTION',
                    'player_out': 'Rony',
                    'player_in': 'Endrick',
                    'team': 'Palmeiras'
                }
            ],
            'chronological_order': True
        }

    def _mock_referee_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock referee statistics response."""
        return {
            'referee_id': args.get('referee_id'),
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

    def _mock_venue_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock venue statistics response."""
        return {
            'venue_id': args.get('venue_id'),
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

    def _mock_competition_format(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock competition format response."""
        return {
            'competition_id': args.get('competition_id'),
            'format': {
                'type': 'Knockout',
                'rounds': [
                    {'name': 'First Round', 'teams': 80, 'matches': 40},
                    {'name': 'Final', 'teams': 2, 'matches': 1}
                ],
                'qualification_rules': [
                    'Single elimination',
                    'Extra time and penalties if tied'
                ],
                'prize_money': {
                    'winner': 54000000,
                    'runner_up': 20000000
                }
            }
        }

    def _mock_live_match_updates(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock live match updates response."""
        return {
            'match_id': args.get('match_id'),
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


class MockNeo4jDriver:
    """Mock Neo4j driver for testing."""

    def __init__(self, test_config: Dict[str, Any]):
        self.config = test_config
        self.closed = False

    def session(self):
        """Return mock session."""
        return MockNeo4jSession()

    def close(self):
        """Close mock driver."""
        self.closed = True

    def verify_connectivity(self):
        """Verify mock connectivity."""
        return {'address': self.config['neo4j']['uri']}


class MockNeo4jSession:
    """Mock Neo4j session for testing."""

    def __init__(self):
        self.closed = False

    def run(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """Mock query execution."""
        return MockNeo4jResult()

    def close(self):
        """Close mock session."""
        self.closed = True

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class MockNeo4jResult:
    """Mock Neo4j result for testing."""

    def __init__(self):
        self.records = []

    def single(self):
        """Return single record."""
        return {'count': 1} if self.records else None

    def data(self):
        """Return data list."""
        return self.records


# Pytest fixtures
@pytest.fixture(scope='session')
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG


@pytest.fixture(scope='session')
def neo4j_driver(test_config):
    """Provide mock Neo4j driver for testing."""
    driver = MockNeo4jDriver(test_config)
    yield driver
    driver.close()


@pytest.fixture(scope='session')
def mcp_client(test_config):
    """Provide mock MCP client for testing."""
    client = MockMCPClient(test_config)
    client.connect()
    yield client
    client.disconnect()


@pytest.fixture
def test_player_data():
    """Provide test player data."""
    return TEST_CONFIG['test_data']['players']


@pytest.fixture
def test_team_data():
    """Provide test team data."""
    return TEST_CONFIG['test_data']['teams']


@pytest.fixture
def test_match_data():
    """Provide test match data."""
    return TEST_CONFIG['test_data']['matches']


@pytest.fixture(autouse=True)
def setup_test_environment(neo4j_driver, mcp_client):
    """Set up test environment before each test."""
    # Reset mock client state
    mcp_client.call_count = 0
    mcp_client.last_call = None

    # Ensure database is in clean state
    with neo4j_driver.session() as session:
        # Clear any existing test data
        session.run("MATCH (n) DETACH DELETE n")

    yield

    # Cleanup after test
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


@pytest.fixture
def temp_directory():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing."""
    return {
        'players': [
            {
                'player_id': 'test_player_1',
                'name': 'Test Player 1',
                'position': 'Forward',
                'nationality': 'Brazil'
            }
        ],
        'teams': [
            {
                'team_id': 'test_team_1',
                'name': 'Test Team 1',
                'league': 'Test League'
            }
        ]
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add integration marker to BDD tests
        if 'features' in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that might be slow
        if 'test_match_steps' in str(item.fspath):
            item.add_marker(pytest.mark.slow)


# Test utilities
def assert_valid_response(response: Dict[str, Any], required_fields: list):
    """Assert response contains required fields."""
    assert isinstance(response, dict), "Response must be a dictionary"
    for field in required_fields:
        assert field in response, f"Response missing required field: {field}"


def assert_valid_player_data(player_data: Dict[str, Any]):
    """Assert player data is valid."""
    required_fields = ['player_id', 'name', 'position', 'nationality']
    assert_valid_response(player_data, required_fields)


def assert_valid_team_data(team_data: Dict[str, Any]):
    """Assert team data is valid."""
    required_fields = ['team_id', 'name', 'league']
    assert_valid_response(team_data, required_fields)


def assert_valid_match_data(match_data: Dict[str, Any]):
    """Assert match data is valid."""
    required_fields = ['match_id', 'home_team', 'away_team', 'date']
    assert_valid_response(match_data, required_fields)


# Mock data generators
def generate_mock_player(player_id: str = None) -> Dict[str, Any]:
    """Generate mock player data."""
    if player_id is None:
        player_id = f"test_player_{datetime.now().timestamp()}"

    return {
        'player_id': player_id,
        'name': f'Test Player {player_id}',
        'position': 'Forward',
        'nationality': 'Brazil',
        'birth_date': '1995-01-01',
        'current_team': 'Test Team',
        'market_value': 10000000
    }


def generate_mock_team(team_id: str = None) -> Dict[str, Any]:
    """Generate mock team data."""
    if team_id is None:
        team_id = f"test_team_{datetime.now().timestamp()}"

    return {
        'team_id': team_id,
        'name': f'Test Team {team_id}',
        'league': 'Test League',
        'founded': 2000,
        'stadium': 'Test Stadium',
        'capacity': 50000,
        'city': 'Test City'
    }


def generate_mock_match(match_id: str = None) -> Dict[str, Any]:
    """Generate mock match data."""
    if match_id is None:
        match_id = f"test_match_{datetime.now().timestamp()}"

    return {
        'match_id': match_id,
        'home_team': 'Test Home Team',
        'away_team': 'Test Away Team',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'final_score': '2-1',
        'competition': 'Test Competition',
        'venue': 'Test Venue'
    }


# Environment validation
def validate_test_environment():
    """Validate test environment is properly configured."""
    required_env_vars = []
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        pytest.skip(f"Missing required environment variables: {missing_vars}")

    # Check if Neo4j is available (for integration tests)
    try:
        driver = GraphDatabase.driver(
            TEST_CONFIG['neo4j']['uri'],
            auth=(TEST_CONFIG['neo4j']['username'], TEST_CONFIG['neo4j']['password'])
        )
        driver.verify_connectivity()
        driver.close()
    except Exception as e:
        pytest.skip(f"Neo4j not available for integration tests: {e}")


# Pytest hooks
def pytest_runtest_setup(item):
    """Set up individual test runs."""
    # Skip integration tests if environment not ready
    if item.get_closest_marker("integration"):
        validate_test_environment()


def pytest_runtest_teardown(item, nextitem):
    """Clean up after individual test runs."""
    # Reset any global state if needed
    pass