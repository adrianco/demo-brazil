"""
Brazilian Soccer MCP Knowledge Graph - Kaggle Data Loader

CONTEXT:
This module implements CSV data loading and parsing for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for loading Brazilian football match data from Kaggle datasets,
handling Portuguese text normalization, and extracting entities for graph population.

PHASE: 1 - Core Data
PURPOSE: Load and parse Brazilian soccer data from CSV files
DATA SOURCES: Kaggle Brazilian Football Matches
DEPENDENCIES: pandas, unicodedata, datetime

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition nodes with relationships
- Performance: Batch processing for large datasets
- Testing: BDD scenarios with sample Brazilian teams and players

INTEGRATION:
- MCP Tools: Feeds clean data to graph_builder module
- Error Handling: Validation and data cleaning with fallbacks
- Rate Limiting: N/A for offline data processing
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import re
import unicodedata

# Import local utilities if available, otherwise use standard libraries
try:
    from ..utils.data_utils import normalize_text, parse_date, safe_float, safe_int
except ImportError:
    # Fallback for standalone testing
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from utils.data_utils import normalize_text, parse_date, safe_float, safe_int


class KaggleLoader:
    """Kaggle data loader for Brazilian soccer datasets."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the Kaggle data loader.

        Args:
            data_dir: Directory to store downloaded data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Sample data for development/testing
        self._create_sample_data()

        # Store the common Brazilian data
        self.setup_brazilian_data()

    def _create_sample_data(self) -> None:
        """Create sample data files for development and testing."""
        sample_data_dir = self.data_dir / "sample"
        sample_data_dir.mkdir(exist_ok=True)

        # Sample teams data
        teams_data = [
            {
                "team_id": "FLA", "name": "Flamengo", "full_name": "Clube de Regatas do Flamengo",
                "city": "Rio de Janeiro", "state": "RJ", "founded": 1895,
                "stadium": "Maracanã", "capacity": 78838
            },
            {
                "team_id": "PAL", "name": "Palmeiras", "full_name": "Sociedade Esportiva Palmeiras",
                "city": "São Paulo", "state": "SP", "founded": 1914,
                "stadium": "Allianz Parque", "capacity": 43713
            },
            {
                "team_id": "COR", "name": "Corinthians", "full_name": "Sport Club Corinthians Paulista",
                "city": "São Paulo", "state": "SP", "founded": 1910,
                "stadium": "Neo Química Arena", "capacity": 49205
            },
            {
                "team_id": "SAO", "name": "São Paulo", "full_name": "São Paulo Futebol Clube",
                "city": "São Paulo", "state": "SP", "founded": 1930,
                "stadium": "Morumbi", "capacity": 67428
            },
            {
                "team_id": "GRE", "name": "Grêmio", "full_name": "Grêmio Foot-Ball Porto Alegrense",
                "city": "Porto Alegre", "state": "RS", "founded": 1903,
                "stadium": "Arena do Grêmio", "capacity": 55662
            }
        ]

        # Sample players data
        players_data = [
            {
                "player_id": "FLA_001", "name": "Gabriel Barbosa", "team_id": "FLA",
                "position": "FWD", "age": 27, "height": 175, "nationality": "Brazil",
                "goals": 15, "assists": 8, "matches": 28
            },
            {
                "player_id": "PAL_001", "name": "Rony", "team_id": "PAL",
                "position": "FWD", "age": 28, "height": 174, "nationality": "Brazil",
                "goals": 12, "assists": 5, "matches": 32
            },
            {
                "player_id": "COR_001", "name": "Yuri Alberto", "team_id": "COR",
                "position": "FWD", "age": 23, "height": 180, "nationality": "Brazil",
                "goals": 18, "assists": 4, "matches": 35
            },
            {
                "player_id": "SAO_001", "name": "Calleri", "team_id": "SAO",
                "position": "FWD", "age": 30, "height": 185, "nationality": "Argentina",
                "goals": 14, "assists": 6, "matches": 30
            },
            {
                "player_id": "GRE_001", "name": "Suárez", "team_id": "GRE",
                "position": "FWD", "age": 36, "height": 182, "nationality": "Uruguay",
                "goals": 20, "assists": 9, "matches": 26
            }
        ]

        # Sample matches data
        matches_data = [
            {
                "match_id": "BRA2023_001", "date": "2023-04-15", "home_team": "FLA",
                "away_team": "PAL", "home_score": 2, "away_score": 1,
                "competition": "Brasileirão Serie A", "round": 1
            },
            {
                "match_id": "BRA2023_002", "date": "2023-04-16", "home_team": "COR",
                "away_team": "SAO", "home_score": 1, "away_score": 1,
                "competition": "Brasileirão Serie A", "round": 1
            },
            {
                "match_id": "BRA2023_003", "date": "2023-04-22", "home_team": "GRE",
                "away_team": "FLA", "home_score": 3, "away_score": 0,
                "competition": "Brasileirão Serie A", "round": 2
            },
            {
                "match_id": "BRA2023_004", "date": "2023-04-23", "home_team": "PAL",
                "away_team": "COR", "home_score": 2, "away_score": 2,
                "competition": "Brasileirão Serie A", "round": 2
            }
        ]

        # Save sample data to CSV files
        pd.DataFrame(teams_data).to_csv(sample_data_dir / "teams.csv", index=False)
        pd.DataFrame(players_data).to_csv(sample_data_dir / "players.csv", index=False)
        pd.DataFrame(matches_data).to_csv(sample_data_dir / "matches.csv", index=False)

        self.logger.info(f"Sample data created in {sample_data_dir}")

    def setup_brazilian_data(self):
        """Setup Brazilian soccer data constants."""
        # Brazilian teams mapping
        self.brazilian_teams = {
            'flamengo': 'Clube de Regatas do Flamengo',
            'palmeiras': 'Sociedade Esportiva Palmeiras',
            'corinthians': 'Sport Club Corinthians Paulista',
            'sao_paulo': 'São Paulo Futebol Clube',
            'santos': 'Santos Futebol Clube',
            'gremio': 'Grêmio Foot-Ball Porto Alegrense',
            'internacional': 'Sport Club Internacional',
            'atletico_mg': 'Clube Atlético Mineiro',
            'cruzeiro': 'Cruzeiro Esporte Clube',
            'botafogo': 'Botafogo de Futebol e Regatas',
            'vasco': 'Club de Regatas Vasco da Gama',
            'fluminense': 'Fluminense Football Club'
        }

        # Famous Brazilian players
        self.famous_players = [
            'Pelé', 'Ronaldinho', 'Kaká', 'Ronaldo', 'Rivaldo',
            'Romário', 'Zico', 'Garrincha', 'Jairzinho', 'Tostão',
            'Cafu', 'Roberto Carlos', 'Dida', 'Marcos', 'Gilberto Silva',
            'Dunga', 'Bebeto', 'Careca', 'Falcão', 'Sócrates',
            'Gabriel Barbosa', 'Casemiro', 'Philippe Coutinho', 'Neymar Jr',
            'Alisson Becker', 'Thiago Silva', 'Marquinhos', 'Fabinho'
        ]

        # Brazilian competitions
        self.competitions = {
            'serie_a': 'Campeonato Brasileiro Série A',
            'copa_brasil': 'Copa do Brasil',
            'libertadores': 'Copa Libertadores',
            'sul_americana': 'Copa Sul-Americana',
            'estadual_carioca': 'Campeonato Carioca',
            'estadual_paulista': 'Campeonato Paulista',
            'estadual_gaucho': 'Campeonato Gaúcho',
            'estadual_mineiro': 'Campeonato Mineiro'
        }

    def generate_sample_data(self, num_matches: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample Brazilian soccer data for testing."""
        from datetime import datetime, timedelta
        import random

        self.logger.info(f"Generating {num_matches} sample matches")

        entities = {
            'teams': [],
            'players': [],
            'matches': [],
            'competitions': [],
            'venues': []
        }

        # Create teams
        teams_list = list(self.brazilian_teams.values())
        for i, team_name in enumerate(teams_list):
            entities['teams'].append({
                'id': f"team_{i}",
                'name': team_name,
                'country': 'Brazil',
                'founded': self._get_team_founded_year(team_name),
                'stadium': self._get_team_stadium(team_name)
            })

        # Create competitions
        for i, (key, comp_name) in enumerate(self.competitions.items()):
            entities['competitions'].append({
                'id': f"comp_{i}",
                'name': comp_name,
                'country': 'Brazil',
                'level': self._get_competition_level(comp_name)
            })

        # Create venues
        venues = [
            'Maracanã', 'Allianz Parque', 'Arena Corinthians',
            'Morumbi', 'Vila Belmiro', 'Arena do Grêmio',
            'Beira-Rio', 'Mineirão', 'Arena Fonte Nova'
        ]

        for i, venue_name in enumerate(venues):
            entities['venues'].append({
                'id': f"venue_{i}",
                'name': venue_name,
                'city': self._get_venue_city(venue_name),
                'capacity': self._get_venue_capacity(venue_name)
            })

        # Create players
        for i, player_name in enumerate(self.famous_players):
            entities['players'].append({
                'id': f"player_{i}",
                'name': player_name,
                'position': random.choice(['Forward', 'Midfielder', 'Defender', 'Goalkeeper']),
                'nationality': 'Brazilian',
                'birth_date': self._generate_birth_date().isoformat()
            })

        # Generate matches
        start_date = datetime(2023, 1, 1)

        for i in range(num_matches):
            home_team = random.choice(teams_list)
            away_team = random.choice([t for t in teams_list if t != home_team])

            match_date = start_date + timedelta(days=random.randint(0, 365))
            competition = random.choice(list(self.competitions.values()))
            venue = random.choice(venues)

            # Generate realistic scores
            home_score = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 25, 30, 20, 10, 5])[0]
            away_score = random.choices([0, 1, 2, 3, 4], weights=[15, 30, 25, 20, 10])[0]

            entities['matches'].append({
                'id': f"match_{i}",
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'date': match_date.isoformat(),
                'competition': competition,
                'venue': venue,
                'attendance': random.randint(10000, 80000)
            })

        return entities

    def _get_team_founded_year(self, team_name: str) -> int:
        """Get founding year for Brazilian teams."""
        founding_years = {
            'Clube de Regatas do Flamengo': 1895,
            'Sociedade Esportiva Palmeiras': 1914,
            'Sport Club Corinthians Paulista': 1910,
            'São Paulo Futebol Clube': 1930,
            'Santos Futebol Clube': 1912,
            'Grêmio Foot-Ball Porto Alegrense': 1903,
            'Sport Club Internacional': 1909,
            'Clube Atlético Mineiro': 1908,
            'Cruzeiro Esporte Clube': 1921,
            'Botafogo de Futebol e Regatas': 1904
        }
        return founding_years.get(team_name, 1900)

    def _get_team_stadium(self, team_name: str) -> str:
        """Get stadium for Brazilian teams."""
        stadiums = {
            'Clube de Regatas do Flamengo': 'Maracanã',
            'Sociedade Esportiva Palmeiras': 'Allianz Parque',
            'Sport Club Corinthians Paulista': 'Arena Corinthians',
            'São Paulo Futebol Clube': 'Morumbi',
            'Santos Futebol Clube': 'Vila Belmiro',
            'Grêmio Foot-Ball Porto Alegrense': 'Arena do Grêmio',
            'Sport Club Internacional': 'Beira-Rio',
            'Clube Atlético Mineiro': 'Mineirão',
            'Botafogo de Futebol e Regatas': 'Nilton Santos'
        }
        return stadiums.get(team_name, 'Stadium')

    def _get_competition_level(self, competition: str) -> int:
        """Get competition level (1 = highest)."""
        levels = {
            'Campeonato Brasileiro Série A': 1,
            'Copa Libertadores': 1,
            'Copa do Brasil': 2,
            'Copa Sul-Americana': 2,
            'Campeonato Carioca': 3,
            'Campeonato Paulista': 3
        }
        return levels.get(competition, 3)

    def _get_venue_city(self, venue: str) -> str:
        """Get city for venue."""
        cities = {
            'Maracanã': 'Rio de Janeiro',
            'Allianz Parque': 'São Paulo',
            'Arena Corinthians': 'São Paulo',
            'Morumbi': 'São Paulo',
            'Vila Belmiro': 'Santos',
            'Arena do Grêmio': 'Porto Alegre',
            'Beira-Rio': 'Porto Alegre',
            'Mineirão': 'Belo Horizonte',
            'Arena Fonte Nova': 'Salvador'
        }
        return cities.get(venue, 'São Paulo')

    def _get_venue_capacity(self, venue: str) -> int:
        """Get capacity for venue."""
        capacities = {
            'Maracanã': 78838,
            'Allianz Parque': 43713,
            'Arena Corinthians': 49205,
            'Morumbi': 67052,
            'Vila Belmiro': 16068,
            'Arena do Grêmio': 55662,
            'Beira-Rio': 50128,
            'Mineirão': 61846,
            'Arena Fonte Nova': 47907
        }
        return capacities.get(venue, 40000)

    def _generate_birth_date(self) -> datetime:
        """Generate realistic birth date for players."""
        import random
        from datetime import datetime, timedelta
        # Ages between 18-40
        years_ago = random.randint(18, 40)
        base_date = datetime.now() - timedelta(days=years_ago * 365)
        random_days = random.randint(0, 365)
        return base_date + timedelta(days=random_days)

    def load_csv_data(self, filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
        """
        Load CSV data with proper encoding handling.

        Args:
            filepath: Path to CSV file
            encoding: File encoding (utf-8, latin-1, etc.)

        Returns:
            Pandas DataFrame with loaded data
        """
        try:
            # Try UTF-8 first
            df = pd.read_csv(filepath, encoding=encoding)
            self.logger.info(f"Loaded {len(df)} records from {filepath}")
            return df

        except UnicodeDecodeError:
            # Fallback to latin-1 for Brazilian Portuguese files
            try:
                df = pd.read_csv(filepath, encoding="latin-1")
                self.logger.warning(f"Used latin-1 encoding for {filepath}")
                return df
            except Exception as e:
                self.logger.error(f"Failed to load {filepath}: {e}")
                raise

        except Exception as e:
            self.logger.error(f"Failed to load {filepath}: {e}")
            raise

    def clean_team_names(self, df: pd.DataFrame, team_column: str) -> pd.DataFrame:
        """
        Clean and normalize team names.

        Args:
            df: DataFrame containing team names
            team_column: Column name containing team names

        Returns:
            DataFrame with normalized team names
        """
        # Common team name mappings
        team_mappings = {
            "CR Flamengo": "Flamengo",
            "SE Palmeiras": "Palmeiras",
            "SC Corinthians Paulista": "Corinthians",
            "São Paulo FC": "São Paulo",
            "Grêmio FBPA": "Grêmio",
            "Sport Club Internacional": "Internacional",
            "Santos FC": "Santos",
            "Clube Atlético Mineiro": "Atlético-MG",
            "Cruzeiro EC": "Cruzeiro",
            "Botafogo FR": "Botafogo"
        }

        df = df.copy()

        # Apply mappings
        df[team_column] = df[team_column].replace(team_mappings)

        # Normalize text
        df[team_column] = df[team_column].apply(normalize_text)

        return df

    def extract_teams(self, matches_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract unique teams from matches data.

        Args:
            matches_df: DataFrame containing match data

        Returns:
            List of Team entities
        """
        teams = []
        team_names = set()

        # Get unique team names from home and away columns
        if "home_team" in matches_df.columns:
            team_names.update(matches_df["home_team"].dropna().unique())
        if "away_team" in matches_df.columns:
            team_names.update(matches_df["away_team"].dropna().unique())

        # Load additional team data if available
        team_data_file = self.data_dir / "sample" / "teams.csv"
        team_details = {}

        if team_data_file.exists():
            teams_df = self.load_csv_data(str(team_data_file))
            for _, row in teams_df.iterrows():
                team_details[row["name"]] = row.to_dict()

        # Create Team entities
        for team_name in sorted(team_names):
            details = team_details.get(team_name, {})

            team = {
                "id": details.get("team_id", self._generate_team_id(team_name)),
                "name": team_name,
                "full_name": details.get("full_name", team_name),
                "city": details.get("city"),
                "state": details.get("state"),
                "founded_year": safe_int(details.get("founded")),
                "stadium_name": details.get("stadium")
            }
            teams.append(team)

        self.logger.info(f"Extracted {len(teams)} teams")
        return teams

    def extract_players(self, players_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Extract players from player data.

        Args:
            players_df: DataFrame containing player data

        Returns:
            List of Player entities
        """
        if players_df is None:
            # Load sample player data
            player_data_file = self.data_dir / "sample" / "players.csv"
            if player_data_file.exists():
                players_df = self.load_csv_data(str(player_data_file))
            else:
                return []

        players = []

        for _, row in players_df.iterrows():
            # Map position
            position = None
            if "position" in row and pd.notna(row["position"]):
                pos_map = {"FWD": "Forward", "MID": "Midfielder",
                          "DEF": "Defender", "GK": "Goalkeeper"}
                position = pos_map.get(row["position"], row["position"])

            player = {
                "id": row.get("player_id", f"PLR_{len(players)}"),
                "name": normalize_text(row["name"]),
                "nationality": row.get("nationality", "Brazil"),
                "position": position,
                "height": safe_float(row.get("height")),
                "total_goals": safe_int(row.get("goals", 0)),
                "total_assists": safe_int(row.get("assists", 0)),
                "total_matches": safe_int(row.get("matches", 0))
            }
            players.append(player)

        self.logger.info(f"Extracted {len(players)} players")
        return players

    def extract_matches(self, matches_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Extract matches from match data.

        Args:
            matches_df: DataFrame containing match data

        Returns:
            List of Match entities
        """
        if matches_df is None:
            # Load sample match data
            match_data_file = self.data_dir / "sample" / "matches.csv"
            if match_data_file.exists():
                matches_df = self.load_csv_data(str(match_data_file))
            else:
                return []

        matches = []

        for _, row in matches_df.iterrows():
            match_date = parse_date(row["date"])

            match = {
                "id": row.get("match_id", f"MATCH_{len(matches)}"),
                "date": match_date.isoformat() if match_date else None,
                "home_team_id": self._generate_team_id(row["home_team"]),
                "away_team_id": self._generate_team_id(row["away_team"]),
                "home_score": safe_int(row.get("home_score")),
                "away_score": safe_int(row.get("away_score")),
                "status": "finished" if pd.notna(row.get("home_score")) else "scheduled",
                "round": str(row.get("round", ""))
            }
            matches.append(match)

        self.logger.info(f"Extracted {len(matches)} matches")
        return matches

    def extract_competitions(self) -> List[Dict[str, Any]]:
        """
        Extract competitions/tournaments.

        Returns:
            List of Competition entities
        """
        competitions = [
            {
                "id": "BRA_SERIE_A",
                "name": "Brasileirão Série A",
                "full_name": "Campeonato Brasileiro Série A",
                "type": "league",
                "country": "Brazil",
                "tier": 1,
                "total_teams": 20,
                "format": "round_robin"
            },
            {
                "id": "BRA_SERIE_B",
                "name": "Brasileirão Série B",
                "full_name": "Campeonato Brasileiro Série B",
                "type": "league",
                "country": "Brazil",
                "tier": 2,
                "total_teams": 20,
                "format": "round_robin"
            },
            {
                "id": "COPA_BR",
                "name": "Copa do Brasil",
                "full_name": "Copa do Brasil",
                "type": "cup",
                "country": "Brazil",
                "format": "knockout"
            },
            {
                "id": "LIBERTADORES",
                "name": "Copa Libertadores",
                "full_name": "Copa Libertadores da América",
                "type": "international",
                "format": "group_stage"
            }
        ]

        self.logger.info(f"Created {len(competitions)} competitions")
        return competitions

    def extract_stadiums(self) -> List[Dict[str, Any]]:
        """
        Extract stadium information.

        Returns:
            List of Stadium entities
        """
        stadiums = [
            {
                "id": "MARACANA",
                "name": "Maracanã",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "capacity": 78838,
                "opened_year": 1950
            },
            {
                "id": "ALLIANZ_PARQUE",
                "name": "Allianz Parque",
                "city": "São Paulo",
                "state": "SP",
                "capacity": 43713,
                "opened_year": 2014
            },
            {
                "id": "NEO_QUIMICA",
                "name": "Neo Química Arena",
                "city": "São Paulo",
                "state": "SP",
                "capacity": 49205,
                "opened_year": 2014
            },
            {
                "id": "MORUMBI",
                "name": "Estádio do Morumbi",
                "city": "São Paulo",
                "state": "SP",
                "capacity": 67428,
                "opened_year": 1960
            },
            {
                "id": "ARENA_GREMIO",
                "name": "Arena do Grêmio",
                "city": "Porto Alegre",
                "state": "RS",
                "capacity": 55662,
                "opened_year": 2012
            }
        ]

        self.logger.info(f"Created {len(stadiums)} stadiums")
        return stadiums

    def load_brazilian_championship_data(self) -> Dict[str, List[Any]]:
        """
        Load complete Brazilian championship data.

        Returns:
            Dictionary containing all extracted entities
        """
        self.logger.info("Loading Brazilian championship data...")

        # Load matches first (they contain team references)
        matches = self.extract_matches()

        # Extract teams from matches - convert to DataFrame
        if matches:
            matches_df = pd.DataFrame(matches)
            teams = self.extract_teams(matches_df)
        else:
            teams = []

        # Load other entities
        players = self.extract_players()
        competitions = self.extract_competitions()
        stadiums = self.extract_stadiums()

        data = {
            "teams": teams,
            "players": players,
            "matches": matches,
            "competitions": competitions,
            "stadiums": stadiums
        }

        self.logger.info("Data loading completed")
        return data

    def _generate_team_id(self, team_name: str) -> str:
        """Generate a team ID from team name."""
        # Common team abbreviations
        abbreviations = {
            "Flamengo": "FLA",
            "Palmeiras": "PAL",
            "Corinthians": "COR",
            "São Paulo": "SAO",
            "Grêmio": "GRE",
            "Internacional": "INT",
            "Santos": "SAN",
            "Atlético-MG": "ATL",
            "Cruzeiro": "CRU",
            "Botafogo": "BOT"
        }

        return abbreviations.get(team_name,
                                re.sub(r'[^A-Z]', '', normalize_text(team_name).upper())[:3])

    def validate_data(self, data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Validate loaded data for consistency and completeness.

        Args:
            data: Dictionary containing extracted entities

        Returns:
            Validation report
        """
        report = {
            "total_entities": sum(len(entities) for entities in data.values()),
            "entity_counts": {key: len(entities) for key, entities in data.items()},
            "issues": []
        }

        # Check for duplicate team IDs
        team_ids = [team.id for team in data.get("teams", [])]
        if len(team_ids) != len(set(team_ids)):
            report["issues"].append("Duplicate team IDs found")

        # Check for matches with missing teams
        team_id_set = set(team_ids)
        for match in data.get("matches", []):
            if match.home_team_id not in team_id_set:
                report["issues"].append(f"Match {match.id} references unknown home team {match.home_team_id}")
            if match.away_team_id not in team_id_set:
                report["issues"].append(f"Match {match.id} references unknown away team {match.away_team_id}")

        self.logger.info(f"Data validation completed: {len(report['issues'])} issues found")
        return report

    def load_fifa_players(self, years: Optional[List[int]] = None) -> Dict[int, pd.DataFrame]:
        """
        Load FIFA player datasets for specified years.

        Args:
            years: List of years to load (e.g., [15, 16, 17]). Defaults to all available.

        Returns:
            Dictionary mapping year to DataFrame
        """
        if years is None:
            years = [15, 16, 17, 18, 19, 20, 21, 22]

        data = {}
        kaggle_dir = self.data_dir / "kaggle"

        for year in years:
            filepath = kaggle_dir / f"players_{year}.csv"
            if filepath.exists():
                try:
                    df = self.load_csv_data(str(filepath))
                    data[year] = df
                    self.logger.info(f"Loaded {len(df)} players from FIFA {year}")
                except Exception as e:
                    self.logger.error(f"Failed to load players_{year}.csv: {e}")

        return data

    def extract_transfers_from_fifa(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Extract player transfers by comparing club changes across FIFA years.

        Args:
            limit: Maximum number of transfers to extract

        Returns:
            List of Transfer entities
        """
        fifa_data = self.load_fifa_players()

        if not fifa_data:
            self.logger.warning("No FIFA data available for transfer extraction")
            return []

        transfers = []
        years = sorted(fifa_data.keys())

        # Track player clubs across years
        player_history = {}  # {sofifa_id: {year: club_name}}

        for year in years:
            df = fifa_data[year]
            for _, row in df.iterrows():
                sofifa_id = row.get('sofifa_id')
                club_name = row.get('club_name')

                if pd.isna(sofifa_id) or pd.isna(club_name):
                    continue

                sofifa_id = int(sofifa_id)

                if sofifa_id not in player_history:
                    player_history[sofifa_id] = {
                        'clubs': {},
                        'name': row.get('short_name', ''),
                        'long_name': row.get('long_name', '')
                    }

                player_history[sofifa_id]['clubs'][year] = {
                    'club': club_name,
                    'joined': row.get('club_joined'),
                    'loaned_from': row.get('club_loaned_from')
                }

        # Identify transfers (club changes between consecutive years)
        transfer_id = 0
        for sofifa_id, history in player_history.items():
            clubs = history['clubs']
            years_list = sorted(clubs.keys())

            for i in range(len(years_list) - 1):
                prev_year = years_list[i]
                curr_year = years_list[i + 1]

                prev_club = clubs[prev_year]['club']
                curr_club = clubs[curr_year]['club']
                loaned_from = clubs[curr_year].get('loaned_from')

                # Skip if same club or loaned from same club
                if prev_club == curr_club:
                    continue

                # Skip if player is on loan
                if pd.notna(loaned_from):
                    transfer_type = "LOAN"
                else:
                    transfer_type = "PERMANENT"

                transfer = {
                    "id": f"TRF_{transfer_id:06d}",
                    "player_id": f"FIFA_{sofifa_id}",
                    "player_name": history['name'],
                    "from_team_id": self._generate_team_id(prev_club),
                    "from_team_name": prev_club,
                    "to_team_id": self._generate_team_id(curr_club),
                    "to_team_name": curr_club,
                    "transfer_year": 2000 + curr_year,
                    "transfer_type": transfer_type
                }
                transfers.append(transfer)
                transfer_id += 1

                if len(transfers) >= limit:
                    break

            if len(transfers) >= limit:
                break

        self.logger.info(f"Extracted {len(transfers)} transfers from FIFA data")
        return transfers

    def extract_coaches_from_fifa(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Extract coaches managing teams from FIFA datasets.

        Since FIFA player data doesn't include coaches directly, we'll create
        sample coaches for the major teams in the datasets.

        Args:
            limit: Maximum number of coaches to extract

        Returns:
            List of Coach entities with MANAGES relationships
        """
        fifa_data = self.load_fifa_players()

        if not fifa_data:
            self.logger.warning("No FIFA data available for coach extraction")
            return []

        # Get unique teams from the most recent year
        latest_year = max(fifa_data.keys())
        df = fifa_data[latest_year]

        unique_teams = df['club_name'].dropna().unique()

        # Famous coaches and their teams (as sample data)
        famous_coaches = {
            'FC Barcelona': {'name': 'Pep Guardiola', 'nationality': 'Spain'},
            'Real Madrid CF': {'name': 'Carlo Ancelotti', 'nationality': 'Italy'},
            'FC Bayern München': {'name': 'Julian Nagelsmann', 'nationality': 'Germany'},
            'Manchester City': {'name': 'Pep Guardiola', 'nationality': 'Spain'},
            'Liverpool': {'name': 'Jürgen Klopp', 'nationality': 'Germany'},
            'Chelsea': {'name': 'Thomas Tuchel', 'nationality': 'Germany'},
            'Manchester United': {'name': 'Erik ten Hag', 'nationality': 'Netherlands'},
            'Paris Saint-Germain': {'name': 'Christophe Galtier', 'nationality': 'France'},
            'Juventus': {'name': 'Massimiliano Allegri', 'nationality': 'Italy'},
            'Arsenal': {'name': 'Mikel Arteta', 'nationality': 'Spain'},
            'Tottenham Hotspur': {'name': 'Antonio Conte', 'nationality': 'Italy'},
            'Borussia Dortmund': {'name': 'Edin Terzic', 'nationality': 'Germany'},
            'Atlético Madrid': {'name': 'Diego Simeone', 'nationality': 'Argentina'},
            'Inter': {'name': 'Simone Inzaghi', 'nationality': 'Italy'},
            'AC Milan': {'name': 'Stefano Pioli', 'nationality': 'Italy'},
            'Napoli': {'name': 'Luciano Spalletti', 'nationality': 'Italy'},
            'Ajax': {'name': 'Alfred Schreuder', 'nationality': 'Netherlands'},
            'Sevilla FC': {'name': 'Jorge Sampaoli', 'nationality': 'Argentina'},
            'RB Leipzig': {'name': 'Marco Rose', 'nationality': 'Germany'},
            'Leicester City': {'name': 'Brendan Rodgers', 'nationality': 'Northern Ireland'},
        }

        coaches = []
        coach_id = 0

        for team_name in unique_teams[:limit]:
            if team_name in famous_coaches:
                coach_info = famous_coaches[team_name]
            else:
                # Generate a placeholder coach
                coach_info = {'name': f'Coach of {team_name}', 'nationality': 'Unknown'}

            coach = {
                "id": f"COACH_{coach_id:04d}",
                "name": coach_info['name'],
                "nationality": coach_info['nationality'],
                "team_id": self._generate_team_id(team_name),
                "team_name": team_name,
                "manages": True
            }
            coaches.append(coach)
            coach_id += 1

            if len(coaches) >= limit:
                break

        self.logger.info(f"Extracted {len(coaches)} coaches from FIFA data")
        return coaches

    def extract_teams_from_fifa(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Extract unique teams from FIFA player datasets.

        Args:
            limit: Maximum number of teams to extract

        Returns:
            List of Team entities
        """
        fifa_data = self.load_fifa_players()

        if not fifa_data:
            self.logger.warning("No FIFA data available for team extraction")
            return []

        all_teams = set()

        for year, df in fifa_data.items():
            teams = df['club_name'].dropna().unique()
            for team in teams:
                all_teams.add(team)

        teams_list = []
        for i, team_name in enumerate(sorted(all_teams)[:limit]):
            team = {
                "id": self._generate_team_id(team_name),
                "name": team_name,
                "full_name": team_name,
                "country": self._infer_team_country(team_name)
            }
            teams_list.append(team)

        self.logger.info(f"Extracted {len(teams_list)} teams from FIFA data")
        return teams_list

    def _infer_team_country(self, team_name: str) -> str:
        """Infer country from team name patterns."""
        country_patterns = {
            'FC Barcelona': 'Spain', 'Real Madrid': 'Spain', 'Atlético Madrid': 'Spain',
            'Bayern': 'Germany', 'Borussia': 'Germany', 'RB Leipzig': 'Germany',
            'Manchester': 'England', 'Liverpool': 'England', 'Chelsea': 'England',
            'Arsenal': 'England', 'Tottenham': 'England', 'Leicester': 'England',
            'Paris Saint-Germain': 'France', 'Lyon': 'France', 'Marseille': 'France',
            'Juventus': 'Italy', 'Inter': 'Italy', 'Milan': 'Italy', 'Napoli': 'Italy',
            'Roma': 'Italy', 'Ajax': 'Netherlands', 'PSV': 'Netherlands',
            'Porto': 'Portugal', 'Benfica': 'Portugal', 'Sporting': 'Portugal',
            'Flamengo': 'Brazil', 'Palmeiras': 'Brazil', 'Santos': 'Brazil',
            'Corinthians': 'Brazil', 'São Paulo': 'Brazil', 'Grêmio': 'Brazil'
        }

        for pattern, country in country_patterns.items():
            if pattern.lower() in team_name.lower():
                return country

        return "Unknown"

    def extract_players_from_fifa(self, year: int = 22, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Extract players from a specific FIFA year dataset.

        Args:
            year: FIFA year (e.g., 22 for FIFA 22)
            limit: Maximum number of players to extract

        Returns:
            List of Player entities
        """
        fifa_data = self.load_fifa_players([year])

        if year not in fifa_data:
            self.logger.warning(f"No FIFA {year} data available")
            return []

        df = fifa_data[year]
        players = []

        for _, row in df.head(limit).iterrows():
            player = {
                "id": f"FIFA_{row.get('sofifa_id', len(players))}",
                "name": row.get('short_name', ''),
                "full_name": row.get('long_name', ''),
                "nationality": row.get('nationality_name', 'Unknown'),
                "position": self._map_position(row.get('player_positions', '')),
                "height": safe_float(row.get('height_cm')),
                "weight": safe_float(row.get('weight_kg')),
                "preferred_foot": row.get('preferred_foot', 'Right'),
                "market_value": safe_float(row.get('value_eur')),
                "current_team_id": self._generate_team_id(row.get('club_name', '')),
                "current_team_name": row.get('club_name', '')
            }
            players.append(player)

        self.logger.info(f"Extracted {len(players)} players from FIFA {year}")
        return players

    def _map_position(self, positions: str) -> str:
        """Map FIFA position codes to position categories."""
        if pd.isna(positions):
            return "Unknown"

        pos = positions.split(',')[0].strip().upper()
        position_map = {
            'GK': 'Goalkeeper',
            'CB': 'Defender', 'RB': 'Defender', 'LB': 'Defender',
            'RWB': 'Defender', 'LWB': 'Defender',
            'CDM': 'Midfielder', 'CM': 'Midfielder', 'CAM': 'Midfielder',
            'RM': 'Midfielder', 'LM': 'Midfielder',
            'RW': 'Forward', 'LW': 'Forward', 'CF': 'Forward',
            'ST': 'Forward', 'RF': 'Forward', 'LF': 'Forward'
        }
        return position_map.get(pos, 'Unknown')