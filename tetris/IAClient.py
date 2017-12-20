# coding: utf-8

import asyncio
import json

import websockets

import IA
import GlobalParameters as gp
URI = gp.ADRESSE + str(gp.PORT)


class IAClient:

    def __init__(self, name):
        self.my_socket = None
        self.keep_connection = True
        self.my_ia = IA.IA(IA.random_ia)
        self.name = name
        self.nid = None
        self.last_turn=-1

    async def connect(self, uri=URI):
        self.my_socket = await websockets.connect(uri)
        await self.send_message({"user": "player", "name": self.name})
        data = await self.receive_message()
        self.nid = data["nid"]
        while self.keep_connection:
            await asyncio.sleep(0)

    def make_connection_to_server(self):
        asyncio.ensure_future(self.connect())

    async def receive_message(self):
        data = await self.my_socket.recv()
        #print("receive")
        #print(data)
        return json.loads(data)

    async def action(self):
        data = await self.receive_message()
        if data["step"] == "init":
            print("Succesfull server connection")
            self.keep_connection = True
        elif data["step"] == "game" or data["step"] == "suggest":
            if (data["actual_player"] == self.nid and data["step"] == "game" and data["turn"]!=self.last_turn ) or\
             (data["step"] == "suggest" and data["actual_player"] != self.nid and data["turn"]!=self.last_turn ):

                dec = self.my_ia.play(data)
                self.last_turn=data["turn"]
                await self.send_message({"action": ["choose", dec.pop("choose")]})
                for (key, value) in dec.items():
                    await self.send_message({"action": [key, value]})
                if data["step"] == "game":
                    await self.send_message({"action": ["valid"]})
        elif data["step"] == "finished" and gp.NB_PARTIE_RESTANTE == 0:
            self.keep_connection = False
        elif data["step"] == "finished" :
            gp.NB_PARTIE_RESTANTE -= 1
        return data

    async def send_message(self, data):
        #print("send")
        #print(data)
        await self.my_socket.send(json.dumps(data))



async def run_IAClient():
    my_client = IAClient("Bernard")
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    while my_client.keep_connection:
        await my_client.action()
        await asyncio.sleep(0)

#asyncio.get_event_loop().run_until_complete(main())
