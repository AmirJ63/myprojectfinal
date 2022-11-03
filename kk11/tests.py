from otree.api import Currency as cu, currency_range, expect, Bot, Submission
from . import *
from random import randint


class PlayerBot(Bot):

    def play_round(self):
        import random
        a = random.choice([-5, -3, -1, 1, 3, 5])
        if self.player.round_number == 1:
            yield GeneralInstructions
            yield TaskOneInstructions

        yield Submission(Paintings, dict(vote=a), check_html=False)

        if self.player.round_number == C.NUM_ROUNDS:
            yield Results
