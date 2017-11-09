# coding : utf-8

import asyncio
import websockets
import json
import GlobalParameters as gp
import Piece


class Server :
	def __init__(self):
		self.mySockets={"players": [],"viewers": []}
		self.compteur = 0

	async def connect(self, sock, path) :
		mess = await sock.recv()
		mess = json.loads(mess)
		self.compteur += 1
				
		if mess["user"] == "display" :
			self.mySockets["viewers"].append(sock)
			gp.MaPartie.bind_viewer([mess["name"],sock, self.compteur])	
			data = self.data_init_display()
			await sock.send(json.dumps(data))		
			print("Un display connecté")

		elif mess["user"] == "player" :
			self.mySockets["players"].append(sock)
			gp.MaPartie.bind_player([mess["name"],sock, self.compteur])
			await sock.send(json.dumps({"id":self.compteur}))
			print("Un player connecté")
		else :
			print("WARNING ! Bad connection detected !")
		while True:
			await asyncio.sleep(0)

	def data_init_display(self) :
		data = {}
		data["step"] = "init"
		data["nid"] = self.compteur
		data["nb_player"] = gp.NOMBRE_DE_JOUEUR
		data["kinds"] = {}
		for (key, blocks) in Piece.Piece.kinds.items() :
			data["kinds"][key] = []
			for b in blocks :
				data["kinds"][key] += [[float(b[0][0]), float(b[1][0])]]
		data["color"] = {}
		for (key, color) in Piece.Piece.colors.items() :
			data["color"][key] = color.value
		return data


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
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
		data = json.loads(mess)
		return data["kind"]

	async def ask_user_rotate(self) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
		data = json.loads(mess)
		return data["rotate"]

	async def ask_user_abscisse(self) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
		data = json.loads(mess)
		return int(data["abscisse"])

	# async def run(self, websocket) :
	# 	async for message in websocket:
	# 		data = json.loads(message)
	# 		elif data["action"] == "disconnect_player" :
	# 			self.disconnect_player(websocket, data["name"])

	# 		elif data["action"] == "disconnect_viewer" :
	# 			self.disconnect_viewer(websocket, data["name"])

