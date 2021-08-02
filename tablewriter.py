# import seaborn as sns
import os
import json
import csv

def parse_json(j):
    player_ct = len(j['1']['decks'])
    gamelength = len(j)-1
    games = [j['gameid'], player_ct, gamelength]

    rounds = []
    eliminations = [j['gameid']] + [None for _ in range(player_ct)]

    for i in range(gamelength):
        for idx, player in enumerate(j[str(i+1)]['decks']):
            rounds.append([j['gameid'], i+1, idx+1] + player)
            if player[0] == 0 and eliminations[idx] is None:
                eliminations[idx+1] = i+1

    return games, rounds, eliminations


def write_table(games, rounds, eliminations):
    with open('database/games.csv', 'a') as f:
        csv.writer(f).writerow(games)
    with open('database/rounds.csv', 'a') as f:
        csv.writer(f).writerows(rounds)
    with open('database/eliminations.csv', 'a') as f:
        csv.writer(f).writerow(eliminations)


def read_files():
    for path, dir, files in os.walk(f'{os.getcwd()}/logs'):
        for filename in files:
            if filename[-4:] == 'json':
                with open(path + '/' + filename, 'r') as f:
                    g, r, e = parse_json(json.loads(f.read()))
                write_table(g, r, e)


if __name__ == '__main__':
    read_files()