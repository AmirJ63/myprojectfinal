import random
from collections import defaultdict
from itertools import product, cycle

from otree.api import *

c = cu

doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'cardgame'
    PLAYERS_PER_GROUP = 2
    NUM_TURNS = 3
    NUM_GAMES = 2
    NUM_ROUNDS = NUM_GAMES * NUM_TURNS
    REWARD = cu(10)
    DECK = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    NUM_CARDS_PER_PLAYER_f = 3
    NUM_CARDS_PER_PLAYER_uf = 2
    PLAYER_ROLES = ['kandinsky', 'klee']
    Quiz_correct_answers = (3, 3, 2, 4)
    CHART_TEMPLATE = __name__ + '/chart.html'




class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    game_num = models.IntegerField()
    unfair = models.BooleanField(initial=False)
    highest_card = models.IntegerField()
    random_taking1 = models.IntegerField()
    random_taking2 = models.IntegerField()


class Player(BasePlayer):
    card = models.IntegerField()
    unfair = models.BooleanField(initial=False)
    win_turn = models.BooleanField(initial=False)
    slider_max1 = models.IntegerField()
    slider_max2 = models.IntegerField()
    quiz1 = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, '3'],
            [2, '4'],
            [3, '8'],
        ],
        label=''
    )
    quiz2 = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'You 90 units-your coplayer 30 units'],
            [2, 'You 30 units-your coplayer 30 units '],
            [3, 'You 30 units-your coplayer 90 units'],
            [4, 'You 90 units-your coplayer 90 units.'],
        ],
        label=''
    )
    quiz3 = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'a or d'],
            [2, 'b or c '],
            [3, 'Only d'],
            [4, 'Only c'],
        ],
        label=''
    )
    quiz4 = models.IntegerField(
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'a or d'],
            [2, 'b or c '],
            [3, 'Only b'],
            [4, 'Only a'],
        ],
        label=''
    )
    taking_offer_1 = models.IntegerField(
        initial=0,
        min=0,
        label="How many units you want to take from your coplayer?",
    )
    taking_offer_2 = models.IntegerField(
        initial=0,
        min=0,
        label="How many units you want to take from your coplayer?",
    )


def taking_offer_1_max(player):
    other_player = [ p for p in player.get_others_in_group() ]
    for p in other_player:
        return p.participant.cardgame_payoff_1


def taking_offer_2_max(player):
    other_player = [ p for p in player.get_others_in_group() ]
    for p in other_player:
        return p.participant.cardgame_payoff_2




# Functions

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        import random
        players = subsession.get_players()
        for p in players:
            participant = p.participant
            # Card game to pay
            participant.cardgame_to_pay = random.choice([ 1, 2 ])
            participant.cardgame_score_1 = 0
            participant.cardgame_payoff_1 = cu(0)
            participant.cardgame_score_2 = 0
            participant.cardgame_payoff_2 = cu(0)
            participant.taking_payoff_1 = cu(0)
            participant.taking_payoff_2 = cu(0)
            participant.unfair = False
            participant.unfair1 = False
            participant.coplayer1=[]
            participant.coplayer2 = []
            participant.num_wins = 0
            participant.random_taking1 = 0





def set_groups(subsession: Subsession):
    from random import shuffle
    import math
    conditions = cycle([True, False])
    players = subsession.get_players()
    shuffle(players)
    round_number = subsession.round_number
    if round_number == 1:
        ps_klee = [p for p in players if p.participant.group == 'klee']
        ps_kandinsky = [p for p in players if p.participant.group == 'kandinsky']
        group_matrix = [list(pair) for pair in zip(ps_klee, ps_kandinsky)]

        for n, g in enumerate(group_matrix):
           if math.remainder(n, 4) == 0 or math.remainder(n, 4) == 1:
                condition = next(conditions)
                for p in g:
                    participant = p.participant
                    if condition and participant.group == 'klee':
                        participant.unfair = True
                    elif not condition and participant.group == 'kandinsky':
                        participant.unfair = True

    else:

        ps_unfair = [p for p in players if p.in_round(1).group.unfair]
        for p in ps_unfair:
            p.participant.unfair = False

        ps_fair = [p for p in players if not p.in_round(1).group.unfair]
        ps_klee = [p for p in ps_fair if p.participant.group == 'klee']
        ps_klee.reverse()
        ps_kandinsky = [p for p in ps_fair if p.participant.group == 'kandinsky']
        ps_fair = [list(pair) for pair in zip(ps_klee, ps_kandinsky)]

        for n, g in enumerate(ps_fair):
            condition = next(conditions)
            for p in g:
                participant = p.participant
                if condition and participant.group == 'klee':
                    participant.unfair = True
                elif not condition and participant.group == 'kandinsky':
                    participant.unfair = True

        group_matrix = [ps_unfair[n: n + 2] for n in range(0, len(ps_unfair), 2)] + ps_fair



    for s in subsession.in_rounds(subsession.round_number, subsession.round_number + C.NUM_TURNS - 1):
        s.set_group_matrix(group_matrix)
        for g in s.get_groups():
            ps = g.get_players()
            if any(p.participant.unfair for p in ps):
                print('p.participant.unfair', participant.unfair)
                g.unfair = True
            for p in ps:
                p.unfair = p.participant.unfair

def set_cards(group: Group):
    import random
    if group.unfair == True:
        num_cards_uf = 5
        deck_uf = random.sample(C.DECK, k=num_cards_uf)
        random.shuffle(deck_uf)
        for p in group.get_players():
            cards_uf = []
            if p.unfair:
                for n in range(C.NUM_CARDS_PER_PLAYER_uf):
                    cards_uf.append(deck_uf.pop())
                p.participant.vars['cards_in_deck_uf'] = cards_uf
            else:
                for n in range(C.NUM_CARDS_PER_PLAYER_f):
                    cards_uf.append(deck_uf.pop())
                p.participant.vars['cards_in_deck_uf'] = cards_uf
    elif group.unfair == False:
        num_cards_f = 6
        deck_f = random.sample(C.DECK, k=num_cards_f)
        random.shuffle(deck_f)
        for p in group.get_players():
            cards_f = []
            for n in range(C.NUM_CARDS_PER_PLAYER_f):
                cards_f.append(deck_f.pop())
            p.participant.vars['cards_in_deck_f'] = cards_f

def set_round_result(group:Group):
    import math
    round_number = group.round_number
    game_num = math.ceil(round_number / C.NUM_TURNS)
    group.game_num = game_num
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    if p1.card > p2.card:
        group.highest_card = p1.card
        p1.win_turn = True
        if game_num == 1:
            p1.participant.cardgame_score_1 += 1
            print('p1.participant.cardgame_score_1 ' ,p1.participant.cardgame_score_1)
        else:
            p1.participant.cardgame_score_2 += 1
            print('p1.participant.cardgame_score_2 ', p1.participant.cardgame_score_2)

    else:
        group.highest_card = p2.card
        p2.win_turn = True
        if game_num == 1:
            p2.participant.cardgame_score_1 += 1
            print('p2.participant.cardgame_score_1 ', p2.participant.cardgame_score_1)
        else:
            p2.participant.cardgame_score_2 += 1
            print('p2.participant.cardgame_score_2 ', p2.participant.cardgame_score_2)

def set_cardgame_results(group: Group):
    import math
    round_number = group.round_number
    game_num = math.ceil(round_number / C.NUM_TURNS)
    group.game_num = game_num
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    if game_num == 1:
        winner = max([ p1, p2 ], key=lambda x: x.participant.cardgame_score_1)
        winner.participant.cardgame_payoff_1 = 9 * C.REWARD
        loser = min([ p1, p2 ], key=lambda x: x.participant.cardgame_score_1)
        loser.participant.cardgame_payoff_1 = 3 * C.REWARD

    if game_num == 2:
        winner = max([p1, p2], key=lambda x: x.participant.cardgame_score_2)
        winner.participant.cardgame_payoff_2 = 9 * C.REWARD
        loser = min([p1, p2], key=lambda x: x.participant.cardgame_score_2)
        loser.participant.cardgame_payoff_2 = 3 * C.REWARD

def set_taking_results(group: Group):
    import random
    import math

    # pe is executive_taking_offer_player (the player whose offer is executive)
    # pe is selected rondomly among two players.
    # pe_not is the other player in each group
    players = [ p for p in group.get_players() ]
    pe = random.choice(players)
    pe_not_players = [ p for p in players if p.id_in_group != pe.id_in_group ]
    pe_not = random.choice(pe_not_players)
    round_number = group.round_number
    game_num = math.ceil(round_number / C.NUM_TURNS)
    group.game_num = game_num

    if game_num == 1:
        pe.participant.taking_payoff_1 = pe.participant.cardgame_payoff_1 + (pe.taking_offer_1 / 2)
        pe_not.participant.taking_payoff_1 = pe_not.participant.cardgame_payoff_1 - pe.taking_offer_1
        group.random_taking1 = pe.id_in_group
        pe.participant.random_taking1 = pe.id_in_group
    elif game_num == 2:
        pe.participant.taking_payoff_2 = pe.participant.cardgame_payoff_2 + (pe.taking_offer_2 / 2)
        pe_not.participant.taking_payoff_2 = pe_not.participant.cardgame_payoff_2 - pe.taking_offer_2
        group.random_taking2 = pe.id_in_group
def set_final_results(subsession: Subsession):
    if subsession.round_number == C.NUM_ROUNDS:
        players = [ p for p in subsession.get_players() ]
        for p in players:
            # we have two cadgames. participant.cardgame_to_pay selects which cardgame among these two is sleceted for payment.
            if p.participant.cardgame_to_pay == 1:
                p.participant.taking_payoff = p.participant.taking_payoff_1
            elif p.participant.cardgame_to_pay == 2:
                p.participant.taking_payoff = p.participant.taking_payoff_2

        for p in players:
            p.participant.payoff = p.participant.taking_payoff + p.participant.payoff_kk2




# Pages
class GroupingPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = set_groups

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 or player.round_number == 4


class WaitToInstruction(WaitPage):
    after_all_players_arrive = set_cards

class Instruction(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4']

    @staticmethod
    def get_form_fields(player: Player):
        group = player.group
        if player.round_number == 1:
            if group.unfair == False:
                return ['quiz1', 'quiz2','quiz3', ]
            else:
                return ['quiz1', 'quiz2', 'quiz4', ]


    @staticmethod
    def error_message(player: Player, values):
        print('Your answer is', values)
        if player.round_number ==1:
            for i in range(2):
                if values[f'quiz{i+1}'] != C.Quiz_correct_answers[i]:
                    return f'Your answer to quiz {i+1} is not true. Please read the instructions again carefully and answer the quiz correctly'
            if player.group.unfair == False:
                if values['quiz3'] != C.Quiz_correct_answers[2]:
                    return 'Your answer to quiz3 is not true. Please read the instructions again carefully and answer the quiz correctly'
            else:
                if values['quiz4'] != C.Quiz_correct_answers[3]:
                    return 'Your answer to quiz3 is not true. Please read the instructions again carefully and answer the quiz correctly'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 or player.round_number == 4

    @staticmethod
    def vars_for_template(player: Player):

        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        for p in player.get_others_in_group():
            others = p.participant
        return dict(game_number=game_number, others=others)



class WaitToPlay(WaitPage):
    wait_for_all_players = True


class PlayCards(Page):
    form_model = 'player'
    form_fields = [ 'card' ]

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        group = player.group
        participant.unfair1 = group.unfair
        for p in player.get_others_in_group():
            others = p.participant
        Round_Number = player.round_number - 3
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2

        if participant.unfair1 == True:
            participant.num_cards = participant.vars[ 'cards_in_deck_uf']
            len_uf = len(participant.vars[ 'cards_in_deck_uf'])
            others_uf = ['Not show' for p in range(len(others.vars['cards_in_deck_uf']))]
            return dict(
                cards_uf = participant.vars[ 'cards_in_deck_uf' ],
                others=others,
                others_uf=others_uf,
                len_uf = len_uf,
                Round_Number= Round_Number,
                game_number = game_number,
            )
        else:
            participant.num_cards = participant.vars['cards_in_deck_f']
            len_f = len(participant.vars['cards_in_deck_f'])
            others_uf = ['Not show' for p in range(len(others.vars['cards_in_deck_f']))]
            return dict(
                cards_f=participant.vars['cards_in_deck_f'],
                others=others,
                others_f = others_uf,
                len_f = len_f,
                Round_Number = Round_Number,
                game_number = game_number

            )

            ##cards_used=participant.vars['cards_used']

class Wait(WaitPage):
    wait_for_all_players = True
    after_all_players_arrive = set_round_result



class PlaycardsResult(Page):

    @staticmethod
    def vars_for_template(player: Player):
        your_chosen_card = player.card
        for p in player.get_others_in_group():
            others = p
        coparticipant_chosen_card = others.card
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        ##this is for game_number 2 that needs to minus 3 to show the round number in game 2
        Round_Number = player.round_number - 3
        return dict(
            your_chosen_card = your_chosen_card,
            coparticipant_chosen_card = coparticipant_chosen_card,
            game_number = game_number,
            Round_Number = Round_Number,
        )

class WaitToTaking(WaitPage):
    wait_for_all_players = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

    after_all_players_arrive = set_cardgame_results

class PlaycardsFinalresults(Page):
    @staticmethod
    def vars_for_template(player: Player):

        for p in player.get_others_in_group():
            others = p
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        ##this is for game_number 2 that needs to minus 3 to show the round number in game 2
        Round_Number = player.round_number - 3
        return dict(
            others = others,
            game_number=game_number,
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

class TakingInstructions(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        return dict(
            game_number = game_number,

        )


class Taking(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.round_number == 3:
            return [ 'taking_offer_1' ]
        elif player.round_number == 6:
            return [ 'taking_offer_2' ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

    @staticmethod
    def vars_for_template(player: Player):
        other_player = [p for p in player.get_others_in_group()]
        for p in other_player:
            player.slider_max1 = int(p.participant.cardgame_payoff_1)
            player.slider_max2 = int(p.participant.cardgame_payoff_2)
            if player.round_number==3:
                player.participant.coplayer1 = p.participant.id_in_session
            elif player.round_number==6:
                player.participant.coplayer2 = p.participant.id_in_session
            return dict(p=p, other_participant= p.participant.cardgame_payoff_2)

    @staticmethod
    def js_vars(player: Player):
        for p in player.get_others_in_group():
            max1 = p.participant.cardgame_payoff_1
            max2 = p.participant.cardgame_payoff_2
        return dict(max1=max1,
                    max2=max2,
                    payoff1=player.participant.cardgame_payoff_1,
                    payoff2=player.participant.cardgame_payoff_2,
                    round_number=player.round_number,
                    taking_offer_1=player.taking_offer_1,
                    )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        highcharts_series = []
        if 'taking_offer_1' in data:
            player.taking_offer_1 = int(data['taking_offer_1'])
            bin = int(data['taking_offer_1']/2)
            myself1 = int(data['myself1'])
            coplayer1 = int(data['coplayer1'])
            series = dict(data=[myself1, coplayer1, bin], type='line')
            return {0: dict(highcharts_series=highcharts_series)}

        if 'taking_offer_2' in data:
            player.taking_offer_2 = int(data['taking_offer_2'])



class WaitTurnResults(WaitPage):
    after_all_players_arrive = set_taking_results

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6


class WaitGameResults(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = set_final_results

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class GameResults(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        for p in player.get_others_in_group():
            others = p
        return dict(game_number=game_number, others=others)

class InstructionTask34(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 or player.round_number == 4

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number <= 3:
            game_number = 1
        elif player.round_number >= 4:
            game_number = 2
        for p in player.get_others_in_group():
            others = p.participant
        return dict(game_number=game_number, others=others)


page_sequence = [ GroupingPage, WaitToInstruction, InstructionTask34, Instruction, WaitToPlay, PlayCards, Wait, PlaycardsResult, WaitToTaking, PlaycardsFinalresults, TakingInstructions, Taking, WaitTurnResults,
                  WaitGameResults, GameResults ]
