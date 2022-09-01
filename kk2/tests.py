from otree.api import Currency as cu, currency_range, expect, Bot, Submission
from . import *
from random import randint

class PlayerBot(Bot):

    def play_round(self):
        e = randint(1, 5)
        f= randint(1,5)
        if self.participant.group == 'klee':
            yield DecisionKlee, dict(klee_quiz=e)
            if self.player.round_number==1:
                yield GuideKlee
        elif self.participant.group == 'kandinsky':
            yield DecisionKandinsky, dict(kandinsky_quiz=f)
            if self.player.round_number == 1:
                yield  GuideKandinsky


        if self.player.round_number == C.NUM_ROUNDS:
            yield Results

