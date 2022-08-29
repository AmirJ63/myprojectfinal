import pathlib
##for this program, I need to make better appearance of pages specially the decisionklee and ecisionkandinsky pages.
from otree.api import *
from otree.models import subsession
from random import shuffle

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'kk2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS =2
    TRUE_PAINTINGS = [3, 5]
    REWARDS = cu(10)



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    klee_quiz = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5 ],
        initial=0,
        label="we choose:"
    )
    kandinsky_quiz = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5 ],
        initial=0,
        label="we choose:"
    )


# Functions
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.vars[ 'payoff' ] = [ ]


def set_payoff(player: Player):
    participant = player.participant
    if player.klee_quiz == C.TRUE_PAINTINGS[player.round_number-1]:
        participant.vars[ 'payoff' ].append(C.REWARDS)
    elif player.kandinsky_quiz == C.TRUE_PAINTINGS[player.round_number-1]:
        participant.vars[ 'payoff' ].append(C.REWARDS)

    if player.round_number == C.NUM_ROUNDS:
        participant.payoff = sum(participant.vars[ 'payoff' ])



##PAGES

class DecisionKlee(Page):
    form_model = 'player'
    form_fields = [ 'klee_quiz']

    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'klee'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoff(player)

class DecisionKandinsky(Page):
    form_model = 'player'
    form_fields = [ 'kandinsky_quiz' ]

    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'kandinsky'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoff(player)

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS



page_sequence = [DecisionKlee, DecisionKandinsky, Results]
