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
    NUM_CARDS_PER_PLAYER = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    game_num = models.IntegerField()
    highest_card = models.IntegerField()



class Player(BasePlayer):
    card = models.IntegerField()
    win_turn = models.BooleanField(initial=False)



#Functions

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        import random
        players = subsession.get_players()
        for p in players:
            participant = p.participant
            # Card game to pay
            participant.cardgame_to_pay = random.choice([1, 2])
            print ('participant.cardgame_to_pay', participant.cardgame_to_pay)
            participant.cardgame_score_1 = 0
            participant.cardgame_payoff_1 = cu(0)
            participant.cardgame_score_2 = 0
            participant.cardgame_payoff_2 = cu(0)


def set_groups(subsession: Subsession):
    from random import shuffle

    players = subsession.get_players()
    shuffle(players)

    ps_klee = [p for p in players if p.participant.group == 'klee']
    ps_kandinsky = [p for p in players if p.participant.group == 'kandinsky']
    shuffle(ps_klee)
    shuffle(ps_kandinsky)
    group_matrix = [list(pair) for pair in zip(ps_klee, ps_kandinsky)]

    for s in subsession.in_rounds(subsession.round_number, subsession.round_number + C.NUM_TURNS - 1):
        s.set_group_matrix(group_matrix)


def set_cards(group: Group):
    import random
    num_cards = C.NUM_CARDS_PER_PLAYER * C.PLAYERS_PER_GROUP
    deck = random.sample(C.DECK, k=num_cards)
    for p in group.get_players():
        cards = []
        for n in range(C.NUM_CARDS_PER_PLAYER):
            cards.append(deck.pop())
        p.participant.vars['cards_in_deck'] = cards


def set_game_results(group: Group):
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
            winner = max([p1, p2], key=lambda x: x.participant.cardgame_score_1)
            winner.participant.cardgame_payoff_1 = 9 * C.REWARD
            loser = min([p1, p2], key=lambda x: x.participant.cardgame_score_1)
            loser.participant.cardgame_payoff_1 = 3 * C.REWARD
        else:
            winner = max([p1, p2], key=lambda x: x.participant.cardgame_score_2)
            winner.participant.cardgame_payoff_2 = 9 * C.REWARD
            loser = min([p1, p2], key=lambda x: x.participant.cardgame_score_2)
            loser.participant.cardgame_payoff_1 = 3 * C.REWARD

    players = [p for p in group.get_players()]
    for p in players:
        if p.participant.cardgame_to_pay == 1:
            p.participant.payoff_cardgame = p.participant.cardgame_payoff_1
        elif p.participant.cardgame_to_pay == 2:
            p.participant.payoff_cardgame = p.participant.cardgame_payoff_2

def set_card_game_turn(player):
    pass



#Pages
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
    form_fields = ['card']

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        return dict(
            cards=participant.vars['cards_in_deck'],
            ##cards_used=participant.vars['cards_used']
        )

class Taking(Page):
    def is_displayed(player: Player):
        return player.round_number == 3 or player.round_number == 6

class WaitTurnResults(WaitPage):
    wait_for_all_players = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 6

    after_all_players_arrive = set_game_results

class GameResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [Instruction, GroupingPage, WaitToPlay, PlayCards, Taking, WaitTurnResults, GameResults  ]
