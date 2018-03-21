# coding: utf-8
import sys
sys.path.append("../")
import asyncio
import json
import websockets
import numpy as np
import GlobalParameters as gp
URI = gp.ADRESSE + str(gp.PORT)


class Comunication:

    def __init__(self, name,my_ia,active = True, level=None):
        self.my_socket = None
        self.keep_connection = True
        self.my_ia = my_ia
        self.name = name
        self.level = level
        self.pid = None
        self.ids_in_games = {} # different {gid1:[id1,id2...],gid2:[id1,id2...]}
        self.last_turn = {}
        self.active = active

    async def connect(self, uri=URI):
        self.my_socket = await websockets.connect(uri)
        mess = {"name": self.name}
        if self.level is not None:
            mess["level"]=self.level
        await self.send_message(mess)
        data = await self.receive_message()
        self.init_connect(data)
        while self.keep_connection:
            await asyncio.sleep(0)

    def make_connection_to_server(self):
        asyncio.ensure_future(self.connect())

    async def receive_message(self):
        data = await self.my_socket.recv()
        #print(data)
        return json.loads(data)

    async def on_message(self):
        data = await self.receive_message()
        if data["step"] == "update":
            self.update(data)
        elif data["step"] == "init_game":
            self.init_game(data)
        elif data["step"] == "game":
            if data["actual_player"] in self.ids_in_games[data["gid"]] and\
            data["turn"]!= self.last_turn[data["gid"]]:
                await asyncio.ensure_future(self.play(data))
            self.update_play(data)
        elif data["step"] == "suggest":
            if data["actual_player"] in self.ids_in_games[data["gid"]] and\
            data["turn"] != self.last_turn[data["gid"]]:
                await self.suggest(data)
        elif data["step"] == "finished":
            self.finished(data)
        else:
            print("Error Client message receive : step unknown")

    def update(self,data):
        gid_removed =[]
        for key in self.ids_in_games:
            if not str(key) in data["games"]:
                gid_removed.append(key)
        for gid in gid_removed:
            del self.ids_in_games[gid]

    def update_play(self, data) :
        self.my_ia.update_play(data)

    def finished(self, data):
        self.my_ia.on_finished_game(data)
        del self.last_turn[data["gid"]]
        del self.ids_in_games[data["gid"]]
        
    def init_game(self, data):
        self.my_ia.on_init_game(data)
        self.keep_connection = True
        self.ids_in_games[data["gid"]] = data["ids_in_game"]
        self.last_turn[data["gid"]] = None
        print(self.name, ": Succesfull game connection ids_in_games:", str(self.ids_in_games))

    def init_connect(self, data):
        self.pid = data["pid"]
        print(self.name, ": Succesfull server connection id:", str(self.pid))

    async def play(self, data):
        dec = await self.my_ia.play(data)
        self.last_turn[data["gid"]] = data["turn"]
        #await self.send_message({"gid": data["gid"], "mess_type": "action", "action": ["choose", dec.pop("choose")]})*
        try:
            choose = dec.pop("choose")
            await self.send_message({"gid": data["gid"], "mess_type": "action", "action": ["choose", choose]})
        except KeyError:
            pass
        for (key, value) in dec.items():
            if key != "valid":
                await self.send_message({"gid": data["gid"], "mess_type": "action", "action": [key, value]})
        if (not "valid" in dec.keys()) or (dec["valid"]):
            await self.send_message({"gid": data["gid"], "mess_type": "action", "action": ["valid"]})
        else:
            asyncio.ensure_future(self.play(data))

    async def suggest(self, data):
        dec = await self.my_ia.play(data)
        self.last_turn[data["gid"]] = data["turn"]
        try:
            choose = dec.pop("choose")
            await self.send_message({"gid": data["gid"], "mess_type": "action", "action": ["choose", choose]})
        except KeyError:
            pass
        for (key, value) in dec.items():
            if key != "valid":
                await self.send_message({"gid": data["gid"], "mess_type": "action", "action": [key, value]})
        if (not "valid" in dec.keys()) or (dec["valid"]):
            await self.send_message({"gid": data["gid"], "mess_type": "action", "action": ["valid"]})
        else:
            asyncio.ensure_future(self.play(data))

    async def send_message(self, data):
        # print("send")
        # print(data)
        await self.my_socket.send(json.dumps(data))


async def run(name):
    my_client = Comunication(name,Level.Level(Level.random_ia))
    my_client.make_connection_to_server()
    while my_client.my_socket is None:
        await asyncio.sleep(0)
    while my_client.keep_connection:
        await my_client.on_message()
        await asyncio.sleep(0)


# asyncio.get_event_loop().run_until_complete(main())
