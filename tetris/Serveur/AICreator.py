
"""
Script de creation des niveaux de jeu appele par le serveur, chaque niveau represente un client de
type AIEntity stocke dans l'attribut my-ias du serveur.
"""
import sys
import os
sys.path.append('../')
import numpy as np
import asyncio

from JoueurIA import Level
from JoueurIA import Comunication
from JoueurIA.Client import Entropy
from JoueurIA.Client import Heuristic as H

async def create_ia(name,level):
    """
    Fonction de creation d'un thread correspondant a une niveau du jeu.

    Attributs:
        -name : nom du niveau;
        -level : niveau correspondant dans le tableau level de GlobalParameters.
    """
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
    my_client = Comunication.Comunication(name, IA_STRATEGIE, level = level)
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    #print("socket")
    while my_client.keep_connection:
        await my_client.on_message()
        await asyncio.sleep(0)
    print("connexion lost")
