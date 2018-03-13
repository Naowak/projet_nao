"""
Script de lancement du programme lance :
-le serveur;
-une interface client GUI. 
"""
import asyncio
import os
import webbrowser

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


SERVER = Server.Server()

loop = asyncio.get_event_loop()
loop.run_until_complete(SERVER.accept_connections(gp.PORT))
asyncio.ensure_future(SERVER.init_ia())
asyncio.ensure_future(javascript_run())
loop.run_forever()
