import sys
sys.path.append('../')
import numpy as np
import asyncio

from JoueurIA import IA
from JoueurIA import IAClientClient
from JoueurIA.Trainable_AI import Entropy
from JoueurIA.Trainable_AI import Heuristic as H

async def create_ia(name,level):
    my_client = None
    if level == 0 :
        IA_STRATEGIE = IA.random_ia
        my_client = IAClientClient.IAClientClient(name, IA.IA(IA_STRATEGIE), level )
    elif level == 1 :
        IA_STRATEGIE = IA.basic_smart_ia
        my_client = IAClientClient.IAClientClient(name, IA.IA(IA_STRATEGIE), level )
    elif level == 2 :
        my_client = IAClientClient.IAClientClient(name,\
                                   Entropy.Genetic_IA(\
                                   name,\
                                   [H.line_transition,H.column_transition,H.holes,H.wells],\
                                   weights = np.array([-1.04341569,  0.19629992, -0.63325367, -1.0576598 ])),\
                                   level)
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    print("socket")
    while my_client.keep_connection:
        await my_client.receive_msg()
        await asyncio.sleep(0)
