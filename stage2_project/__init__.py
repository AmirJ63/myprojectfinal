


from otree.api import *
from otree.models import participant
import random
import json

doc = """
Card Game (competition game)
"""



class Constants(BaseConstants):
    name_in_url = 'CardGame'
    players_per_group = 2
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    current_card = models.StringField(initial='')


class Player(BasePlayer):
    hand = models.LongStringField()
    is_winner = models.BooleanField(initial=False)
    #decision = models.StringField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    rand_card2 = models.IntegerField()
    rand_card3 = models.IntegerField()

    #def decision_choices (player):
        #choices = ["card1", "card2", "card3"]
      #  return choices

class WaitToPlay(WaitPage):
    pass

# PAGES

##def live_method(player: Player, data):
   ## group = player.group
   ## my_id = player.id_in_group
   ## hand = json.loads(player.hand)

   ## current_card = group.current_card
   ## msg_type = data['type']

   ## if card in hand (card, current_card):
          ##  hand.remove(card)
          ##  group.current_card = card
          ##  player.hand = json.dumps(hand)



class Page3(Page):
    form_model = 'player'
    #form_fields = ['decision']
    @staticmethod
    def vars_for_template(player: Player):
        player.card1 = random.randint(1, 10)
        rand_card2 = random.randint(1, 10)
        if rand_card2 != player.card1:
            player.card2 = rand_card2
        rand_card3 = random.randint(1, 10)
        if rand_card3 != player.card1 and rand_card3 != player.card2:
            player.card3 = rand_card3

    @staticmethod
    def live_method(player: Player, card):
        my_id = player.id_in_group
        return dict(id_in_group=my_id, card=card)


#class Results(Page):


## def vars_for_template(player: Player):

#class Page2(Page):
   # form_model = 'player'
    #form_fields = [ 'kandinsky5_paintings', 'klee5_paintings' ]



#class Results(Page):
   ## def vars_for_template(player: Player):
     ##   player.sum_klee_paintings = player.klee1_paintings + player.klee2_paintings + player.klee3_paintings + player.klee4_paintings + player.kandinsky5_paintings
      ##  player.sum_kandinsky_paintings = player.kandinsky1_paintings + player.kandinsky2_paintings + player.kandinsky3_paintings + player.kandinsky4_paintings + player.kandinsky5_paintings
    ##    player.difference_klee = player.sum_klee_paintings - player.sum_kandinsky_paintings
       ## player.payoff = player.difference_klee
     ##   print(player.payoff)


##class ResultsWaitPage(WaitPage):
  ##  @staticmethod
   ## def after_all_players_arrive(group: Group):
    ##    AA=[]
     ##       AA.append(p.payoff)
     ##   return AA


##class Group1(Page):
    ##pass




page_sequence = [WaitToPlay, Page3]

