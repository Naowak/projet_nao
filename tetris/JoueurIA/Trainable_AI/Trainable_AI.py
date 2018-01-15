# coding: utf-8
import sys
sys.path.append("../")
sys.path.append("../../")
import asyncio


from JoueurIA import IAClientClient
from JoueurIA import IA

class TrainableIA(IA.IA):
    def __init__(self,name, file):
        self.state = None
        self.my_client = None
        self.name = name
        self.file = file

    async def init_train(self):
        self.my_client = IAClientClient.IAClientClient(self.name, self)
        self.my_client.make_connection_to_server()
        print("Wait for connection")
        while self.my_client.my_socket is None or self.my_client.pid is None:
            await asyncio.sleep(0)
        print("Connect")
        asyncio.ensure_future(self.message_loop())

    async def message_loop(self):
        while self.my_client.keep_connection:
            await self.my_client.receive_msg()
            await asyncio.sleep(0)

    def play(self, state):
        pass

    def on_init_game(self, data):
        pass

    def on_finished_game(self,data):
        pass

    async def new_game(self,opposite_level):
        mess = {'mess_type': 'new_game',\
                'players': [[self.my_client.pid,1]],\
                'observers': [3],\
                'IAs': [[opposite_level,1]]}
        await self.my_client.send_message(mess)

    def save(self):
        pass

    def load(self):
        pass

