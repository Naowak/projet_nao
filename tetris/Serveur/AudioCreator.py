import sys
import os
sys.path.append('../')
import numpy as np
import asyncio

from JoueurIA import Comunication
from JoueurIA.Client import Voice

async def create_audio(name):
    """
    Fonction de creation d'un thread correspondant a une gestion vocale

    Attributs:
        -name : nom de la commande vocale
    """
    my_client = None
    my_client = Comunication.Comunication(name, Voice.VoiceControl(), level="audio")
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    #print("socket")
    while my_client.keep_connection:
        await my_client.on_message()
        await asyncio.sleep(0)
    print("Audio Connexion lost")
