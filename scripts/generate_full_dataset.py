#!/usr/bin/env python3
"""
Generate comprehensive Brazilian football dataset for testing.
This simulates a full Kaggle dataset with realistic Brazilian football data.
"""

import csv
import json
import random
from datetime import datetime, timedelta
import os

# Create output directory
os.makedirs("data/kaggle", exist_ok=True)

# Brazilian teams data
teams = [
    # Serie A teams
    {"team_id": "FLA", "name": "Clube de Regatas do Flamengo", "city": "Rio de Janeiro", "state": "RJ", "founded": 1895, "stadium": "Maracanã", "capacity": 78838},
    {"team_id": "COR", "name": "Sport Club Corinthians Paulista", "city": "São Paulo", "state": "SP", "founded": 1910, "stadium": "Neo Química Arena", "capacity": 49205},
    {"team_id": "PAL", "name": "Sociedade Esportiva Palmeiras", "city": "São Paulo", "state": "SP", "founded": 1914, "stadium": "Allianz Parque", "capacity": 43713},
    {"team_id": "SAN", "name": "Santos Futebol Clube", "city": "Santos", "state": "SP", "founded": 1912, "stadium": "Vila Belmiro", "capacity": 16068},
    {"team_id": "SPF", "name": "São Paulo Futebol Clube", "city": "São Paulo", "state": "SP", "founded": 1930, "stadium": "Morumbi", "capacity": 66795},
    {"team_id": "GRE", "name": "Grêmio Foot-Ball Porto Alegrense", "city": "Porto Alegre", "state": "RS", "founded": 1903, "stadium": "Arena do Grêmio", "capacity": 55662},
    {"team_id": "INT", "name": "Sport Club Internacional", "city": "Porto Alegre", "state": "RS", "founded": 1909, "stadium": "Beira-Rio", "capacity": 50128},
    {"team_id": "CAM", "name": "Clube Atlético Mineiro", "city": "Belo Horizonte", "state": "MG", "founded": 1908, "stadium": "Mineirão", "capacity": 61846},
    {"team_id": "CRU", "name": "Cruzeiro Esporte Clube", "city": "Belo Horizonte", "state": "MG", "founded": 1921, "stadium": "Mineirão", "capacity": 61846},
    {"team_id": "VAS", "name": "Club de Regatas Vasco da Gama", "city": "Rio de Janeiro", "state": "RJ", "founded": 1898, "stadium": "São Januário", "capacity": 21880},
    {"team_id": "BOT", "name": "Botafogo de Futebol e Regatas", "city": "Rio de Janeiro", "state": "RJ", "founded": 1894, "stadium": "Nilton Santos", "capacity": 46831},
    {"team_id": "FLU", "name": "Fluminense Football Club", "city": "Rio de Janeiro", "state": "RJ", "founded": 1902, "stadium": "Maracanã", "capacity": 78838},
    {"team_id": "ATH", "name": "Club Athletico Paranaense", "city": "Curitiba", "state": "PR", "founded": 1924, "stadium": "Arena da Baixada", "capacity": 42372},
    {"team_id": "BAH", "name": "Esporte Clube Bahia", "city": "Salvador", "state": "BA", "founded": 1931, "stadium": "Arena Fonte Nova", "capacity": 47907},
    {"team_id": "FOR", "name": "Fortaleza Esporte Clube", "city": "Fortaleza", "state": "CE", "founded": 1918, "stadium": "Castelão", "capacity": 63903},
    {"team_id": "RBB", "name": "Red Bull Bragantino", "city": "Bragança Paulista", "state": "SP", "founded": 1928, "stadium": "Nabi Abi Chedid", "capacity": 15010},
    {"team_id": "CEA", "name": "Ceará Sporting Club", "city": "Fortaleza", "state": "CE", "founded": 1914, "stadium": "Castelão", "capacity": 63903},
    {"team_id": "GOI", "name": "Goiás Esporte Clube", "city": "Goiânia", "state": "GO", "founded": 1943, "stadium": "Serrinha", "capacity": 16500},
    {"team_id": "CUI", "name": "Cuiabá Esporte Clube", "city": "Cuiabá", "state": "MT", "founded": 2001, "stadium": "Arena Pantanal", "capacity": 44000},
    {"team_id": "AME", "name": "América Futebol Clube", "city": "Belo Horizonte", "state": "MG", "founded": 1912, "stadium": "Independência", "capacity": 23018}
]

# Famous Brazilian players
players = [
    # Legends
    {"player_id": "PEL", "name": "Pelé", "full_name": "Edson Arantes do Nascimento", "position": "Forward", "birth_date": "1940-10-23", "nationality": "Brazilian", "height": 173, "weight": 75},
    {"player_id": "GAR", "name": "Garrincha", "full_name": "Manuel Francisco dos Santos", "position": "Winger", "birth_date": "1933-10-28", "nationality": "Brazilian", "height": 169, "weight": 72},
    {"player_id": "ZIC", "name": "Zico", "full_name": "Arthur Antunes Coimbra", "position": "Midfielder", "birth_date": "1953-03-03", "nationality": "Brazilian", "height": 172, "weight": 70},
    {"player_id": "ROM", "name": "Romário", "full_name": "Romário de Souza Faria", "position": "Forward", "birth_date": "1966-01-29", "nationality": "Brazilian", "height": 167, "weight": 70},
    {"player_id": "RON", "name": "Ronaldo", "full_name": "Ronaldo Luís Nazário de Lima", "position": "Forward", "birth_date": "1976-09-18", "nationality": "Brazilian", "height": 183, "weight": 82},
    {"player_id": "RDG", "name": "Ronaldinho", "full_name": "Ronaldo de Assis Moreira", "position": "Midfielder", "birth_date": "1980-03-21", "nationality": "Brazilian", "height": 181, "weight": 80},
    {"player_id": "RIV", "name": "Rivaldo", "full_name": "Rivaldo Vítor Borba Ferreira", "position": "Forward", "birth_date": "1972-04-19", "nationality": "Brazilian", "height": 186, "weight": 75},
    {"player_id": "CAF", "name": "Cafu", "full_name": "Marcos Evangelista de Morais", "position": "Defender", "birth_date": "1970-06-07", "nationality": "Brazilian", "height": 176, "weight": 73},
    {"player_id": "RCA", "name": "Roberto Carlos", "full_name": "Roberto Carlos da Silva Rocha", "position": "Defender", "birth_date": "1973-04-10", "nationality": "Brazilian", "height": 168, "weight": 70},
    {"player_id": "BEB", "name": "Bebeto", "full_name": "José Roberto Gama de Oliveira", "position": "Forward", "birth_date": "1964-02-16", "nationality": "Brazilian", "height": 175, "weight": 72},
    {"player_id": "SOC", "name": "Sócrates", "full_name": "Sócrates Brasileiro Sampaio de Souza Vieira de Oliveira", "position": "Midfielder", "birth_date": "1954-02-19", "nationality": "Brazilian", "height": 192, "weight": 79},
    {"player_id": "KAK", "name": "Kaká", "full_name": "Ricardo Izecson dos Santos Leite", "position": "Midfielder", "birth_date": "1982-04-22", "nationality": "Brazilian", "height": 186, "weight": 82},

    # Current stars
    {"player_id": "NEY", "name": "Neymar Jr", "full_name": "Neymar da Silva Santos Júnior", "position": "Forward", "birth_date": "1992-02-05", "nationality": "Brazilian", "height": 175, "weight": 68},
    {"player_id": "VIN", "name": "Vinícius Jr", "full_name": "Vinícius José Paixão de Oliveira Júnior", "position": "Forward", "birth_date": "2000-07-12", "nationality": "Brazilian", "height": 176, "weight": 73},
    {"player_id": "ROD", "name": "Rodrygo", "full_name": "Rodrygo Silva de Goes", "position": "Forward", "birth_date": "2001-01-09", "nationality": "Brazilian", "height": 174, "weight": 64},
    {"player_id": "ALI", "name": "Alisson", "full_name": "Alisson Ramses Becker", "position": "Goalkeeper", "birth_date": "1992-10-02", "nationality": "Brazilian", "height": 193, "weight": 91},
    {"player_id": "EDE", "name": "Ederson", "full_name": "Ederson Santana de Moraes", "position": "Goalkeeper", "birth_date": "1993-08-17", "nationality": "Brazilian", "height": 188, "weight": 86},
    {"player_id": "CAS", "name": "Casemiro", "full_name": "Carlos Henrique Casimiro", "position": "Midfielder", "birth_date": "1992-02-23", "nationality": "Brazilian", "height": 185, "weight": 84},
    {"player_id": "MAR", "name": "Marquinhos", "full_name": "Marcos Aoás Corrêa", "position": "Defender", "birth_date": "1994-05-14", "nationality": "Brazilian", "height": 183, "weight": 75},
    {"player_id": "TSI", "name": "Thiago Silva", "full_name": "Thiago Emiliano da Silva", "position": "Defender", "birth_date": "1984-09-22", "nationality": "Brazilian", "height": 183, "weight": 79},
    {"player_id": "MIL", "name": "Éder Militão", "full_name": "Éder Gabriel Militão", "position": "Defender", "birth_date": "1998-01-18", "nationality": "Brazilian", "height": 186, "weight": 78},
    {"player_id": "BRU", "name": "Bruno Guimarães", "full_name": "Bruno Guimarães Rodriguez Moura", "position": "Midfielder", "birth_date": "1997-11-16", "nationality": "Brazilian", "height": 182, "weight": 71},
    {"player_id": "LUC", "name": "Lucas Paquetá", "full_name": "Lucas Tolentino Coelho de Lima", "position": "Midfielder", "birth_date": "1997-08-27", "nationality": "Brazilian", "height": 180, "weight": 72},
    {"player_id": "GAB", "name": "Gabriel Jesus", "full_name": "Gabriel Fernando de Jesus", "position": "Forward", "birth_date": "1997-04-03", "nationality": "Brazilian", "height": 175, "weight": 73},
    {"player_id": "ANT", "name": "Antony", "full_name": "Antony Matheus dos Santos", "position": "Forward", "birth_date": "2000-02-24", "nationality": "Brazilian", "height": 174, "weight": 63},
    {"player_id": "RAF", "name": "Raphinha", "full_name": "Raphael Dias Belloli", "position": "Forward", "birth_date": "1996-12-14", "nationality": "Brazilian", "height": 176, "weight": 68},
    {"player_id": "RIC", "name": "Richarlison", "full_name": "Richarlison de Andrade", "position": "Forward", "birth_date": "1997-05-10", "nationality": "Brazilian", "height": 184, "weight": 83},
    {"player_id": "FRE", "name": "Fred", "full_name": "Frederico Rodrigues de Paula Santos", "position": "Midfielder", "birth_date": "1993-03-05", "nationality": "Brazilian", "height": 169, "weight": 64},
    {"player_id": "FAB", "name": "Fabinho", "full_name": "Fábio Henrique Tavares", "position": "Midfielder", "birth_date": "1993-10-23", "nationality": "Brazilian", "height": 188, "weight": 78},
    {"player_id": "DAN", "name": "Danilo", "full_name": "Danilo Luiz da Silva", "position": "Defender", "birth_date": "1991-07-15", "nationality": "Brazilian", "height": 184, "weight": 78},

    # Domestic stars
    {"player_id": "GAB1", "name": "Gabigol", "full_name": "Gabriel Barbosa Almeida", "position": "Forward", "birth_date": "1996-08-30", "nationality": "Brazilian", "height": 178, "weight": 78},
    {"player_id": "ARR", "name": "Arrascaeta", "full_name": "Giorgian De Arrascaeta", "position": "Midfielder", "birth_date": "1994-06-01", "nationality": "Uruguayan", "height": 174, "weight": 74},
    {"player_id": "HUL", "name": "Hulk", "full_name": "Givanildo Vieira de Sousa", "position": "Forward", "birth_date": "1986-07-25", "nationality": "Brazilian", "height": 180, "weight": 94},
    {"player_id": "VEI", "name": "Veiga", "full_name": "Raphael Veiga", "position": "Midfielder", "birth_date": "1995-06-19", "nationality": "Brazilian", "height": 177, "weight": 75},
    {"player_id": "DUD", "name": "Dudu", "full_name": "Eduardo Pereira Rodrigues", "position": "Forward", "birth_date": "1992-01-07", "nationality": "Brazilian", "height": 166, "weight": 66},
    {"player_id": "RON2", "name": "Rony", "full_name": "Ronielson da Silva Barbosa", "position": "Forward", "birth_date": "1995-05-11", "nationality": "Brazilian", "height": 169, "weight": 65},
    {"player_id": "EVE", "name": "Everton Ribeiro", "full_name": "Everton Augusto de Barros Ribeiro", "position": "Midfielder", "birth_date": "1989-04-10", "nationality": "Brazilian", "height": 175, "weight": 70},
    {"player_id": "PED", "name": "Pedro", "full_name": "Pedro Guilherme Abreu dos Santos", "position": "Forward", "birth_date": "1997-06-20", "nationality": "Brazilian", "height": 185, "weight": 83},
    {"player_id": "CAL", "name": "Calleri", "full_name": "Jonathan Calleri", "position": "Forward", "birth_date": "1993-09-23", "nationality": "Argentine", "height": 184, "weight": 81},
    {"player_id": "NAC", "name": "Nacho Fernández", "full_name": "Ignacio Fernández Lobbe", "position": "Midfielder", "birth_date": "1990-01-12", "nationality": "Argentine", "height": 172, "weight": 68}
]

# Competitions
competitions = [
    {"competition_id": "BRA1", "name": "Campeonato Brasileiro Série A", "type": "League", "country": "Brazil", "level": 1},
    {"competition_id": "BRA2", "name": "Campeonato Brasileiro Série B", "type": "League", "country": "Brazil", "level": 2},
    {"competition_id": "COPA", "name": "Copa do Brasil", "type": "Cup", "country": "Brazil", "level": 1},
    {"competition_id": "LIBC", "name": "Copa Libertadores", "type": "Continental", "country": "South America", "level": 1},
    {"competition_id": "SUDA", "name": "Copa Sul-Americana", "type": "Continental", "country": "South America", "level": 2},
    {"competition_id": "PAUL", "name": "Campeonato Paulista", "type": "State", "country": "Brazil", "level": 1},
    {"competition_id": "CARI", "name": "Campeonato Carioca", "type": "State", "country": "Brazil", "level": 1},
    {"competition_id": "MINE", "name": "Campeonato Mineiro", "type": "State", "country": "Brazil", "level": 1},
    {"competition_id": "GAUC", "name": "Campeonato Gaúcho", "type": "State", "country": "Brazil", "level": 1},
    {"competition_id": "RECB", "name": "Recopa Sul-Americana", "type": "Super Cup", "country": "South America", "level": 1}
]

# Coaches
coaches = [
    {"coach_id": "TIT", "name": "Tite", "full_name": "Adenor Leonardo Bacchi", "birth_date": "1961-05-25", "nationality": "Brazilian"},
    {"coach_id": "ANG", "name": "Ancelotti", "full_name": "Carlo Ancelotti", "birth_date": "1959-06-10", "nationality": "Italian"},
    {"coach_id": "JJ", "name": "Jorge Jesus", "full_name": "Jorge Fernando Pinheiro de Jesus", "birth_date": "1954-07-24", "nationality": "Portuguese"},
    {"coach_id": "REN", "name": "Renato Gaúcho", "full_name": "Renato Portaluppi", "birth_date": "1962-09-09", "nationality": "Brazilian"},
    {"coach_id": "ABE", "name": "Abel Ferreira", "full_name": "Abel Fernando Moreira Ferreira", "birth_date": "1978-12-22", "nationality": "Portuguese"},
    {"coach_id": "COD", "name": "Vítor Pereira", "full_name": "Vítor Manuel de Oliveira Lopes Pereira", "birth_date": "1968-07-26", "nationality": "Portuguese"},
    {"coach_id": "COU", "name": "Cuca", "full_name": "Alexi Stival", "birth_date": "1963-06-07", "nationality": "Brazilian"},
    {"coach_id": "MEI", "name": "Rogério Ceni", "full_name": "Rogério Mücke Ceni", "birth_date": "1973-01-22", "nationality": "Brazilian"},
    {"coach_id": "DOR", "name": "Dorival Júnior", "full_name": "Dorival Silvestre Júnior", "birth_date": "1962-04-25", "nationality": "Brazilian"},
    {"coach_id": "FEL", "name": "Felipe Luis", "full_name": "Filipe Luís Kasmirski", "birth_date": "1985-08-09", "nationality": "Brazilian"}
]

# Generate matches
def generate_matches(num_matches=500):
    matches = []
    start_date = datetime(2020, 1, 1)

    for i in range(num_matches):
        # Random teams
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t["team_id"] != home_team["team_id"]])

        # Random date
        match_date = start_date + timedelta(days=random.randint(0, 1460))

        # Random scores
        home_score = random.randint(0, 5)
        away_score = random.randint(0, 5)

        # Random competition
        competition = random.choice(competitions)

        # Generate match
        match = {
            "match_id": f"M{i+1:04d}",
            "date": match_date.strftime("%Y-%m-%d"),
            "time": f"{random.randint(14, 21)}:00",
            "home_team": home_team["team_id"],
            "away_team": away_team["team_id"],
            "home_score": home_score,
            "away_score": away_score,
            "competition": competition["competition_id"],
            "stadium": home_team["stadium"],
            "attendance": random.randint(5000, home_team["capacity"]),
            "referee": f"Referee_{random.randint(1, 20)}",
            "round": random.randint(1, 38)
        }
        matches.append(match)

    return matches

# Assign each player to a primary team
def assign_players_to_teams(players, teams):
    """Assign each player to one primary team."""
    player_teams = {}
    players_per_team = len(players) // len(teams) + 1

    team_idx = 0
    for i, player in enumerate(players):
        if i % players_per_team == 0 and i > 0:
            team_idx = (team_idx + 1) % len(teams)
        player_teams[player["player_id"]] = teams[team_idx]["team_id"]

    return player_teams

# Generate player stats
def generate_player_stats(matches, players, player_teams):
    player_stats = []

    for match in matches:
        home_team = match["home_team"]
        away_team = match["away_team"]

        # Get players who play for home team
        home_players = [p for p in players if player_teams.get(p["player_id"]) == home_team]
        # Get players who play for away team
        away_players = [p for p in players if player_teams.get(p["player_id"]) == away_team]

        # Select 11 players from each team (or all if less than 11)
        home_squad = random.sample(home_players, min(11, len(home_players))) if home_players else []
        away_squad = random.sample(away_players, min(11, len(away_players))) if away_players else []

        # Generate stats for home team players
        for player in home_squad:
            stat = {
                "match_id": match["match_id"],
                "player_id": player["player_id"],
                "team_id": home_team,
                "minutes_played": random.randint(1, 90),
                "goals": random.randint(0, 2) if random.random() > 0.8 else 0,
                "assists": random.randint(0, 2) if random.random() > 0.85 else 0,
                "yellow_cards": 1 if random.random() > 0.9 else 0,
                "red_cards": 1 if random.random() > 0.98 else 0,
                "rating": round(random.uniform(5.5, 10.0), 1)
            }
            player_stats.append(stat)

        # Generate stats for away team players
        for player in away_squad:
            stat = {
                "match_id": match["match_id"],
                "player_id": player["player_id"],
                "team_id": away_team,
                "minutes_played": random.randint(1, 90),
                "goals": random.randint(0, 2) if random.random() > 0.8 else 0,
                "assists": random.randint(0, 2) if random.random() > 0.85 else 0,
                "yellow_cards": 1 if random.random() > 0.9 else 0,
                "red_cards": 1 if random.random() > 0.98 else 0,
                "rating": round(random.uniform(5.5, 10.0), 1)
            }
            player_stats.append(stat)

    return player_stats

# Generate transfers
def generate_transfers(players, teams):
    transfers = []

    for i in range(100):
        player = random.choice(players)
        from_team = random.choice(teams)
        to_team = random.choice([t for t in teams if t["team_id"] != from_team["team_id"]])

        transfer = {
            "transfer_id": f"T{i+1:04d}",
            "player_id": player["player_id"],
            "from_team": from_team["team_id"],
            "to_team": to_team["team_id"],
            "date": datetime(2020 + random.randint(0, 3), random.randint(1, 12), random.randint(1, 28)).strftime("%Y-%m-%d"),
            "fee": random.randint(0, 50000000),
            "type": random.choice(["Transfer", "Loan", "Free", "End of Loan"])
        }
        transfers.append(transfer)

    return transfers

# Write CSV files
def write_csv(filename, data, fieldnames):
    with open(f"data/kaggle/{filename}", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Created {filename} with {len(data)} records")

# Generate all data
print("Generating comprehensive Brazilian football dataset...")
print("=" * 60)

# Generate matches
matches = generate_matches(1000)
write_csv("matches.csv", matches,
          ["match_id", "date", "time", "home_team", "away_team", "home_score", "away_score",
           "competition", "stadium", "attendance", "referee", "round"])

# Write teams
write_csv("teams.csv", teams,
          ["team_id", "name", "city", "state", "founded", "stadium", "capacity"])

# Write players
write_csv("players.csv", players,
          ["player_id", "name", "full_name", "position", "birth_date", "nationality", "height", "weight"])

# Assign players to teams (each player gets one primary team)
player_teams = assign_players_to_teams(players, teams)

# Generate and write player stats
player_stats = generate_player_stats(matches, players, player_teams)
write_csv("player_stats.csv", player_stats,
          ["match_id", "player_id", "team_id", "minutes_played", "goals", "assists",
           "yellow_cards", "red_cards", "rating"])

# Write competitions
write_csv("competitions.csv", competitions,
          ["competition_id", "name", "type", "country", "level"])

# Write coaches
write_csv("coaches.csv", coaches,
          ["coach_id", "name", "full_name", "birth_date", "nationality"])

# Generate and write transfers
transfers = generate_transfers(players, teams)
write_csv("transfers.csv", transfers,
          ["transfer_id", "player_id", "from_team", "to_team", "date", "fee", "type"])

# Create summary
summary = {
    "dataset": "Brazilian Football Dataset",
    "generated": datetime.now().isoformat(),
    "statistics": {
        "teams": len(teams),
        "players": len(players),
        "matches": len(matches),
        "player_stats": len(player_stats),
        "competitions": len(competitions),
        "coaches": len(coaches),
        "transfers": len(transfers)
    }
}

with open("data/kaggle/dataset_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 60)
print("Dataset generation complete!")
print(f"Total records: {sum(summary['statistics'].values())}")
print("\nFiles created in data/kaggle/:")
for key, value in summary['statistics'].items():
    print(f"  - {key}: {value} records")