# coding : utf-8

import asyncio
import websockets
import json
import GlobalParameters as gp
import Piece
import Game


class Server :
	def __init__(self):
		self.mySockets={"players": [],"viewers": []}
		self.games ={}
		self.next_games_id = 0
		self.next_connect_id = 0

	async def run_server(self):
		await self.accept_connections(gp.PORT)
		print("Serveur running on")
		while not len(self.mySockets["players"]) == gp.NOMBRE_DE_JOUEUR :
				await asyncio.sleep(0)
		asyncio.ensure_future(self.run_game(self.mySockets["players"],self.mySockets["players"]))

	async def run_game(self,players,viewers):
			gid = self.next_games_id
			game = self.games[gid] = Game.Game(gid)
			self.next_games_id+=1
			for viewer in viewers:
				game.bind_viewer(viewer)
			for player in players:
				game.bind_player(player)
			await game.init_turn()
			while(not game.is_finished) :
				await self.receive_command()
			del self.games[game.gid]

	async def connect(self, sock, path) :
		mess = await sock.recv()
		mess = json.loads(mess)
		self.next_connect_id  += 1
		data = self.data_init_display()
		if mess["user"] == "display" :
			self.mySockets["viewers"].append([mess["name"],sock, self.next_connect_id])
			await self.send_message(sock,data)
			print("Un display connecté")

		elif mess["user"] == "player" :
			self.mySockets["players"].append([mess["name"],sock, self.next_connect_id])
			await self.send_message(sock,data)
			print("Un player connecté")
		else :
			print("WARNING ! Bad connection detected !")

		while True:
			await asyncio.sleep(0)

	def data_init_display(self) :
		data = {}
		data["step"] = "init"
		data["nid"] = self.next_connect_id
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
		return websockets.serve(self.connect, 'localhost', port) #, timeout=100

	def disconnect_player(self, sock, name) :
		self.mySockets["players"].remove(sock)
		gp.MaPartie.unbind_player(name)

	def diconnect_viewer(self, sock, name) :
		self.mySockets["viewers"].remove(sock)
		gp.MaPartie.unbind_viewer(name)

	async def send_message(self, websocket, mess) :
		print("send")
		print(mess)
		await websocket.send(json.dumps(mess))

	async def receive_command(self,game) :
		mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
		mess = json.loads(mess)
		print("receive")
		print(mess)
		game.set_etat(mess["action"])



	# async def ask_user_piece_choose(self, pieces_kind) :
	# 	mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
	# 	data = json.loads(mess)
	# 	return data["kind"]
	#
	# async def ask_user_rotate(self) :
	# 	mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
	# 	data = json.loads(mess)
	# 	return data["rotate"]
	#
	# async def ask_user_abscisse(self) :
	# 	mess = await self.mySockets["players"][gp.MaPartie.actual_turn%gp.NOMBRE_DE_JOUEUR].recv()
	# 	data = json.loads(mess)
	# 	return int(data["abscisse"])

	# async def run(self, websocket) :
	# 	async for message in websocket:
	# 		data = json.loads(message)
	# 		elif data["action"] == "disconnect_player" :
	# 			self.disconnect_player(websocket, data["name"])

	# 		elif data["action"] == "disconnect_viewer" :
	# 			self.disconnect_viewer(websocket, data["name"])

server = Server()
asyncio.get_event_loop().run_until_complete(server.run_server())
