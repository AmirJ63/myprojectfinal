from otree.api import *

c = cu

doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'cardgame'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    REWARD = cu(100)
    ROLE_KLEE = 'klee'
    ROLE_KANDINSKY = 'kandinsky'
    DECK = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    session = subsession.session
    import random
    players = subsession.get_players()
    for p in players:
        if p.round_number == 1:
            participant = p.participant
            participant.cardgame_round_to_pay = random.randint(1,
                                                               C.NUM_ROUNDS)  # the random should be between the result after first taking and second taking.
            participant.dropout = False
            participant.unmatched = False


def set_groups(subsession: Subsession):
    session = subsession.session
    import random
    session = subsession.session
    from random import shuffle

    players = session.get_players()
    active_players = [ p for p in players if not (p.participant.dropout or p.participant.unmatched) ]
    inactive = [ p for p in players if p.participant.dropout or p.participant.unmatched ]
    shuffle(active_players)

    n, r = divmod(len(active_players), C.PLAYERS_PER_GROUP)

    while r:
        p = active_players.pop()
        p.participant.unmatched = True
        inactive.append(p)
        r -= 1
    for p in active_players:
        participant = p.participant
        participant.role = random.randint(C.ROLE_KLEE, C.ROLE_KANDINSKY)
    # when I want to add this app after kk11, the coding should be like the following code:
    # if participant.group = 'klee':
    # participant.role = C.ROLE_KLEE
    # else:
    # participant.role = C.ROLE_KANDINSKY
    group_klee = [ ]
    group_kandinsky = [ ]
    for p in active_players:
        if participant.role == 'klee':
            group_klee.append(p)
        else:
            group_kandinsky.append(p)
    shuffle(group_klee)
    shuffle(group_kandinsky)
    group_matrix = [ [ group_klee[ n ], group_kandinsky[ n ] ] for n in
                     range(0, len(group_klee)) ]

    if inactive:
        group_matrix.append(inactive)

    session.set_group_matrix(group_matrix)


def set_payoff(subsession: Subsession):
    session = subsession.session
    import random
    players = subsession.get_players()
    for p in players:
        participant = p.participant
        participant.payoff = random.randint(participant.payoff_1, participant.payoff_2)


class Group(BaseGroup):
    card_1 = models.IntegerField(initial=0)
    card_2 = models.IntegerField(initial=0)
    highest_card = models.IntegerField(initial=0)
    highest_player = models.IntegerField(initial=1)


def set_payoff_1(group: Group):
    players = group.get_players()
    for p in players:
        participant = p.participant
        if p.num_winners_1 >= 2:
            ##participant.is_winner_1 = True
            participant.payoff_1 = C.REWARD


def set_payoff_2(group: Group):
    players = group.get_players()
    for p in players:
        participant = p.participant
        if p.num_winners_2 >= 2:
            participant.payoff_2.apprnd(C.REWARD)


def set_cards(group: Group):
    import random
    n = 6
    players = group.get_players()

    for p in players:
        participant = p.participant
        participant.card_number = list(random.sample(C.DECK, n))
        print(participant.card_number)
    random.shuffle(participant.card_number)
    for i in range(0, 6, C.PLAYERS_PER_GROUP):
        group.card_1 = participant.card_number[ i ]
        group.card_2 = participant.card_number[ i + 1 ]

    for p in players:
        participant = p.participant
        if p.id_in_group == 1:
            participant.my_deck = group.card_1
        else:
            participant.my_deck = group.card_2


class Player(BasePlayer):
    my_deck = models.IntegerField(label='Please select one card.')
    card = models.IntegerField(initial=0)
    is_winner_1 = models.BooleanField(initial=False)


def live_method(player: Player, data):
    group = player.group
    my_id = player.id_in_group
    is_new_high_card = False

    # card = bid
    if 'card' in data:
        card = data[ 'card' ]
        if card > group.highest_card:
            player.card = card
            group.highest_card = card
            group.highest_player = my_id
            is_new_high_card = True

    return {
        0: dict(
            is_new_high_card=is_new_high_card,
            highest_card=group.highest_card,
            highest_player=group.highest_player,
        )
    }


def js_vars(player: Player):
    group = player.group
    return dict(my_id=player.id_in_group)


class Instruction(Page):
    form_model = 'player'


class WaitToPlay(WaitPage):
    after_all_players_arrive = set_cards


class PlayCards(Page):
    form_model = 'player'
    form_fields = [ 'my_deck' ]
    live_method = 'live_method'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(deck_numbers=range(1, 4))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        for p in group.highest_player:
            p.num_winners_1 += 1


class WaitForResults(WaitPage):
    after_all_players_arrive = set_payoff_1

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [ Instruction, WaitToPlay, PlayCards, WaitForResults ]
