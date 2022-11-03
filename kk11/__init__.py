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
    NUM_PAINTINGS = 1
    NUM_ROUNDS = NUM_PAINTINGS


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    import random
    rand = models.IntegerField()
    klee_difference = models.IntegerField()

    vote = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        label=""
        )
def vote_choices(player):
    import random
    player.rand = random.randint(1, 2)
    if player.rand == 1:
         choices=[
            [5, 'strongly prefer A'],
            [3, 'prefer A'],
            [1, 'slightly prefer A'],
            [-1, 'slightly prefer B'],
            [-3, 'prefer B'],
            [-5, 'strongly prefer B'],
         ]
         return choices

    if player.rand == 2:
        choices = [[-5, 'strongly prefer A'],
                   [-3, 'prefer A'],
                   [-1, 'slightly prefer A'],
                   [1, 'slightly prefer B'],
                   [3, 'prefer B'],
                   [5, 'strongly prefer B'],
                   ]
        return choices
# Functions
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.vars['scores'] = []


def set_score(player:Player):
    participant = player.participant
    player.klee_difference = player.vote
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
class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class InstructionsII(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class InstructionsIII(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class TaskOneInstructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Paintings(Page):

    form_model = 'player'
    form_fields = ['vote']

    @staticmethod
    def vars_for_template(player: Player):
        import random
        print('player.id_in_group',player.id_in_group, 'player.rand',player.rand)

        return dict(
            klee_img=f'first5paintings/klee{player.round_number}.jpg',
            kandinsky_img=f'first5paintings/kandinsky{player.round_number}.jpg',
            rand=player.rand,
        )

    @staticmethod
    def error_message(player: Player, values):
        print('values is', values)
        if values['vote'] == None:
            return 'You should choose one of the options'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_score(player)
        print('player.vote=', player.vote)


class WaitingResults(WaitPage):
    wait_for_all_groups = True

    after_all_players_arrive = set_minimal_groups

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class Task1complete(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS




page_sequence = [Instructions, InstructionsII, InstructionsIII, TaskOneInstructions, Paintings, WaitingResults, Task1complete]
