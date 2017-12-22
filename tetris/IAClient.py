# coding: utf-8

import asyncio
import json

import websockets

import IA
import GlobalParameters as gp
URI = gp.ADRESSE + str(gp.PORT)


class IAClient:

    def __init__(self, name,my_ia,level=None):
        self.my_socket = None
        self.keep_connection = True
        self.my_ia = my_ia
        self.name = name
        self.level = level
        self.pid = None
        self.ids_in_game = {} # different {gid1:[id1,id2...],gid2:[id1,id2...]}
        self.last_turn = None

    async def connect(self, uri=URI):
        self.my_socket = await websockets.connect(uri)
        mess = {"name": self.name}
        if self.level is not None:
            mess["level"]=self.level
        await self.send_message(mess)
        data = await self.receive_message()
        self.pid = data["pid"]
        while self.keep_connection:
            await asyncio.sleep(0)

    def make_connection_to_server(self):
        asyncio.ensure_future(self.connect())

    async def receive_message(self):
        data = await self.my_socket.recv()
        # print("receive")
        # print(data)
        return json.loads(data)

    async def receive_msg(self):
        data = await self.receive_message()
        print(data["step"])
        if data["step"] == "connect":
            self.init_connect(data)
        elif data["step"] == "init_game":
            self.init_game(data)
        elif data["step"] == "game":
            if data["actual_player"] in self.ids_in_game[data["gid"]]:
                await self.play(data)
        elif data["step"] == "suggest":
            if data["actual_player"] in self.ids_in_game[data["gid"]]:
                await self.suggest(data)
        elif data["step"] == "finished":
            self.finished(data)
        else:
            print("Error message receive : step unknown")
            
    def finished(self,data):
        self.last_turn = None
        self.ids_in_game = None

    def init_game(self, data):
        self.keep_connection = True
        self.ids_in_game[data["gid"]] = data["ids_in_game"]
        print("Succesfull game connection ids_in_game:", str(self.ids_in_game))

    def init_connect(self, data):
        self.nid = data["pid"]
        print("Succesfull server connection id:", str(self.nid))

    async def play(self, data):
        dec = self.my_ia.play(data)
        self.last_turn = data["turn"]
        await self.send_message({"mess_type":"action","action": ["choose", dec.pop("choose")]})
        for (key, value) in dec.items():
            await self.send_message({"mess_type":"action","action": [key, value]})
        await self.send_message({"mess_type":"action","action": ["valid"]})
        return data

    async def suggest(self, data):
        dec = self.my_ia.play(data)
        self.last_turn = data["turn"]
        await self.send_message({"mess_type":"action","action": ["choose", dec.pop("choose")]})
        for (key, value) in dec.items():
            await self.send_message({"mess_type":"action","action": [key, value]})

    async def send_message(self, data):
        # print("send")
        # print(data)
        await self.my_socket.send(json.dumps(data))


async def run(name):
    my_client = IAClient(name,IA.IA(IA.random_ia))
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    while my_client.keep_connection:
        await my_client.receive_msg()
        await asyncio.sleep(0)


async def create_ia(name,level):
    my_client = IAClient(name, IA.IA(IA.random_ia),level )
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    while my_client.keep_connection:
        await my_client.receive_msg()
        await asyncio.sleep(0)
    print("end")
#
# asyncio.get_event_loop().run_until_complete(main())
