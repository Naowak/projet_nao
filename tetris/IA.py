# coding: utf-8
import random
import GlobalParameters as gp

URI = gp.ADRESSE + str(gp.PORT)


class IA:
    def __init__(self, strategy):
        self.strategy = strategy

    def play(self, state):
        return self.strategy(state)

def random_ia(state):
    piece = random.choice(state["pieces"])
    rotat = random.randrange(1, 4, 1)
    hor_move = random.randrange(0, 9, 1)-4
    return {"hor_move":hor_move, "rotate":rotat, "choose":piece}
