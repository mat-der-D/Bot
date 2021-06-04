import random
from typing import Optional


# *****************************************************************
#  For Card
# *****************************************************************
class Card:
    def __init__(self, number: int):
        if not (isinstance(number, int) and 1 <= number <= 13):
            raise ValueError
        self.number = number

    def __str__(self):
        return "0 A 2 3 4 5 6 7 8 9 10 J Q K".split()[self.number]

    def __repr__(self):
        return f"Card({self.__str__()})"

    def __eq__(self, other):
        if not isinstance(other, Card):
            raise NotImplemented
        return self.number == other.number

    def __gt__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplemented
        if self.number == 1:
            return other.number in (11, 12, 13)
        if other.number == 1:
            return 2 <= self.number <= 10
        return self.number > other.number

    def __lt__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplemented
        return other > self

    def __le__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplemented
        return not (self > other)

    def __ge__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplemented
        return not (other > self)


# *****************************************************************
#  For Deck
# *****************************************************************
class DeckRunsOutError(IndexError):
    pass


class Deck(list):
    def __init__(self):
        super().__init__(Card(n) for n in range(1, 14))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self)

    def draw(self):
        try:
            return self.pop()
        except IndexError:
            raise DeckRunsOutError


# *****************************************************************
#  For Game
# *****************************************************************
class GameNotFinishedError(Exception):
    pass


class Turn:
    def __init__(self, num_player: int):
        self.num_player = num_player
        self.count = 1
        self.player = 0

    def advance(self):
        self.player = (self.player + 1) % self.num_player
        if self.player == 0:
            self.count += 1


class SinglePoker:
    def __init__(self, max_turn: int):
        if not (isinstance(max_turn, int) and max_turn >= 0):
            raise ValueError(max_turn)
        self.max_turn = max_turn
        self.deck = Deck()
        self.trash = []
        self.turn = Turn(2)
        # --- Deal ---
        self.hands = [self.deck.draw(), self.deck.draw()]

    @property
    def winner(self) -> int:
        if self.turn.count <= self.max_turn:
            raise GameNotFinishedError
        if self.hands[0] > self.hands[1]:
            return 0
        else:
            return 1

    @property
    def num_cards_in_deck(self) -> int:
        return len(self.deck)

    def replace_hand(self, player: Optional[int] = None):
        if player is None:
            player = self.turn.player

        new_card = self.deck.draw()  # raise DeckRunsOutError if no card leaves
        self.trash.append(self.hands[player])
        self.hands[player] = new_card

    def advance_turn(self):
        self.turn.advance()


# *****************************************************************
#  Others
# *****************************************************************
class SampleGame:
    def __init__(self, max_turn):
        self.master = SinglePoker(max_turn)
        self.name_list = ("CPU", "You")

    def play(self):
        self.cpu_turn()
        self.advance_turn()
        self.your_turn()
        self.advance_turn()

        try:
            winner = self.master.winner
        except GameNotFinishedError:
            self.play()  # Next Turn
        else:
            self.show_result(winner)

    def cpu_turn(self):
        if random.randint(0, 1):
            self.replace_hand()

    def your_turn(self):
        self.show_status()
        while True:
            y_or_n = input("Do you change your hand?(Y/n):").lower()
            if y_or_n not in ("y", "n"):
                print("Please input Y or n.")
            else:
                change_hand = y_or_n == "y"
                break

        if change_hand:
            self.replace_hand()

    def advance_turn(self):
        self.master.advance_turn()

    def show_status(self):
        print("Deck: {} card(s) left")
        print("Trash:", self.master.trash)
        print("Your Hand:", self.master.hands[1])

    def show_result(self, winner: int):
        print("*** RESULT ***")
        print("CPU's Hand:", self.master.hands[0])
        print("Your Hand:", self.master.hands[1])
        print(f"{self.name_list[winner]} won!")

    def replace_hand(self, player: int = None):
        try:
            self.master.replace_hand(player)
        except DeckRunsOutError:
            print(f"{self.name_list[player]} failed to change the hand.")


if __name__ == "__main__":
    game = SampleGame(5)
    game.play()
