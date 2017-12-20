import Server
import IAClient
import GlobalParameters as gp
import asyncio
import os

async def javascript_run():
    os.system("gnome-open tetris_ui.html")

async def GUI()
    print ("Players connect :",SERVER.my_sockets["players"][0])
    print ("Viewers connect :",SERVER.my_sockets["players"][0])

SERVER = Server.Server()

loop = asyncio.get_event_loop()
loop.run_until_complete(SERVER.accept_connections(gp.PORT))
asyncio.ensure_future(javascript_run())
asyncio.ensure_future(GUI)
loop.run_forever()


