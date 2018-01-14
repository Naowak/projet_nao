# coding: utf-8
import sys
sys.path.append('../')

from JoueurIA import IA
from JoueurIA import IAClientClient

class TrainableIA(IA.IA):
    def __init__(self,name, file):
        self.state = None
        self.my_client = None
        self.name = name
        self.file = file

    def init_train(self):
        self.my_client = IAClientClient.IAClientClient(self.name, self)
        self.my_client.make_connection_to_server()

    def play(self, state):
        pass

    def on_init_game(self, data):
        pass

    def on_finished_game(self,data):
        pass

    def new_game(self,opposite_level):
        mess = {'mess_type': 'new_game',\
                'players': [[self.my_client.pid,1]],\
                'observers': [],\
                'IAs': [opposite_level,1]}
        self.my_client.send_message(mess)

    def save(self):
        pass

    def load(self):
        pass

