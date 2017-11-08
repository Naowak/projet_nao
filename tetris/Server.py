# coding : utf-8

import asyncio
import websockets
import json
import GlobalParameters as gp


class Server :
	def __init__(self):
		self.mySockets={"players": [],"viewers": []}

	async def connect(self, sock, path) :
		mess = await sock.recv()
		mess = json.loads(mess)
		if mess["user"] == "display" :
			self.mySockets["viewers"].append(sock)
			gp.MaPartie.bind_viewer([mess["name"],sock])
			print("Un display connecté")
		elif mess["user"] == "player" :
			self.mySockets["players"].append(sock)
			gp.MaPartie.bind_player([mess["name"],sock])
			print("Un player connecté")
		else :
			print("WARNING ! Bad connection detected !")
		while True:
			await asyncio.sleep(0)

	def accept_connections(self, port) :
		asyncio.ensure_future(websockets.serve(self.connect, 'localhost', port, timeout=100))

	def disconnect_player(self, sock, name) :
		self.mySockets["players"].remove(sock)
		gp.MaPartie.unbind_player(name)

	def diconnect_viewer(self, sock, name) :
		self.mySockets["viewers"].remove(sock)
		gp.MaPartie.unbind_viewer(name)

	async def send_game(self, websocket) :
		await websocket.send(gp.MaPartie.encode_to_Json())

	async def ask_user_piece_choose(self, pieces_kind) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%2].recv()
		data = json.loads(mess)
		return data["kind"]

	async def ask_user_rotate(self) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%2].recv()
		data = json.loads(mess)
		return data["rotate"]

	async def ask_user_abscisse(self) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%2].recv()
		data = json.loads(mess)
		return int(data["abscisse"])

	# async def run(self, websocket) :
	# 	async for message in websocket:
	# 		data = json.loads(message)
	# 		elif data["action"] == "disconnect_player" :
	# 			self.disconnect_player(websocket, data["name"])

	# 		elif data["action"] == "disconnect_viewer" :
	# 			self.disconnect_viewer(websocket, data["name"])

