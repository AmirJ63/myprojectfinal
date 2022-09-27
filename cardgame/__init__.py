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



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    game_num = models.IntegerField()
    highest_card = models.IntegerField()


class Player(BasePlayer):
    card = models.IntegerField()
    win_turn = models.BooleanField(initial=False)
    slider_max1 = models.IntegerField()
    slider_max2 = models.IntegerField()
    taking_offer_1 = models.IntegerField(
        min=0,
        label="How many units you want to take from your coplayer?",
    )
    taking_offer_2 = models.IntegerField(
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


def set_groups(subsession: Subsession):
    from random import shuffle
    players = subsession.get_players()

    ps_klee = [ p for p in players if p.participant.group == 'klee' ]
    shuffle(ps_klee)
    ps_kandinsky = [ p for p in players if p.participant.group == 'kandinsky' ]
    shuffle(ps_kandinsky)
    group_matrix = [ list(pair) for pair in zip(ps_klee, ps_kandinsky) ]

    for s in subsession.in_rounds(subsession.round_number, subsession.round_number + C.NUM_TURNS - 1):
        s.set_group_matrix(group_matrix)


def set_cards(group: Group):
    import random
    num_cards_f = C.NUM_CARDS_PER_PLAYER_f * C.PLAYERS_PER_GROUP
    deck_f = random.sample(C.DECK, k=num_cards_f)
    random.shuffle(deck_f)
    for p in group.get_players():
        cards_f = [ ]
        for n in range(C.NUM_CARDS_PER_PLAYER_f):
            cards_f.append(deck_f.pop())
        p.participant.vars[ 'cards_in_deck_f' ] = cards_f

    num_cards_uf = 5
    deck_uf = random.sample(C.DECK, k=num_cards_uf)
    random.shuffle(deck_uf)
    for p in group.get_players():
        cards_uf = [ ]
        if p.participant.group == 'klee':
            for n in range(C.NUM_CARDS_PER_PLAYER_uf):
                cards_uf.append(deck_uf.pop())
            p.participant.vars[ 'cards_in_deck_uf' ] = cards_uf
        else:
            for n in range(C.NUM_CARDS_PER_PLAYER_f):
                cards_uf.append(deck_uf.pop())
            p.participant.vars[ 'cards_in_deck_uf' ] = cards_uf


def set_cardgame_results(group: Group):
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
        else:
            p1.participant.cardgame_score_2 += 1
    else:
        group.highest_card = p2.card
        p2.win_turn = True
        if game_num == 1:
            p2.participant.cardgame_score_1 += 1
        else:
            p2.participant.cardgame_score_2 += 1

    if game_num == 1:
        winner = max([ p1, p2 ], key=lambda x: x.participant.cardgame_score_1)
        winner.participant.cardgame_payoff_1 = 9 * C.REWARD
        loser = min([ p1, p2 ], key=lambda x: x.participant.cardgame_score_1)
        loser.participant.cardgame_payoff_1 = 3 * C.REWARD
    else:
        winner = max([ p1, p2 ], key=lambda x: x.participant.cardgame_score_2)
        winner.participant.cardgame_payoff_2 = 9 * C.REWARD
        loser = min([ p1, p2 ], key=lambda x: x.participant.cardgame_score_2)
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
        pe.participant.taking_payoff_1 = pe.participant.cardgame_payoff_1 + int(pe.taking_offer_1 / 2)
        pe_not.participant.taking_payoff_1 = pe_not.participant.cardgame_payoff_1 - pe.taking_offer_1

    else:
        pe.participant.taking_payoff_2 = pe.participant.cardgame_payoff_2 + int(pe.taking_offer_2 / 2)
        pe_not.participant.taking_payoff_2 = pe_not.participant.cardgame_payoff_2 - pe.taking_offer_2



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

def set_number_mydeck_cards(player):
    pass


# Pages
class Instruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class GroupingPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = set_groups

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 or player.round_number == 4


class WaitToPlay(WaitPage):
    after_all_players_arrive = set_cards


class PlayCards(Page):
    form_model = 'player'
    form_fields = [ 'card' ]

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            cards_f=participant.vars[ 'cards_in_deck_f' ],
            cards_uf = participant.vars[ 'cards_in_deck_uf' ],
            ##cards_used=participant.vars['cards_used']
        )


class WaitToTaking(WaitPage):
    wait_for_all_players = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

    after_all_players_arrive = set_cardgame_results


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
        other_player = [ p for p in player.get_others_in_group() ]
        for p in other_player:
            player.slider_max1 = int(p.participant.cardgame_payoff_1)
            player.slider_max2 = int(p.participant.cardgame_payoff_2)
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
                    round_number=player.round_number
                    )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        if 'taking_offer_1' in data:
            player.taking_offer_1 = int(data['taking_offer_1'])

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



page_sequence = [ Instruction, GroupingPage, WaitToPlay, PlayCards, WaitToTaking, Taking, WaitTurnResults,
                  WaitGameResults, GameResults ]
