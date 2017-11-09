# coding: utf-8
import IA

URI = gp.ADRESSE + str(gp.PORT)

class IAClient:

    def __init__(self) :
        self.mySocket = None
        self.keep_connection = True
        self.ia = IA(IA.randomIA)

    async def connect(self, uri = URI) :
		self.mySocket = await websockets.connect(uri)
		await self.send_message({"user":"player" "name":self.name})
		data = await self.receive_message()
		self.nid = data["nid"]
		while self.keep_connection :
			await asyncio.sleep(0)

    def make_connection_to_server(self) :
		asyncio.ensure_future(self.connect())

    async def receive_message(self) :
        mess = await self.mySocket.recv()
        if data["step"] == "init" :
            self.keep_connection = False
        if (data["actual_player"] == self.player_number && data["step"] == "game") ||
         (data["step"] == "suggest" && data["actual_player"] != self.player_number):
            dec = ia.play(json.loads(mess))
            for (key,value) in dec.items :
                await self.mySocket.send({"action":[key,value]})
        if data["step"] == "game" :
            await self.mySocket.send({"action":["valid"]})
