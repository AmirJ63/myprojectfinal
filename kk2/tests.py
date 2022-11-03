from otree.api import Currency as cu, currency_range, expect, Bot, Submission
from . import *
from random import randint

class PlayerBot(Bot):

    def play_round(self):
        e = randint(1, 5)
        f = randint(1, 5)

        if self.player.round_number == 1:
            if self.participant.group == 'klee':
                yield GuideKlee
                if self.participant.klee_quiz == True:
                    yield DecisionKlee, dict(klee_quiz=e)
            elif self.participant.group == 'kandinsky':
                yield GuideKandinsky
                if self.participant.kandinsky_quiz == True:
                    yield DecisionKandinsky, dict(kandinsky_quiz=f)
