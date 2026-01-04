"""
Brazilian Soccer MCP Knowledge Graph - Test Data Loader

CONTEXT:
This module provides utilities for loading minimal test data into Neo4j
for integration tests. Uses testcontainers for isolated test environments.

PHASE: 3 - Integration & Testing
PURPOSE: Load test fixtures into Neo4j testcontainer
DATA SOURCES: Static test data for Brazilian soccer domain
DEPENDENCIES: neo4j
"""

from typing import Dict, Any, List
from neo4j import Driver


class DataLoader:
    """
    Loads minimal test data into Neo4j for integration tests.

    Provides sufficient data to test all MCP tools without requiring
    external data sources or the full Kaggle dataset.
    """

    def __init__(self, driver: Driver):
        """
        Initialize the test data loader.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def load_all(self) -> Dict[str, int]:
        """
        Load all test data into the database.

        Returns:
            Dictionary with counts of created nodes by type
        """
        counts = {}
        counts['players'] = self._load_players()
        counts['teams'] = self._load_teams()
        counts['matches'] = self._load_matches()
        counts['competitions'] = self._load_competitions()
        counts['coaches'] = self._load_coaches()
        counts['transfers'] = self._load_transfers()
        counts['relationships'] = self._load_relationships()
        return counts

    def _load_players(self) -> int:
        """Load test player data."""
        players = [
            {
                'id': 'player_neymar',
                'name': 'Neymar Jr',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '1992-02-05',
                'market_value': 90000000,
                'goals': 85,
                'assists': 76,
                'matches_played': 245
            },
            {
                'id': 'player_vinicius',
                'name': 'Vinicius Jr',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '2000-07-12',
                'market_value': 100000000,
                'goals': 78,
                'assists': 42,
                'matches_played': 198
            },
            {
                'id': 'player_ronaldinho',
                'name': 'Ronaldinho',
                'position': 'Attacking Midfielder',
                'nationality': 'Brazil',
                'birth_date': '1980-03-21',
                'market_value': 0,
                'goals': 180,
                'assists': 145,
                'matches_played': 585
            },
            {
                'id': 'player_pele',
                'name': 'Pele',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '1940-10-23',
                'market_value': 0,
                'goals': 1281,
                'assists': 380,
                'matches_played': 1363
            },
            {
                'id': 'player_gabigol',
                'name': 'Gabriel Barbosa',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '1996-08-30',
                'market_value': 25000000,
                'goals': 150,
                'assists': 45,
                'matches_played': 320
            },
            {
                'id': 'player_casemiro',
                'name': 'Casemiro',
                'position': 'Defensive Midfielder',
                'nationality': 'Brazil',
                'birth_date': '1992-02-23',
                'market_value': 30000000,
                'goals': 35,
                'assists': 28,
                'matches_played': 420
            },
            {
                'id': 'player_alisson',
                'name': 'Alisson Becker',
                'position': 'Goalkeeper',
                'nationality': 'Brazil',
                'birth_date': '1992-10-02',
                'market_value': 40000000,
                'goals': 0,
                'assists': 2,
                'matches_played': 380
            },
            {
                'id': 'player_endrick',
                'name': 'Endrick',
                'position': 'Forward',
                'nationality': 'Brazil',
                'birth_date': '2006-07-21',
                'market_value': 60000000,
                'goals': 20,
                'assists': 8,
                'matches_played': 45
            }
        ]

        with self.driver.session() as session:
            for player in players:
                session.run("""
                    CREATE (p:Player {
                        id: $id,
                        name: $name,
                        position: $position,
                        nationality: $nationality,
                        birth_date: $birth_date,
                        market_value: $market_value,
                        goals: $goals,
                        assists: $assists,
                        matches_played: $matches_played
                    })
                """, player)

        return len(players)

    def _load_teams(self) -> int:
        """Load test team data."""
        teams = [
            {
                'id': 'team_flamengo',
                'name': 'Flamengo',
                'league': 'Serie A',
                'founded': 1895,
                'stadium': 'Maracana',
                'capacity': 78838,
                'city': 'Rio de Janeiro',
                'state': 'RJ'
            },
            {
                'id': 'team_palmeiras',
                'name': 'Palmeiras',
                'league': 'Serie A',
                'founded': 1914,
                'stadium': 'Allianz Parque',
                'capacity': 43713,
                'city': 'Sao Paulo',
                'state': 'SP'
            },
            {
                'id': 'team_corinthians',
                'name': 'Corinthians',
                'league': 'Serie A',
                'founded': 1910,
                'stadium': 'Neo Quimica Arena',
                'capacity': 49205,
                'city': 'Sao Paulo',
                'state': 'SP'
            },
            {
                'id': 'team_santos',
                'name': 'Santos',
                'league': 'Serie A',
                'founded': 1912,
                'stadium': 'Vila Belmiro',
                'capacity': 16068,
                'city': 'Santos',
                'state': 'SP'
            },
            {
                'id': 'team_sao_paulo',
                'name': 'Sao Paulo',
                'league': 'Serie A',
                'founded': 1930,
                'stadium': 'Morumbi',
                'capacity': 66795,
                'city': 'Sao Paulo',
                'state': 'SP'
            },
            {
                'id': 'team_gremio',
                'name': 'Gremio',
                'league': 'Serie A',
                'founded': 1903,
                'stadium': 'Arena do Gremio',
                'capacity': 55662,
                'city': 'Porto Alegre',
                'state': 'RS'
            }
        ]

        with self.driver.session() as session:
            for team in teams:
                session.run("""
                    CREATE (t:Team {
                        id: $id,
                        name: $name,
                        league: $league,
                        founded: $founded,
                        stadium: $stadium,
                        capacity: $capacity,
                        city: $city,
                        state: $state
                    })
                """, team)

        return len(teams)

    def _load_matches(self) -> int:
        """Load test match data."""
        matches = [
            {
                'id': 'match_fla_pal_2023',
                'home_team': 'Flamengo',
                'away_team': 'Palmeiras',
                'date': '2023-08-15',
                'home_score': 2,
                'away_score': 1,
                'competition': 'Brasileirao',
                'venue': 'Maracana',
                'attendance': 65000
            },
            {
                'id': 'match_pal_cor_2023',
                'home_team': 'Palmeiras',
                'away_team': 'Corinthians',
                'date': '2023-09-10',
                'home_score': 1,
                'away_score': 1,
                'competition': 'Brasileirao',
                'venue': 'Allianz Parque',
                'attendance': 40000
            },
            {
                'id': 'match_san_fla_2023',
                'home_team': 'Santos',
                'away_team': 'Flamengo',
                'date': '2023-10-05',
                'home_score': 0,
                'away_score': 3,
                'competition': 'Brasileirao',
                'venue': 'Vila Belmiro',
                'attendance': 15000
            },
            {
                'id': 'match_gre_sao_2023',
                'home_team': 'Gremio',
                'away_team': 'Sao Paulo',
                'date': '2023-11-20',
                'home_score': 2,
                'away_score': 2,
                'competition': 'Brasileirao',
                'venue': 'Arena do Gremio',
                'attendance': 45000
            },
            {
                'id': 'match_fla_cor_2023',
                'home_team': 'Flamengo',
                'away_team': 'Corinthians',
                'date': '2023-12-03',
                'home_score': 4,
                'away_score': 0,
                'competition': 'Copa do Brasil',
                'venue': 'Maracana',
                'attendance': 70000
            }
        ]

        with self.driver.session() as session:
            for match in matches:
                session.run("""
                    CREATE (m:Match {
                        id: $id,
                        home_team: $home_team,
                        away_team: $away_team,
                        date: $date,
                        home_score: $home_score,
                        away_score: $away_score,
                        competition: $competition,
                        venue: $venue,
                        attendance: $attendance
                    })
                """, match)

        return len(matches)

    def _load_competitions(self) -> int:
        """Load test competition data."""
        competitions = [
            {
                'id': 'comp_brasileirao',
                'name': 'Brasileirao Serie A',
                'country': 'Brazil',
                'type': 'League',
                'teams_count': 20,
                'season': '2023'
            },
            {
                'id': 'comp_copa_brasil',
                'name': 'Copa do Brasil',
                'country': 'Brazil',
                'type': 'Cup',
                'teams_count': 92,
                'season': '2023'
            },
            {
                'id': 'comp_libertadores',
                'name': 'Copa Libertadores',
                'country': 'South America',
                'type': 'Continental',
                'teams_count': 47,
                'season': '2023'
            }
        ]

        with self.driver.session() as session:
            for comp in competitions:
                session.run("""
                    CREATE (c:Competition {
                        id: $id,
                        name: $name,
                        country: $country,
                        type: $type,
                        teams_count: $teams_count,
                        season: $season
                    })
                """, comp)

        return len(competitions)

    def _load_coaches(self) -> int:
        """Load test coach data with MANAGES relationships."""
        coaches = [
            {
                'id': 'coach_jorge_jesus',
                'name': 'Jorge Jesus',
                'nationality': 'Portugal',
                'team_id': 'team_flamengo',
                'team_name': 'Flamengo'
            },
            {
                'id': 'coach_abel_ferreira',
                'name': 'Abel Ferreira',
                'nationality': 'Portugal',
                'team_id': 'team_palmeiras',
                'team_name': 'Palmeiras'
            },
            {
                'id': 'coach_vagner_mancini',
                'name': 'Vagner Mancini',
                'nationality': 'Brazil',
                'team_id': 'team_corinthians',
                'team_name': 'Corinthians'
            },
            {
                'id': 'coach_fernando_diniz',
                'name': 'Fernando Diniz',
                'nationality': 'Brazil',
                'team_id': 'team_sao_paulo',
                'team_name': 'Sao Paulo'
            },
            {
                'id': 'coach_renato_gaucho',
                'name': 'Renato Gaucho',
                'nationality': 'Brazil',
                'team_id': 'team_gremio',
                'team_name': 'Gremio'
            }
        ]

        with self.driver.session() as session:
            for coach in coaches:
                session.run("""
                    CREATE (c:Coach {
                        id: $id,
                        name: $name,
                        nationality: $nationality
                    })
                """, coach)

        return len(coaches)

    def _load_transfers(self) -> int:
        """Load test transfer data."""
        transfers = [
            {
                'id': 'transfer_neymar_1',
                'player_id': 'player_neymar',
                'player_name': 'Neymar Jr',
                'from_team_id': 'team_santos',
                'from_team_name': 'Santos',
                'to_team_id': 'team_barcelona',
                'to_team_name': 'Barcelona',
                'transfer_year': 2013,
                'transfer_type': 'PERMANENT'
            },
            {
                'id': 'transfer_neymar_2',
                'player_id': 'player_neymar',
                'player_name': 'Neymar Jr',
                'from_team_id': 'team_barcelona',
                'from_team_name': 'Barcelona',
                'to_team_id': 'team_psg',
                'to_team_name': 'PSG',
                'transfer_year': 2017,
                'transfer_type': 'PERMANENT'
            },
            {
                'id': 'transfer_gabigol_1',
                'player_id': 'player_gabigol',
                'player_name': 'Gabriel Barbosa',
                'from_team_id': 'team_santos',
                'from_team_name': 'Santos',
                'to_team_id': 'team_inter',
                'to_team_name': 'Inter Milan',
                'transfer_year': 2016,
                'transfer_type': 'PERMANENT'
            },
            {
                'id': 'transfer_gabigol_2',
                'player_id': 'player_gabigol',
                'player_name': 'Gabriel Barbosa',
                'from_team_id': 'team_inter',
                'from_team_name': 'Inter Milan',
                'to_team_id': 'team_flamengo',
                'to_team_name': 'Flamengo',
                'transfer_year': 2020,
                'transfer_type': 'PERMANENT'
            },
            {
                'id': 'transfer_endrick_1',
                'player_id': 'player_endrick',
                'player_name': 'Endrick',
                'from_team_id': 'team_palmeiras',
                'from_team_name': 'Palmeiras',
                'to_team_id': 'team_real_madrid',
                'to_team_name': 'Real Madrid',
                'transfer_year': 2024,
                'transfer_type': 'PERMANENT'
            },
            {
                'id': 'transfer_vinicius_1',
                'player_id': 'player_vinicius',
                'player_name': 'Vinicius Jr',
                'from_team_id': 'team_flamengo',
                'from_team_name': 'Flamengo',
                'to_team_id': 'team_real_madrid',
                'to_team_name': 'Real Madrid',
                'transfer_year': 2018,
                'transfer_type': 'PERMANENT'
            }
        ]

        with self.driver.session() as session:
            for transfer in transfers:
                session.run("""
                    CREATE (tr:Transfer {
                        id: $id,
                        player_id: $player_id,
                        player_name: $player_name,
                        from_team_name: $from_team_name,
                        to_team_name: $to_team_name,
                        transfer_year: $transfer_year,
                        transfer_type: $transfer_type
                    })
                """, transfer)

        return len(transfers)

    def _load_relationships(self) -> int:
        """Load relationships between nodes."""
        count = 0

        with self.driver.session() as session:
            # Player-Team relationships (PLAYS_FOR)
            player_team_rels = [
                ('player_neymar', 'team_santos'),
                ('player_gabigol', 'team_flamengo'),
                ('player_endrick', 'team_palmeiras'),
                ('player_pele', 'team_santos'),
                ('player_ronaldinho', 'team_flamengo'),
            ]

            for player_id, team_id in player_team_rels:
                session.run("""
                    MATCH (p:Player {id: $player_id})
                    MATCH (t:Team {id: $team_id})
                    CREATE (p)-[:PLAYS_FOR]->(t)
                """, {'player_id': player_id, 'team_id': team_id})
                count += 1

            # Team-Match relationships (HOME_TEAM, AWAY_TEAM)
            session.run("""
                MATCH (t:Team), (m:Match)
                WHERE m.home_team = t.name
                CREATE (t)-[:HOME_TEAM]->(m)
            """)

            session.run("""
                MATCH (t:Team), (m:Match)
                WHERE m.away_team = t.name
                CREATE (t)-[:AWAY_TEAM]->(m)
            """)

            # Coach-Team relationships (MANAGES)
            coach_team_rels = [
                ('coach_jorge_jesus', 'team_flamengo'),
                ('coach_abel_ferreira', 'team_palmeiras'),
                ('coach_vagner_mancini', 'team_corinthians'),
                ('coach_fernando_diniz', 'team_sao_paulo'),
                ('coach_renato_gaucho', 'team_gremio'),
            ]

            for coach_id, team_id in coach_team_rels:
                session.run("""
                    MATCH (c:Coach {id: $coach_id})
                    MATCH (t:Team {id: $team_id})
                    CREATE (c)-[:MANAGES {active: true}]->(t)
                """, {'coach_id': coach_id, 'team_id': team_id})
                count += 1

            # Transfer relationships (TRANSFERRED_FROM, TRANSFERRED_TO)
            # For each transfer, create relationships from player to source and destination teams
            transfer_rels = [
                ('player_neymar', 'team_santos', 'transfer_neymar_1', 2013),
                ('player_gabigol', 'team_santos', 'transfer_gabigol_1', 2016),
                ('player_gabigol', 'team_flamengo', 'transfer_gabigol_2', 2020),
                ('player_endrick', 'team_palmeiras', 'transfer_endrick_1', 2024),
                ('player_vinicius', 'team_flamengo', 'transfer_vinicius_1', 2018),
            ]

            for player_id, from_team_id, transfer_id, year in transfer_rels:
                # Create TRANSFERRED_FROM relationship
                session.run("""
                    MATCH (p:Player {id: $player_id})
                    MATCH (t:Team {id: $from_team_id})
                    CREATE (p)-[:TRANSFERRED_FROM {transfer_id: $transfer_id, year: $year}]->(t)
                """, {'player_id': player_id, 'from_team_id': from_team_id,
                      'transfer_id': transfer_id, 'year': year})
                count += 1

            # Create some TRANSFERRED_TO relationships for players going to known teams
            to_transfer_rels = [
                ('player_gabigol', 'team_flamengo', 'transfer_gabigol_2', 2020),
            ]

            for player_id, to_team_id, transfer_id, year in to_transfer_rels:
                session.run("""
                    MATCH (p:Player {id: $player_id})
                    MATCH (t:Team {id: $to_team_id})
                    CREATE (p)-[:TRANSFERRED_TO {transfer_id: $transfer_id, year: $year}]->(t)
                """, {'player_id': player_id, 'to_team_id': to_team_id,
                      'transfer_id': transfer_id, 'year': year})
                count += 1

            # Count all relationships created
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            count = result.single()["count"]

        return count

    def clear_all(self) -> None:
        """Clear all data from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with self.driver.session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")

            return {
                'nodes': node_result.single()["count"],
                'relationships': rel_result.single()["count"]
            }


def load_test_data(driver: Driver) -> Dict[str, int]:
    """
    Convenience function to load all test data.

    Args:
        driver: Neo4j driver instance

    Returns:
        Dictionary with counts of created entities
    """
    loader = DataLoader(driver)
    return loader.load_all()


# Alias for backwards compatibility
TestDataLoader = DataLoader
