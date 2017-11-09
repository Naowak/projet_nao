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

	def __init__(self,gid) :
		super().__init__(gid)
		self.grid = State.State()
		self.is_finished = False
		self.actual_turn = 0
		self.actual_pieces = list()
		self.step = "init"
		self.current_piece = None
		self.current_abscisse = None

	def pieces_random(self, nb = 3) :
		kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
		kinds_select = []
		for _ in range(nb) :
			k = random.choice(kinds)
			kinds.remove(k)
			kinds_select.append(k)
		self.actual_pieces = kinds_select
		return kinds_select

	async def update():
		self.grid.piece_show(self_current_piece)
		self.grid.show_abscisse(self.current_piece, self.current_abscisse)
		await self.notify_all_observers()

	def init_turn() :
		self.actual_pieces = self.pieces_random();
		self.current_piece = self.actual_pieces[0]
		self.current_abscisse = Piece.Piece.centers_init[self.current_piece]
		update()

	def choose_piece(self,kinds) :
		self.current_piece = kinds
		self.current_abscisse = 5


	async def hor_move_piece(self, move) :
		if self.grid.is_piece_accepted_abscisse(self.current_pieces, self.current_abscisse + move):
			center[0] = abscisse - piece.block_control[0]
		self.update()
		await self.notify_all_observers()

	def rotate_piece(self, rotate):
		for i in range(rotate%4) :
			self.current_piece.rotate()

	def valid(self) :
		result = self.grid.drop_piece(self.current_piece, self.actual_turn %gp.NOMBRE_DE_JOUEUR)
		self.actual_turn += 1 #Le tour commence à 1
		if not result :
			self.is_finished = True
			print("Game Lost !")
		else :
			self.init_turn()

	async def set_action(self,command,value) :
		if command == "choose" :
			self.choose_piece(value)
		elif command == "rotate" :
			self.rotate_piece(value)
		elif command == "hor_move" :
			self.hor_move_piece(value)
		else :
			print ("Modification d'état inconnu")
			return False
		await self.update()
		return True

	# async def turn(self) :
	# 	if self.step != "init" :
	# 		await self.notify_view()
	# 	print(self.grid)
	# 	if not self.is_finished :
	# 		self.actual_turn += 1 #Le tour commence à 1
	#
	# 		self.step = "piece_choice"
	# 		kinds = self.pieces_random()
	# 		await self.notify_all_observers()
	# 		kind = await self.server.ask_user_piece_choose(kinds)
	#
	# 		center = copy.copy(Piece.Piece.centers_init[kind])
	# 		piece = Piece.Piece.factory(kind, center)
	# 		self.grid.piece_show(piece)
	#
	# 		self.step = "rotation"
	# 		boucle = True
	# 		while boucle :
	# 			await self.notify_all_observers()
	# 			rotate = await self.server.ask_user_rotate()
	# 			if rotate == "R":
	# 				piece.rotate()
	# 				self.grid.piece_show(piece)
	# 			elif rotate == "" :
	# 				boucle = False
	#
	# 		self.step = "abscisse"
	# 		boucle = True
	# 		abscisse = 0
	# 		while boucle :
	# 			await self.notify_all_observers()
	# 			abscisse = await self.server.ask_user_abscisse()
	# 			boucle = not self.grid.is_piece_accepted_abscisse(piece, abscisse)
	#
	#
	# 		center[0] = abscisse - piece.block_control[0]
	# 		self.grid.show_abscisse(piece, abscisse)
	# 		self.step = "end_turn"
	# 		await self.notify_view()
	# 		result = self.grid.drop_piece(piece, self.actual_turn %gp.NOMBRE_DE_JOUEUR)
	# 		if not result :
	# 			self.step = "finished"
	# 			self.is_finished = True
	# 			await self.notify_view()
	# 			print("Game Lost !")

	def encode_to_Json(self) :
		dico = self.grid.encode_to_Json()
		tmp = {"pieces":[i for i in self.actual_pieces]}
		dico["gid"]=gid
		dico["pieces"]=tmp["pieces"]
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
