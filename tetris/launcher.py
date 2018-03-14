"""
Script de lancement du programme lance :
-le serveur;
-une interface client GUI. 
"""
import asyncio
import os
import webbrowser
import argparse

import GlobalParameters as gp
from Serveur import Server
from JoueurIA.Client import Stats


async def javascript_run() :
    """
    Fonction asynchrone permettant de lancer une interface client GUI dans le navigateur internet
    par defaut.
    """
    #os.system("gnome-open tetris_ui.html")
    webbrowser.open("JoueurGUI/tetris_ui.html")
    # pass


parser = argparse.ArgumentParser(description='launcher')
parser.add_argument('--remote', dest='local_ip', const="0.0.0.0", action='store_const', help='remote possible')
args = parser.parse_args()

if args.local_ip is not None:
    gp.LOCAL_ADDRESS = args.local_ip

SERVER = Server.Server()

loop = asyncio.get_event_loop()
loop.run_until_complete(SERVER.accept_connections(gp.PORT))
asyncio.ensure_future(SERVER.init_ia())
asyncio.ensure_future(javascript_run())
loop.run_forever()
