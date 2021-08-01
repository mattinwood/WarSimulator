from game import War

if __name__ == '__main__':
    for player_ct in [2, 3, 4]:
        for _ in range(10000):
            game = War(player_ct, False, True)
            game.resolve_game()