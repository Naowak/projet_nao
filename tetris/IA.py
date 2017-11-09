# coding: utf-8
import asyncio
import websockets
import GlobalParameters as gp
import json
import random
import sys

URI = gp.ADRESSE + str(gp.PORT)

class IA:
    def __init__(self,strategy) :
        self.strategy = strategy

    def play(state):
        return strategy(state)

def randomIA(state):
    print(state)
    piece = random.choice(state["pieces"])
    rotat = random.range(1,4)
    hor_move = random.range(0,9)-4
    return {"hor_move":hor_move,"rotat":rotat,"choose":piece}
