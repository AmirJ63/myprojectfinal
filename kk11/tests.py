from otree.api import Currency as cu, currency_range, expect, Bot, Submission
from . import *
from random import randint


class PlayerBot(Bot):

    def play_round(self):
        a = randint(0, 5)
        b = 5 - a
        yield Paintings, dict(klee=a, kandinsky=b)
        if self.player.round_number == C.NUM_ROUNDS:
            yield Results
