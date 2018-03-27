# coding: utf-8
import sys
sys.path.append("../")
sys.path.append("../../")
import asyncio


from JoueurIA import Comunication
from JoueurIA import Level

class ClientInterface:
    def __init__(self,name, file, active = True):
        self.state = None
        self.my_client = None
        self.name = name
        self.file = file
        self.active = active

    async def init_train(self): #rappeler connect (eventuellement)
        self.my_client = Comunication.Comunication(self.name, self)
        self.my_client.make_connection_to_server()
        while self.my_client.my_socket is None or self.my_client.pid is None:
            await asyncio.sleep(0)
        asyncio.ensure_future(self.message_loop())

    async def message_loop(self):
        while self.my_client.keep_connection:
            await self.my_client.on_message()
            await asyncio.sleep(0)

    async def play(self, state):
        pass

    def on_init_game(self, data):
        pass

    def on_finished_game(self,data):
        pass

    def update_play(self, data) :
        pass

    async def new_game(self,players=[],ias=[],viewers=[]):
        mess = {'mess_type': 'new_game',\
                'players': players,\
                'viewers': viewers,\
                'IAs': ias}
        await self.my_client.send_message(mess)

    async def observe_game(self,gid):
        mess = {'mess_type': 'link_game',\
                'gid': gid } 
        await self.my_client.send_message(mess)

    def save(self):
        pass

    def load(self):
        pass

