# coding: utf-8
import sys
import random

sys.path.append("../")
sys.path.append("../../")

from JoueurIA import Level


class Example(Level.Level):
    def __init__(self, name, load_file):
        self.file = load_file

        self.load()

    def play(self, state):
        # return {'hor_move': 0, 'choose': 'O', 'rotation': 0}

        piece = random.choice(state["pieces"])
        rotat = random.randrange(1, 4, 1)
        hor_move = random.randrange(0, 9, 1)-5
        return {"hor_move":hor_move, "rotate":rotat, "choose":piece}

    def load(self):
        pass
