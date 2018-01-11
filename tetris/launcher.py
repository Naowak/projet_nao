import asyncio
import os
import webbrowser

import GlobalParameters as gp
from Serveur import Server


async def javascript_run():
    #os.system("gnome-open tetris_ui.html")
    webbrowser.open("JoueurGUI/tetris_ui.html")
    # pass


SERVER = Server.Server()

loop = asyncio.get_event_loop()
loop.run_until_complete(SERVER.accept_connections(gp.PORT))
asyncio.ensure_future(SERVER.init_ia())
asyncio.ensure_future(javascript_run())
loop.run_forever()
