from otree.api import *
from otree.models import subsession

doc = """
Your app description
"""


def read_csv():
    import csv

    f = open(__name__ + '/paintings.csv', encoding='utf-8-sig')
    rows = [row for row in csv.DictReader(f)]
    for row in rows:
        row['image_path'] = 'first5paintings/{}.jpg'.format(row['image_jpg'])

    return rows


class C(BaseConstants):
    NAME_IN_URL = 'kk11'
    PLAYERS_PER_GROUP = None
    PRODUCTS = read_csv()
    NUM_ROUNDS = len(PRODUCTS)



class Subsession(BaseSubsession):
    pass



class Group(BaseGroup):
    pass



class Player(BasePlayer):
    sku = models.StringField()
    klee_difference = models.IntegerField()

    klee = models.IntegerField(
            widget=widgets.RadioSelectHorizontal,
            choices=[ 0, 1, 2, 3, 4, 5 ],
            label="I like:"
        )
    kandinsky = models.IntegerField(
            widget=widgets.RadioSelectHorizontal,
            choices=[ 0, 1, 2, 3, 4, 5 ],
            label="I like:"
    )


# Functions

def creating_session(subsession: Subsession):
    session = subsession.session
    session.scores = []
    for p in subsession.get_players():
       img = get_current_product(p)
       p.sku = img[ 'sku' ]

def set_score(player:Player):
    player.klee_difference = player.klee - player.kandinsky
    players = player.in_all_rounds()
    for p in players:
        p.klee_difference += (p.klee - p.kandinsky)


def get_current_product(player: Player):
    return C.PRODUCTS[player.round_number - 1]



##PAGES
class Page1(Page):
    form_model = 'player'
    form_fields = ['klee', 'kandinsky']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(product=get_current_product(player))

    @staticmethod
    def error_message(player: Player, values):
        print('values is', values)
        if values['klee'] + values['kandinsky'] != 5:
            return 'The numbers must add up to 5'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_score(player)



class ResultsWaitPage(WaitPage):
    pass

class Resultscombine(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        session.scores.append(player.klee_difference)

##This is my last try for defining a list of players and attributing scores to them. my problem is to have a list
## in which I can see klee_difference_all of all rounds fo all players.




# def vars_for_template(player: Player):
       # participant = player.participant
      #  all_scores =participant.kk11_klee_difference
      #  print(all_scores)



page_sequence = [Page1, ResultsWaitPage, Resultscombine]

