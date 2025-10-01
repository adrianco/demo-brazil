# Data Source Notes

## Current Implementation: Real Kaggle Data ✅

**Status**: The database now uses **real Kaggle datasets** with actual Brazilian football match data.

### What We're Using Now:
- **Real Kaggle datasets** with authentic Brazilian football history
- 17,068 actual matches from various competitions
- 673 real teams (Brazilian and international)
- 6 competitions (Brasileirão, Copa do Brasil, Copa Libertadores, etc.)
- Actual match statistics (goals, corners, attacks, shots)

### Data Sources:
1. **BR-Football-Dataset.csv**: 10,296 matches with detailed statistics (corners, attacks, shots)
2. **Brasileirao_Matches.csv**: 4,180 league matches from 2012+
3. **Brazilian_Cup_Matches.csv**: 1,337 cup matches from 2012+
4. **Libertadores_Matches.csv**: 1,255 continental matches from 2013+

## Data Loading Process

The database uses real Kaggle data loaded via `scripts/load_real_kaggle_data.py`.

### To Reload Data:

```bash
python scripts/load_real_kaggle_data.py
```

This script:
- Clears existing data from Neo4j
- Creates constraints for data integrity
- Loads all four Kaggle CSV files
- Normalizes team names across datasets
- Creates proper graph relationships
- Handles data quality issues (missing values, different formats)

### Schema Mapping

The loader maps Kaggle CSV fields to Neo4j graph structure:

**BR-Football-Dataset.csv:**
```
Kaggle Field          → Neo4j Property
tournament            → Competition.name
date                  → Match.date
time                  → Match.time
home                  → Team.name (via HOME_TEAM relationship)
away                  → Team.name (via AWAY_TEAM relationship)
home_goal             → Match.home_score
away_goal             → Match.away_score
home_corner           → Match.home_corners
away_corner           → Match.away_corners
home_attack           → Match.home_attacks
away_attack           → Match.away_attacks
home_shots            → Match.home_shots
away_shots            → Match.away_shots
```

**Brasileirao_Matches.csv:**
```
Kaggle Field          → Neo4j Property
datetime              → Match.datetime
season                → Match.season
round                 → Match.round
home_team             → Team.name (normalized, e.g., "Palmeiras-SP" → "Palmeiras")
away_team             → Team.name (normalized)
home_goal             → Match.home_score
away_goal             → Match.away_score
home_team_state       → Match.home_state
away_team_state       → Match.away_state
```

### Current Data Quality

**Real Kaggle Data Characteristics:**
- ✅ Actual historical match results from 2012-2023
- ✅ Real competition data (Brasileirão, Copa do Brasil, Libertadores)
- ✅ Authentic team names and match statistics
- ✅ Proper graph relationships (HOME_TEAM, AWAY_TEAM, PART_OF)
- ✅ 673 unique teams including international clubs
- ✅ 17,068 verified matches
- ✅ Detailed match statistics (corners, attacks, shots)
- ⚠️ No individual player statistics (team-level data only)
- ⚠️ Some missing scores in Libertadores dataset (handled gracefully)

### Data Quality Improvements:
- **Team Name Normalization**: Handles variations like "Palmeiras-SP" vs "Palmeiras"
- **Missing Value Handling**: Gracefully handles '-' and null values in scores
- **Duplicate Prevention**: Match IDs prevent duplicate entries
- **Competition Classification**: Automatically categorizes as league/cup/continental

## Implementation Status

1. ✅ **Phase 1 (Done)**: Synthetic data with proper graph structure (archived)
2. ✅ **Phase 2 (Done)**: Real Kaggle data integration complete
3. ⏳ **Phase 3 (Future)**: Individual player statistics from additional datasets
4. ⏳ **Phase 4 (Future)**: API integration for current season data

## Quick Start

To load the real Kaggle data into your Neo4j instance:

```bash
# Ensure Neo4j is running on bolt://localhost:7687
# Default credentials: neo4j/neo4j123

# Load all real Kaggle datasets
python scripts/load_real_kaggle_data.py
```

Expected output:
- 673 teams
- 17,068 matches
- 6 competitions
- 51,204 total relationships

---

*Last Updated: 2025-10-01*
*Current Dataset: Real Kaggle Data (Loaded)*
*Synthetic Data: Archived (scripts/*.old)*
