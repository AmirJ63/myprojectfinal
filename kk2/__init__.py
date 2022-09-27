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
    NUM_ROUNDS = 2
    TRUE_PAINTINGS = [3, 5]
    REWARDS = cu(10)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    max_payoff_klee = models.CurrencyField()
    max_payoff_kandinsky = models.CurrencyField()


class Player(BasePlayer):
    klee_quiz = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'painting 1'],
            [2, 'painting 2'],
            [3, 'painting 3'],
            [4, 'painting 4'],
            [5, 'painting 5'],
        ],
        initial=0,
        label="we choose:"
    )
    kandinsky_quiz = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5],
        initial=0,
        label="we choose:"
    )


class Message(ExtraModel):
    group = models.Link(Group)
    sender = models.Link(Player)
    text = models.StringField()


# Functions

def to_dict(msg: Message):
    return dict(sender=msg.sender.id_in_group, text=msg.text)


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.vars['payoff'] = []
            p.participant.klee_quiz = False
            p.participant.kandinsky_quiz = False


def set_spokesperson(group: Group):
    import random
    from random import shuffle
    players = group.get_players()

    ps_klee = [p for p in players if p.participant.group == 'klee']
    shuffle(ps_klee)
    ps_kandinsky = [p for p in players if p.participant.group == 'kandinsky']
    shuffle(ps_kandinsky)
    # sp is spokesperson
    sp_klee_1 = random.choice(ps_klee)
    sp_kandinsky_1 = random.choice(ps_kandinsky)
    shuffle(ps_klee)
    shuffle(ps_kandinsky)
    sp_klee_2 = random.choice(ps_klee)
    sp_kandinsky_2 = random.choice(ps_kandinsky)

    for p in players:
        if p.round_number == 1:
            p.participant.klee_quiz = False
            p.participant.kandinsky_quiz = False
            sp_klee_1.participant.klee_quiz = True
            sp_kandinsky_1.participant.kandinsky_quiz = True

        elif p.round_number == 2:
            p.participant.klee_quiz = False
            p.participant.kandinsky_quiz = False
            sp_klee_2.participant.klee_quiz = True
            sp_kandinsky_2.participant.kandinsky_quiz = True


# def set_formfield_answers(group: Group):
# players = group.get_players()
# for p in players:


def set_payoff(player: Player):
    participant = player.participant
    if player.klee_quiz == C.TRUE_PAINTINGS[player.round_number - 1]:
        participant.vars['payoff'].append(C.REWARDS)
    elif player.kandinsky_quiz == C.TRUE_PAINTINGS[player.round_number - 1]:
        participant.vars['payoff'].append(C.REWARDS)

    if player.round_number == C.NUM_ROUNDS:
        participant.payoff_kk2 = sum(participant.vars['payoff'])


def set_payoff_group(group: Group):
    players = group.get_players()
    ps_klee = [p for p in players if p.participant.group == 'klee']
    ps_kandinsky = [p for p in players if p.participant.group == 'kandinsky']

    group.max_payoff_klee = 0
    group.max_payoff_kandinsky = 0

    for p in ps_klee:
        if p.participant.payoff_kk2 >= group.max_payoff_klee:
            group.max_payoff_klee = p.participant.payoff_kk2
    for p in ps_klee:
        p.participant.payoff_kk2 = group.max_payoff_klee

    for p in ps_kandinsky:
        if p.participant.payoff_kk2 >= group.max_payoff_kandinsky:
            group.max_payoff_kandinsky = p.participant.payoff_kk2

    for p in ps_kandinsky:
        p.participant.payoff_kk2 = group.max_payoff_kandinsky


##PAGES
class GuideKlee(Page):
    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'klee' and player.round_number == 1


class GuideKandinsky(Page):
    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'kandinsky' and player.round_number == 1


class WaitePage(WaitPage):
    after_all_players_arrive = set_spokesperson


class DecisionKlee(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.participant.klee_quiz == True:
            return ['klee_quiz']

    timeout_seconds = None

    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'klee'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoff(player)

    @staticmethod
    def js_vars(player: Player):
        return dict(my_id=player.id_in_group)

    @staticmethod
    def live_method(player: Player, data):
        my_id = player.id_in_group
        group = player.group
        if 'text' in data:
            text = data['text']
            msg = Message.create(group=group, sender=player, text=text)
            return {0: [to_dict(msg)]}
        return {my_id: [to_dict(msg) for msg in Message.filter(group=group)]}


class DecisionKandinsky(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.participant.kandinsky_quiz == True:
            return ['kandinsky_quiz']

    timeout_seconds = 180

    @staticmethod
    def is_displayed(player: Player):
        participant = player.participant
        return participant.group == 'kandinsky'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_payoff(player)

    @staticmethod
    def js_vars(player: Player):
        return dict(my_id=player.id_in_group)

    @staticmethod
    def live_method(player: Player, data):
        my_id = player.id_in_group
        group = player.group
        if 'text' in data:
            text = data['text']
            msg = Message.create(group=group, sender=player, text=text)
            return {0: [to_dict(msg)]}
        return {my_id: [to_dict(msg) for msg in Message.filter(group=group)]}


class WaitToResults(WaitPage):
    after_all_players_arrive = set_payoff_group

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [GuideKlee, GuideKandinsky, WaitePage, DecisionKlee, DecisionKandinsky, WaitToResults]
