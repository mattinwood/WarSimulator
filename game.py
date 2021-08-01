from random import shuffle, seed
from itertools import chain
from time import time
from uuid import uuid4
import json


def flatten(listlike):
    return list(chain.from_iterable(listlike))


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

        self.face = {
            11: 'Jack',
            12: 'Queen',
            13: 'King',
            14: 'Ace'  # Aces are high in War
        }
        self.name = f'{self.face[self.value] if self.value in self.face else str(self.value)} of {suit}'


class Deck:
    def __init__(self):
        self.cards = []

    def build(self):
        for suit in ['Hearts', 'Diamonds', 'Spades', 'Clubs']:
            for val in range(2, 15):
                self.cards.append(Card(suit, val))

    def shuffle(self):
        shuffle(self.cards)

    def print_deck(self):
        for card in self.cards:
            print(card.name)

    def draw(self, n=1):
        if (n > 1) and (n <= len(self.cards)):
            return[self.cards.pop() for _ in range(n)]
        elif n == 1:
            if len(self.cards) > 0:
                return self.cards.pop()
            else:
                return Card('{null}', -100)  # Dummy card if player runs out of cards to draw
        else:
            raise ValueError(f'{n} is not a valid number of cards to draw')


class Player:
    def __init__(self):
        self.draw_pile = Deck()
        self.discard_pile = Deck()
        self.is_active = True
        self.eliminated_round = None

    def deck_size(self):
        return len(self.draw_pile.cards) + len(self.discard_pile.cards)

    def deck_power(self):
        try:
            return ((sum(x.value for x in self.draw_pile.cards) +
                     sum(x.value for x in self.discard_pile.cards)) /
                    self.deck_size())
        except ZeroDivisionError:
            return None

    def is_out(self, round_num):
        if self.deck_size() == 0:
            self.is_active = False
            if self.eliminated_round is None:
                self.eliminated_round = round_num

    def check_deck(self):
        if self.deck_size() == 0:
            self.is_active = False
        elif len(self.draw_pile.cards) == 0:
            self.draw_pile = self.discard_pile
            self.discard_pile = Deck()
            self.draw_pile.shuffle()


class War:
    def __init__(self, player_ct=2, verbose=False, logging=False):
        self.players = [Player() for _ in range(player_ct)]
        self.verbose = verbose
        self.logging = logging
        self.round_ct = 0
        if logging:
            self.log = {'gameid': str(uuid4())}

    def deal_cards(self):
        deck = Deck()
        deck.build()
        deck.shuffle()
        while True:
            for i, p in enumerate(self.players):
                if len(deck.cards) <= 0:
                    return
                self.players[i].draw_pile.cards.append(deck.draw())

    def print_player_stack_sizes(self):
        for i, p in enumerate(self.players):
            print(f' Player {i+1}: {self.players[i].deck_size()} cards'
                  f'({len(self.players[i].draw_pile.cards)} in draw pile)')

    def log_deck(self):
        self.log[self.round_ct]['decks'] = [[x.deck_size(), x.deck_power()] for x in self.players]

    def log_battle(self, pot):
        self.log[self.round_ct]['battle'] = [[y.value for y in x] for x in pot]

    def play_round(self):
        self.round_ct += 1
        if self.logging:
            self.log[self.round_ct] = {'decks': None, 'battle': None}
            self.log_deck()

        if self.verbose:
            print(f'\n Round {self.round_ct} Started')
            print(f'Players {", ".join([str(i+1) for i, x in enumerate(self.players) if x.is_active is True])} active')

        for player in self.players:
            player.is_out(self.round_ct)

        pot = [[] for _ in self.players]
        pot = self.draw_for_round(pot)
        self.resolve_battle(pot)

        if self.verbose:
            self.print_player_stack_sizes()

    def resolve_battle(self, pot):
        battle = [x[-1].value for x in pot]

        if battle.count(max(battle)) > 1:
            if self.verbose:
                print('Draw, additional cards drawn')
            pot = self.draw_for_round(pot)  # In War rules, these are face down
            pot = self.draw_for_round(pot)  # These are the cards drawn for resolving the tie breaker
            self.resolve_battle(pot)
            return
        else:
            if self.logging:
                self.log_battle(pot)
            self.players[battle.index(max(battle))].discard_pile.cards += [x for x in flatten(pot) if x.value > 0]

    def draw_for_round(self, pot):
        for player in self.players:
            player.check_deck()
        [pot[i].append(self.players[i].draw_pile.draw()) for i, p in enumerate(self.players)]
        if self.verbose:
            print(f'Players Draw: {[x[-1].name for x in pot]}')
            print(f'Size of pot: {len([x for x in flatten(pot) if x.value > 0])}')
        return pot

    def resolve_game(self):
        self.deal_cards()
        while sum([1 if x.is_active is True else 0 for x in self.players]) > 1:
            self.play_round()
        if self.verbose:
            print(f'Game finished in {self.round_ct} rounds')
            print(f'Player {[x.eliminated_round for x in self.players].index(None)+1} wins!')
        if self.logging:
            self.save_logs_to_disk()

    def save_logs_to_disk(self):
        with open(f'logs/{self.log["gameid"]}.json', 'w') as f:
            json.dump(self.log, f)


def timed_game(n, v, l):
    init_time = time()
    game = War(n, verbose=v, logging=l)
    game.resolve_game()
    return time() - init_time


def timer_func():
    seed(1337)
    timer_dict = {}
    for i in range(4):
        timer_dict[i] = {'neither': [], 'verbose': [], 'logging': [], 'both   ': []}
        for n in range(100):
            timer_dict[i]['neither'].append(timed_game(i+1, False, False))
            timer_dict[i]['verbose'].append(timed_game(i+1, True, False))
            timer_dict[i]['logging'].append(timed_game(i+1, False, True))
            timer_dict[i]['both   '].append(timed_game(i+1, True, True))
    print('\n\n\n')
    print('+++++++++++++++++++++++++++')
    print('++++++++++RESULTS++++++++++')
    print('+++++++++++++++++++++++++++')
    print('\n\n')
    for players in timer_dict.keys():
        for parameters in ['neither', 'verbose', 'logging', 'both   ']:
            print(f'Players: {players+1} \t\tParamaters: {parameters} \t'
                  f'{round(sum(timer_dict[players][parameters]) / len(timer_dict[players][parameters]), 5)}')


if __name__ == '__main__':
    for _ in range(10):
        print(timed_game(4, False, True))
