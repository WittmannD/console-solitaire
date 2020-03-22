from __future__ import print_function
import random
import time
import re
import os

EMPTY_SYMBOL = ' '
CARD_HEIGHT = 5
CARD_WIDTH = 8
COUNT_OF_CARD_ROWS = 7
DEFAULT_DEQUE = ['2'] * 4 + ['3'] * 4 + ['4'] * 4 + ['5'] * 4 + ['6'] * 4 + ['7'] * 4 + ['8'] * 4 + ['9'] * 4 + \
                ['10'] * 4 + ['V'] * 4 + ['D'] * 4 + ['K'] * 4 + ['T'] * 4
VALUES_TABLE = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'V': 11,
    'D': 12,
    'K': 13,
    'T': 1
}


class Card:
    """Class of card"""
    def __init__(self, value, index='0.0', reverse=True):
        """

        :param str value: Cost value of card
        :param str index: Index of a card on a game board
        :param bool reverse: The card is turned upside down or not
        """
        self.value = value
        self.reverse = reverse
        self.index = index
        self.passed = False

    @property
    def entity(self):
        return

    @entity.getter
    def entity(self):
        """

        :return: list[str]. Kind of the card on the game board
        """

        if self.passed:
            return [
                EMPTY_SYMBOL * CARD_WIDTH,
                EMPTY_SYMBOL * CARD_WIDTH,
                EMPTY_SYMBOL * CARD_WIDTH,
                EMPTY_SYMBOL * CARD_WIDTH,
                EMPTY_SYMBOL * CARD_WIDTH,
            ]
        elif self.reverse:
            return [
                '########',
                '########',
                '########',
                '########',
                '########'
            ]
        else:
            return [
                '########',
                '#{0:<6}#'.format(self.value),
                '#      #',
                '#      #',
                '{0:#^{1}}'.format(self.index, CARD_WIDTH)
            ]


class CardDeck:
    """Class of card deck"""
    def __init__(self):
        self.queue = []
        self.current = None

    def generate(self):
        """
        Generate new queue of cards
        :return: self
        """
        card_values = DEFAULT_DEQUE.copy()
        random.shuffle(card_values)

        for card_value in card_values:
            self.queue.append(Card(card_value))

        self.roll()
        return self

    def roll(self):
        """
        Method for card deck scrolling. Method sets the 'current' attribute value
        """
        if self.current is not None and not self.current.passed:
            self.current.reverse = True
            self.queue = [self.current] + self.queue
        self.current = self.queue.pop()
        self.current.reverse = False

    @property
    def entity(self):
        return

    @entity.getter
    def entity(self):
        """

        :return: list[str]. Kind of the card deck on the game board
        """
        current_card_entity = self.current.entity
        return [
            '######## ' + current_card_entity[0],
            '######## ' + current_card_entity[1],
            '{0:#^{1}} '.format(len(self.queue), CARD_WIDTH) + current_card_entity[2],
            '######## ' + current_card_entity[3],
            '######## ' + current_card_entity[4]
        ]


class Board:
    """Class of the game board"""
    def __init__(self):
        self.cards = []

    def generate(self, dequeue):
        """
        Generate a new set of cards on the game board
        :param list dequeue: queue of cards
        :return: self
        """
        self.cards = []
        for i in range(COUNT_OF_CARD_ROWS):
            self.cards.append([])

            for j in range(i + 1):
                card = dequeue.pop()
                card.index = '{0}.{1}'.format(i + 1, j + 1)
                self.cards[i].append(card)

        return self

    def update(self):
        """
        Update state of game board
        """
        for i in range(len(self.cards)):
            for j in range(len(self.cards[i])):
                if (
                    len(self.cards) < i + 2 or
                    (self.cards[i + 1][j].passed and
                     self.cards[i + 1][j + 1].passed)
                ):
                    self.cards[i][j].reverse = False


class Game:
    """The main class. Implementation of game logic"""
    def __init__(self):
        self.dequeue = CardDeck().generate()
        self.board = Board().generate(self.dequeue.queue)

    def restart(self):
        """Game restart"""
        self.dequeue = CardDeck().generate()
        self.board = Board().generate(self.dequeue.queue)

    def draw(self):
        """Draw game board to console"""
        dequeue_entity = self.dequeue.entity
        rows_count = COUNT_OF_CARD_ROWS

        for j in range(rows_count):
            cards = self.board.cards[j]

            for i in range(CARD_HEIGHT):
                gap = EMPTY_SYMBOL * 2
                dequeue_row = dequeue_entity[i] if j == 0 else ''
                cards_row = gap.join([card.entity[i] for card in cards])

                print(
                    '{0:{1}<20}{2:{1}^{3}}'.format(
                        dequeue_row,
                        EMPTY_SYMBOL,
                        cards_row,
                        (CARD_WIDTH + len(gap)) * rows_count
                    )
                )

    def win_check(self):
        """
        Win check
        :return: True | False
        """
        if not self.board.cards[0][0].passed:
            return False
        return True

    @staticmethod
    def winner_screen():
        """Draw message for winner to console"""
        with open('winner_screen', 'r') as file:
            rows = file.readlines()

        for row in rows:
            row = row.replace(' ', EMPTY_SYMBOL)
            for symbol in row:
                print(symbol, end='')
            time.sleep(0.1)

    @staticmethod
    def rules():
        """Draw rules for player to console"""
        with open('rules', 'r') as file:
            rows = file.readlines()

        for row in rows:
            for symbol in row:
                print(symbol, end='')
        print()
        input()

    @staticmethod
    def card_sum(card1, card2):
        """Add two cards. If sum equal 13, hide both cards"""
        if (
            not card1.reverse and
            not card2.reverse and
            not card1.passed and
            not card2.passed and
            (
                VALUES_TABLE[card1.value] + VALUES_TABLE[card2.value] == 13 or
                (VALUES_TABLE[card1.value] == 13 and VALUES_TABLE[card2.value] == 13)
            )
        ):
            card1.passed = True
            card2.passed = True

    def run(self):
        """Run the game loop"""
        cheating = False
        while not self.win_check() and not cheating:
            os.system('cls')
            print('\r')
            self.board.update()
            self.draw()

            while True:
                command = input('>>> ')
                card_n_card = re.match(r"(\d+)\.(\d+) (\d+)\.(\d+)", command)

                if command == '':
                    self.dequeue.roll()
                    break

                if command == 'winnow':
                    cheating = True
                    break

                if command == 'restart':
                    self.restart()
                    break

                if command == 'exit':
                    exit(1)

                if command == 'rules':
                    self.rules()
                    break

                if card_n_card is not None:
                    indexes = list(map(lambda x: int(x), card_n_card.groups()))
                    card1 = None
                    card2 = None

                    if indexes[0] == 0 and indexes[1] == 0:
                        card1 = self.dequeue.current

                    if indexes[2] == 0 and indexes[3] == 0:
                        card2 = self.dequeue.current

                    if (
                        0 < indexes[0] <= len(self.board.cards) and
                        0 < indexes[1] <= len(self.board.cards[indexes[0] - 1])
                    ):
                        card1 = self.board.cards[indexes[0] - 1][indexes[1] - 1]

                    if (
                        0 < indexes[2] <= len(self.board.cards) and
                        0 < indexes[3] <= len(self.board.cards[indexes[2] - 1])
                    ):
                        card2 = self.board.cards[indexes[2] - 1][indexes[3] - 1]

                    if card1 is not None and card2 is not None:
                        self.card_sum(card1, card2)
                        break

        self.winner_screen()
        print('Press enter for new game')
        input()
        self.restart()
        self.run()

    def start(self):
        """Game start"""
        self.rules()
        self.run()


if __name__ == '__main__':
    game = Game()
    game.start()
