import sys
import os
sys.path.append('../')
import numpy as np
import asyncio

from JoueurIA import IA
from JoueurIA import IAClientClient
from JoueurIA.Trainable_AI import Entropy
from JoueurIA.Trainable_AI import Heuristic as H

async def create_ia(name,level):
    my_client = None
    IA_STRATEGIE = None
    if level == 0 :
        IA_STRATEGIE = IA.IA(IA.random_ia)
    elif level == 1 :
        IA_STRATEGIE = IA.IA(IA.basic_smart_ia)
    elif level == 2 :
        IA_STRATEGIE = Entropy.Genetic_IA(\
                                   name,\
                                   load_file = "./JoueurIA/Trainable_AI/backup/4_heuristic.save")
    elif level == 3 :
        IA_STRATEGIE = Entropy.Genetic_IA(\
                                   name,\
                                   load_file = "./JoueurIA/Trainable_AI/backup/6_heuristic.save")
    my_client = IAClientClient.IAClientClient(name, IA_STRATEGIE, level = level)
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    #print("socket")
    while my_client.keep_connection:
        await my_client.on_message()
        await asyncio.sleep(0)
    print("connexion lost")