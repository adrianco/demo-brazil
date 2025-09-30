"""
Brazilian Soccer MCP Knowledge Graph - Data Utilities

CONTEXT:
This module implements utility functions for the Brazilian Soccer Knowledge Graph
MCP server. It provides tools for Brazilian text normalization, date parsing,
data validation, and type conversions specific to Brazilian soccer data processing.

PHASE: 1 - Core Data
PURPOSE: Brazilian text normalization and data validation utilities
DATA SOURCES: Brazilian soccer datasets with Portuguese text
DEPENDENCIES: unicodedata, datetime, re, typing

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Supports all entities with proper data normalization
- Performance: Optimized text processing for Brazilian Portuguese
- Testing: BDD scenarios with Brazilian names and text patterns

INTEGRATION:
- MCP Tools: Supports both kaggle_loader and graph_builder modules
- Error Handling: Graceful fallbacks for data parsing errors
- Rate Limiting: N/A for offline data processing
"""

import re
import unicodedata
import logging
from datetime import datetime, date
from typing import Optional, Union, Any, List, Dict
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """
    Normalize Brazilian Portuguese text for consistent processing.

    Handles common Portuguese characters, accents, and spacing issues
    while preserving proper capitalization and special characters.

    Args:
        text: Input text to normalize

    Returns:
        Normalized text string
    """
    if not text or not isinstance(text, str):
        return ""

    # Strip whitespace and handle empty strings
    text = text.strip()
    if not text:
        return ""

    # Normalize Unicode characters (NFKD - Canonical Decomposition)
    # This separates accented characters into base + combining characters
    normalized = unicodedata.normalize('NFKD', text)

    # Keep Portuguese characters intact - don't remove accents
    # Just normalize spacing and capitalization
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space

    return text

def normalize_brazilian_name(name: str) -> str:
    """
    Normalize Brazilian player/coach names with proper capitalization.

    Handles common Brazilian naming patterns like:
    - José da Silva -> José da Silva (keeps 'da' lowercase)
    - PELÉ -> Pelé
    - ronaldinho -> Ronaldinho

    Args:
        name: Person's name to normalize

    Returns:
        Properly capitalized Brazilian name
    """
    if not name:
        return ""

    # Normalize basic text first
    name = normalize_text(name)

    # Split into parts for proper capitalization
    parts = name.split()
    normalized_parts = []

    # Brazilian particles that should remain lowercase
    lowercase_particles = {
        'da', 'das', 'de', 'do', 'dos', 'e', 'em', 'na', 'nas', 'no', 'nos'
    }

    for i, part in enumerate(parts):
        # First and last parts are always capitalized
        if i == 0 or i == len(parts) - 1:
            normalized_parts.append(part.title())
        # Middle particles may stay lowercase
        elif part.lower() in lowercase_particles:
            normalized_parts.append(part.lower())
        else:
            normalized_parts.append(part.title())

    return ' '.join(normalized_parts)

def normalize_team_name(team_name: str) -> str:
    """
    Normalize Brazilian team names with proper formatting.

    Handles common team name variations and abbreviations:
    - CR Flamengo -> Clube de Regatas do Flamengo
    - palmeiras -> Palmeiras
    - CORINTHIANS -> Corinthians

    Args:
        team_name: Team name to normalize

    Returns:
        Normalized team name
    """
    if not team_name:
        return ""

    # Common team name mappings
    team_mappings = {
        # Full names
        'cr flamengo': 'Clube de Regatas do Flamengo',
        'clube de regatas do flamengo': 'Clube de Regatas do Flamengo',
        'se palmeiras': 'Sociedade Esportiva Palmeiras',
        'sociedade esportiva palmeiras': 'Sociedade Esportiva Palmeiras',
        'sc corinthians paulista': 'Sport Club Corinthians Paulista',
        'sport club corinthians paulista': 'Sport Club Corinthians Paulista',
        'são paulo fc': 'São Paulo Futebol Clube',
        'são paulo futebol clube': 'São Paulo Futebol Clube',
        'grêmio fbpa': 'Grêmio Foot-Ball Porto Alegrense',
        'grêmio foot-ball porto alegrense': 'Grêmio Foot-Ball Porto Alegrense',
        'sport club internacional': 'Sport Club Internacional',
        'santos fc': 'Santos Futebol Clube',
        'santos futebol clube': 'Santos Futebol Clube',
        'clube atlético mineiro': 'Clube Atlético Mineiro',
        'cruzeiro ec': 'Cruzeiro Esporte Clube',
        'cruzeiro esporte clube': 'Cruzeiro Esporte Clube',
        'botafogo fr': 'Botafogo de Futebol e Regatas',
        'botafogo de futebol e regatas': 'Botafogo de Futebol e Regatas',
        'club de regatas vasco da gama': 'Club de Regatas Vasco da Gama',
        'fluminense fc': 'Fluminense Football Club',
        'fluminense football club': 'Fluminense Football Club'
    }

    # Normalize and check mappings
    normalized = normalize_text(team_name.lower())

    # Check for exact matches first
    if normalized in team_mappings:
        return team_mappings[normalized]

    # Check for partial matches (common abbreviations)
    for key, full_name in team_mappings.items():
        if any(part in normalized for part in key.split() if len(part) > 2):
            return full_name

    # If no mapping found, return title case version
    return normalize_text(team_name.title())

def parse_date(date_str: Union[str, datetime, date]) -> Optional[datetime]:
    """
    Parse various date formats commonly found in Brazilian soccer data.

    Supports multiple formats:
    - ISO format: 2023-04-15
    - Brazilian format: 15/04/2023
    - Alternative formats: 15-04-2023, 15.04.2023
    - With time: 2023-04-15 15:30:00

    Args:
        date_str: Date string or date object to parse

    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None

    # If already a datetime object, return as-is
    if isinstance(date_str, datetime):
        return date_str

    # If a date object, convert to datetime
    if isinstance(date_str, date):
        return datetime.combine(date_str, datetime.min.time())

    # Clean the string
    date_str = str(date_str).strip()
    if not date_str:
        return None

    # Common Brazilian date formats
    formats = [
        # ISO formats
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',

        # Brazilian formats (day/month/year)
        '%d/%m/%Y',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',

        # Alternative separators
        '%d-%m-%Y',
        '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y %H:%M',
        '%d.%m.%Y',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',

        # Year/month/day with alternative separators
        '%Y/%m/%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    logger.warning(f"Could not parse date: {date_str}")
    return None

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN and None
        if str(value).lower() in ['nan', 'none', '']:
            return default

        # Try direct int conversion
        if isinstance(value, (int, float)):
            return int(value)

        # Try string conversion
        if isinstance(value, str):
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.-]', '', value.strip())
            if cleaned:
                return int(float(cleaned))

        return default

    except (ValueError, TypeError, OverflowError):
        logger.debug(f"Could not convert '{value}' to int, using default {default}")
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN and None
        if str(value).lower() in ['nan', 'none', '']:
            return default

        # Try direct float conversion
        if isinstance(value, (int, float)):
            return float(value)

        # Try string conversion
        if isinstance(value, str):
            # Remove common non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d.-]', '', value.strip())
            if cleaned:
                return float(cleaned)

        return default

    except (ValueError, TypeError, OverflowError):
        logger.debug(f"Could not convert '{value}' to float, using default {default}")
        return default

def safe_decimal(value: Any, default: Decimal = Decimal('0.0')) -> Decimal:
    """
    Safely convert value to Decimal for precise calculations.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Decimal value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN and None
        if str(value).lower() in ['nan', 'none', '']:
            return default

        # Try direct Decimal conversion
        if isinstance(value, (int, float)):
            return Decimal(str(value))

        # Try string conversion
        if isinstance(value, str):
            # Remove common non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d.-]', '', value.strip())
            if cleaned:
                return Decimal(cleaned)

        return default

    except (ValueError, TypeError, InvalidOperation):
        logger.debug(f"Could not convert '{value}' to Decimal, using default {default}")
        return default

def generate_id(prefix: str, name: str, suffix: str = None) -> str:
    """
    Generate a consistent ID from name components.

    Args:
        prefix: ID prefix (e.g., 'TEAM', 'PLAYER')
        name: Main name component
        suffix: Optional suffix

    Returns:
        Generated ID string
    """
    if not name:
        return f"{prefix}_UNKNOWN"

    # Normalize the name and create slug
    normalized = normalize_text(name)

    # Remove accents for ID generation (ASCII-safe)
    slug = unicodedata.normalize('NFKD', normalized)
    slug = ''.join(c for c in slug if not unicodedata.combining(c))

    # Replace spaces and special characters with underscores
    slug = re.sub(r'[^\w]', '_', slug).upper()

    # Remove multiple underscores
    slug = re.sub(r'_+', '_', slug).strip('_')

    # Limit length
    if len(slug) > 20:
        slug = slug[:20].rstrip('_')

    # Build final ID
    parts = [prefix, slug]
    if suffix:
        parts.append(str(suffix))

    return '_'.join(parts)

def validate_brazilian_name(name: str) -> bool:
    """
    Validate if a name looks like a valid Brazilian name.

    Args:
        name: Name to validate

    Returns:
        True if name appears valid
    """
    if not name or len(name.strip()) < 2:
        return False

    # Should contain only letters, spaces, and common Brazilian characters
    pattern = r'^[A-Za-zÀ-ÿ\s\'\-\.]+$'
    return bool(re.match(pattern, name.strip()))

def validate_team_name(team_name: str) -> bool:
    """
    Validate if a team name looks valid.

    Args:
        team_name: Team name to validate

    Returns:
        True if team name appears valid
    """
    if not team_name or len(team_name.strip()) < 3:
        return False

    # Should contain letters, numbers, spaces, and common characters
    pattern = r'^[A-Za-zÀ-ÿ0-9\s\'\-\.\(\)]+$'
    return bool(re.match(pattern, team_name.strip()))

def validate_score(score: Any) -> bool:
    """
    Validate if a score value is reasonable.

    Args:
        score: Score to validate

    Returns:
        True if score is valid
    """
    try:
        score_int = safe_int(score, -1)
        return 0 <= score_int <= 20  # Reasonable soccer score range
    except:
        return False

def clean_dict(data: Dict[str, Any], remove_none: bool = True,
               remove_empty: bool = True) -> Dict[str, Any]:
    """
    Clean dictionary by removing None/empty values.

    Args:
        data: Dictionary to clean
        remove_none: Remove None values
        remove_empty: Remove empty string values

    Returns:
        Cleaned dictionary
    """
    if not isinstance(data, dict):
        return {}

    cleaned = {}

    for key, value in data.items():
        # Skip None values if requested
        if remove_none and value is None:
            continue

        # Skip empty strings if requested
        if remove_empty and value == '':
            continue

        # Recursively clean nested dictionaries
        if isinstance(value, dict):
            nested_clean = clean_dict(value, remove_none, remove_empty)
            if nested_clean:  # Only add if not empty
                cleaned[key] = nested_clean
        else:
            cleaned[key] = value

    return cleaned

def format_brazilian_currency(amount: Union[float, int, str]) -> str:
    """
    Format currency in Brazilian Real format.

    Args:
        amount: Amount to format

    Returns:
        Formatted currency string
    """
    try:
        value = safe_float(amount)
        # Brazilian format: R$ 1.234.567,89
        formatted = f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except:
        return "R$ 0,00"

def extract_numbers_from_text(text: str) -> List[int]:
    """
    Extract all numbers from text string.

    Args:
        text: Text to extract numbers from

    Returns:
        List of extracted numbers
    """
    if not text:
        return []

    # Find all number patterns
    pattern = r'\d+'
    matches = re.findall(pattern, str(text))

    return [int(match) for match in matches]

def is_valid_year(year: Any) -> bool:
    """
    Check if year value is valid for soccer data.

    Args:
        year: Year to validate

    Returns:
        True if year is valid
    """
    try:
        year_int = safe_int(year)
        current_year = datetime.now().year
        return 1860 <= year_int <= current_year + 1  # Soccer history range
    except:
        return False

# Common Brazilian soccer data constants
BRAZILIAN_STATES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

PLAYER_POSITIONS = {
    'GK': 'Goalkeeper', 'GOL': 'Goalkeeper', 'GOLEIRO': 'Goalkeeper',
    'DEF': 'Defender', 'ZAG': 'Defender', 'ZAGUEIRO': 'Defender',
    'LAT': 'Defender', 'LATERAL': 'Defender',
    'MID': 'Midfielder', 'MEI': 'Midfielder', 'MEIA': 'Midfielder',
    'VOL': 'Midfielder', 'VOLANTE': 'Midfielder',
    'FWD': 'Forward', 'ATA': 'Forward', 'ATACANTE': 'Forward',
    'PON': 'Forward', 'PONTA': 'Forward'
}

def normalize_position(position: str) -> Optional[str]:
    """
    Normalize player position to standard format.

    Args:
        position: Position string to normalize

    Returns:
        Normalized position or None
    """
    if not position:
        return None

    position_upper = position.upper().strip()
    return PLAYER_POSITIONS.get(position_upper, position.title())

if __name__ == "__main__":
    # Test the utility functions
    print("Testing Brazilian soccer data utilities...")

    # Test name normalization
    test_names = [
        "PELÉ", "ronaldinho gaúcho", "José da Silva Santos",
        "JOÃO DE DEUS", "maria das graças"
    ]

    print("\nName normalization tests:")
    for name in test_names:
        normalized = normalize_brazilian_name(name)
        print(f"'{name}' -> '{normalized}'")

    # Test team name normalization
    test_teams = [
        "cr flamengo", "PALMEIRAS", "Corinthians", "são paulo fc"
    ]

    print("\nTeam name normalization tests:")
    for team in test_teams:
        normalized = normalize_team_name(team)
        print(f"'{team}' -> '{normalized}'")

    # Test date parsing
    test_dates = [
        "2023-04-15", "15/04/2023", "15-04-2023", "2023-04-15 15:30:00"
    ]

    print("\nDate parsing tests:")
    for date_str in test_dates:
        parsed = parse_date(date_str)
        print(f"'{date_str}' -> {parsed}")

    print("\nAll tests completed!")


def setup_logging(level='INFO'):
    import logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
