import pathlib

from otree.api import *
from otree.models import subsession
from random import shuffle

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'kk11'
    PLAYERS_PER_GROUP = None
    NUM_PAINTINGS = 5
    NUM_ROUNDS = NUM_PAINTINGS


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    klee_difference = models.IntegerField()

    klee = models.IntegerField(
            widget=widgets.RadioSelectHorizontal,
            choices=[0, 1, 2, 3, 4, 5],
            label="I like:"
        )
    kandinsky = models.IntegerField(
            widget=widgets.RadioSelectHorizontal,
            choices=[0, 1, 2, 3, 4, 5],
            label="I like:"
    )


# Functions
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.vars['scores'] = []


def set_score(player:Player):
    participant = player.participant
    player.klee_difference = player.klee - player.kandinsky
    participant.vars['scores'].append(player.klee_difference)
    if player.round_number == C.NUM_ROUNDS:
        participant.score = sum(participant.vars['scores'])


def set_minimal_groups(subsession: Subsession):
    session = subsession.session
    participants = [p.participant for p in subsession.get_players()]
    shuffle(participants)

    ranks = sorted(participants, key=lambda x: x.score)
    session.scores = [p.score for p in ranks]
    median = len(ranks) / 2
    for n, p in enumerate(ranks):
        if n < median:
            p.group = 'kandinsky'
        else:
            p.group = 'klee'


##PAGES
class Paintings(Page):
    form_model = 'player'
    form_fields = ['klee', 'kandinsky']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            klee_img=f'first5paintings/klee{player.round_number}.jpg',
            kandinsky_img=f'first5paintings/kandinsky{player.round_number}.jpg'
        )

    @staticmethod
    def error_message(player: Player, values):
        print('values is', values)
        if values['klee'] + values['kandinsky'] != 5:
            return 'The numbers must add up to 5'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_score(player)


class WaitingResults(WaitPage):
    wait_for_all_groups = True

    after_all_players_arrive = set_minimal_groups

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Paintings, WaitingResults, Results]
