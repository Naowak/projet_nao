# coding : utf-8

import State
import Piece
import random
import copy
import json
import Subject
import Server
import GlobalParameters as gp
import asyncio

#absi = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
class Game(Subject.Subject) :

	def __init__(self) :
		super().__init__()
		self.grid = State.State()
		self.is_finished = False
		self.actual_turn = 0
		self.actual_pieces = list()
		self.step = "init"

	def pieces_random(self, nb = 3) :
		kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
		kinds_select = []
		for _ in range(nb) :
			k = random.choice(kinds)
			kinds.remove(k)
			kinds_select.append(k)
		self.actual_pieces = kinds_select
		return kinds_select

	async def turn(self) :
		if self.step != "init" :
			await self.notify_view()
		print(self.grid)
		if not self.is_finished :
			self.actual_turn += 1 #Le tour commence à 1

			self.step = "piece_choice"
			kinds = self.pieces_random()
			await self.notify_all_observers()
			kind = await self.server.ask_user_piece_choose(kinds)

			center = copy.copy(Piece.Piece.centers_init[kind])
			piece = Piece.Piece.factory(kind, center)
			self.grid.piece_show(piece)

			self.step = "rotation"
			boucle = True
			while boucle :
				await self.notify_all_observers()
				rotate = await self.server.ask_user_rotate()
				if rotate == "R":
					piece.rotate()
					self.grid.piece_show(piece)
				elif rotate == "" :
					boucle = False

			self.step = "abscisse"
			boucle = True
			abscisse = 0
			while boucle :
				await self.notify_all_observers()
				abscisse = await self.server.ask_user_abscisse()
				boucle = not self.grid.is_piece_accepted_abscisse(piece, abscisse)


			center[0] = abscisse - piece.block_control[0]
			self.grid.show_abscisse(piece, abscisse)
			self.step = "end_turn"
			await self.notify_view()
			result = self.grid.drop_piece(piece, self.actual_turn %gp.NOMBRE_DE_JOUEUR)
			if not result :
				self.step = "finished"
				self.is_finished = True
				await self.notify_view()
				print("Game Lost !")

	def encode_to_Json(self) :
		dico = self.grid.encode_to_Json()
		tmp = {"pieces":[i for i in self.actual_pieces]}
		dico["pieces"]=tmp["pieces"]
		dico["step"] = self.step
		dico["actual_player"] = self.observers["players"][self.actual_turn%gp.NOMBRE_DE_JOUEUR][2]
		return json.dumps(dico)


def ask_user_piece_choose(pieces_kind) :
	test = False
	kind = ""
	while not test :
		print("Choose a piece from those pieces : ")
		for p in pieces_kind :
			print(p + " ")
		print("\n")
		kind = input()
		if kind in pieces_kind :
			test = True
	return kind


def ask_user_abscisse() :
	print("Please enter an valid abscisse : ")
	a = int(input())
	return a

def ask_user_rotate() :
	print("To rotate the piece enter 'R', else press 'Enter' : ")
	a = input()
	return a

async def main() :
	gp.MaPartie = Game()
	while not len(gp.MaPartie.server.mySockets["players"]) == gp.NOMBRE_DE_JOUEUR :
            await asyncio.sleep(0)
	while(not gp.MaPartie.is_finished) :
		await gp.MaPartie.turn()


asyncio.get_event_loop().run_until_complete(main())
