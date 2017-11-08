#coding : utf-8

import asyncio
import websockets
import GlobalParameters as gp
import json
import random

URI = gp.ADRESSE + str(gp.PORT)

class Client :
	def __init__(self, user="player") :
		self.user = user
		self.mySocket = None
		self.keep_connection = True
		self.player_number = 0

	async def connect(self, uri = URI) :
		self.mySocket = await websockets.connect(uri)
		await self.send_message({"user":self.user, "name":"bolosse"})
		data = await self.receive_message()
		self.player_number = data["id"]
		while self.keep_connection :
			await asyncio.sleep(0)

	def make_connection_to_server(self) :
		asyncio.ensure_future(self.connect())

	async def receive_message(self) :
		mess = await self.mySocket.recv()
		return json.loads(mess)

	async def send_message(self, data) :
		await self.mySocket.send(json.dumps(data))

	async def play(self) :
		data = await self.receive_message()
		if data["actual_player"] == self.player_number :
			if data["step"] == "init" :
				self.keep_connection = False
			elif data["step"] == "piece_choice" :
				piece = ask_piece_to_choose(data["pieces"])
				await self.send_message({"kind":piece})
			elif data["step"] == "rotation" :
				rotate = ask_rotate()
				await self.send_message({"rotate":rotate})
			elif data["step"] == "abscisse" :
				abscisse = str(ask_abscisse())
				await self.send_message({"abscisse":abscisse})
			elif data["step"] == "finished" :
				self.keep_connection = False



def ask_piece_to_choose(kinds) :
	return random.choice(kinds)

def ask_rotate() :
	return random.choice(["R", ""])

def ask_abscisse() :
	return random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


async def main() :
	monClient = Client()
	monClient.make_connection_to_server()
	while monClient.mySocket == None :
		await asyncio.sleep(0)
	while monClient.keep_connection :
		await monClient.play()
		await asyncio.sleep(0.2)

asyncio.get_event_loop().run_until_complete(main())
