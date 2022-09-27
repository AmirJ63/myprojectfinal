from random import randint

from . import *


class PlayerBot(Bot):

    def play_round(self):
        a = randint(1, 10)
        b = randint(0, 30)
        e = randint(0, 30)

        if self.player.round_number == 1:
            yield Instruction

        yield Submission(PlayCards, dict(card=a), check_html=False)

        if self.player.round_number == 3:
            yield Submission(Taking, dict(taking_offer_1=b), check_html=False)
        elif self.player.round_number == 6:
            yield Submission(Taking, dict(taking_offer_2=e), check_html=False)

        if self.player.round_number == C.NUM_ROUNDS:
            yield Submission(GameResults,check_html=False)

