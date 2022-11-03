from otree.api import *

doc = """
Continuous-time public goods game with slider
"""


class C(BaseConstants):
    NAME_IN_URL = 'continuous_slider'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    MAX_CONTRIBUTION = cu(100)
    CHART_TEMPLATE = __name__ + '/chart.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    start_timestamp = models.IntegerField()


class Player(BasePlayer):
    pass



class WaitToStart(WaitPage):
    pass

# PAGES
class MyPage(Page):


    @staticmethod
    def js_vars(player: Player):
        return dict(my_id=player.id_in_group, max_contribution=C.MAX_CONTRIBUTION)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(max_contribution=int(C.MAX_CONTRIBUTION))

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        import time

        # print('data is', data)

        if 'contribution' in data:
            contribution = data['contribution']


            # this is optional. it allows the line
            # to go all the way to the right of the graph

        highcharts_series = dict(data=contribution, type='line')
        return dict(highcharts_series=highcharts_series)


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # to be filled in.
        # you should calculate some results here. maybe aggregate all the Adjustments,
        # take their weighted average, etc.
        # adjustments = Adjustment.filter(group=group)
        pass


class Results(Page):
    pass


page_sequence = [WaitToStart, MyPage, ResultsWaitPage, Results]