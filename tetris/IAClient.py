# coding: utf-8
import IA
import GlobalParameters as gp
import asyncio
import websockets
import json
URI = gp.ADRESSE + str(gp.PORT)

class IAClient:

    def __init__(self,name) :
        self.mySocket = None
        self.keep_connection = True
        self.ia = IA.IA(IA.randomIA)
        self.name = name
        self.nid = None

    async def connect(self, uri = URI) :
        self.mySocket = await websockets.connect(uri)
        await self.send_message({"user":"player", "name":self.name})
        data = await self.receive_message()
        self.nid = data["nid"]
        while self.keep_connection :
            await asyncio.sleep(0)

    def make_connection_to_server(self) :
        asyncio.ensure_future(self.connect())

    async def receive_message(self) :
        data = await self.mySocket.recv()
        print("receive")
        print(data)
        return json.loads(data)

    def make_connection_to_server(self) :
        asyncio.ensure_future(self.connect())

    async def action(self) :
        data=await self.receive_message()
        if data["step"] == "init" :
            self.keep_connection = False
        elif data["step"] == "game" or data["step"] == "suggest"  :
            if (data["actual_player"] == self.nid and data["step"] == "game") or (data["step"] == "suggest" and data["actual_player"] != self.nid):
                dec = self.ia.play(data)
                for (key,value) in dec.items() :
                    mess=json.dumps({"action":[key,value]})
                    await self.send_message({"action":[key,value]})
                if data["step"] == "game" :
                    await self.send_message({"action":["valid"]})
        elif data["step"] == "finished" :
            self.keep_connection = False
        return data

    async def send_message(self, data) :
        print("send")
        print(data)
        await self.mySocket.send(json.dumps(data))

async def main() :
    monClient = IAClient("Bernard")
    monClient.make_connection_to_server()
    while monClient.mySocket == None :
        await asyncio.sleep(0)
    while monClient.keep_connection :
        await monClient.action()
        await asyncio.sleep(0.3)

asyncio.get_event_loop().run_until_complete(main())
