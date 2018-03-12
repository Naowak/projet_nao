import sys
import os
sys.path.append('../')
import numpy as np
import asyncio

from JoueurIA import Level
from JoueurIA import Comunication
from JoueurIA.Client import Entropy, Reinforcement, Reinforcement2

async def create_ia(name,level):
    my_client = None
    IA_STRATEGIE = None
    if level == 0 :
        IA_STRATEGIE = Level.Level(Level.random_ia)
    elif level == 1 :
        IA_STRATEGIE = Level.Level(Level.basic_smart_ia)
    elif level == 2 :
        IA_STRATEGIE = Entropy.Entropy(name, load_file = "./JoueurIA/Client/backup/4_heuristic.save")
    elif level == 3 :
        IA_STRATEGIE = Entropy.Entropy(name, load_file = "./JoueurIA/Client/backup/6_heuristic.save")
    elif level == 4 :
        # IA_STRATEGIE = Reinforcement.Reinforcement(name, load_file = os.path.join('JoueurIA', 'Client', 'rein_learn_models', 'agent_20180309_160050-10'))
        IA_STRATEGIE = Reinforcement2.Reinforcement(name, load_file=os.path.join('JoueurIA', 'Client', 'rein_learn_models', 'agent_20180312_160212-48264'))

    my_client = Comunication.Comunication(name, IA_STRATEGIE, level = level)
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    #print("socket")
    while my_client.keep_connection:
        await my_client.on_message()
        await asyncio.sleep(0)
    print("connexion lost")
