# coding : utf-8

import State
import Piece
import random
import copy
import json
import Subject

	#absi = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
class Game(Subject.Subject) :

	def __init__(self) :
		self.grid = State.State()
		self.is_finished = False
		self.actual_turn = 0
		self.actual_pieces = list()

	def pieces_random(self, nb = 3) :
		kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
		kinds_select = []
		for _ in range(nb) :
			k = random.choice(kinds)
			kinds.remove(k)
			kinds_select.append(k)
		self.actual_pieces = kinds_select
		return kinds_select

	def turn(self) :
		if not self.is_finished :
			self.actual_turn += 1 #Le tour commence à 1

			kinds = self.pieces_random()
			if self.actual_turn % 2 == 1 :
				kind = ask_user_piece_choose(kinds)
			else :
				kind = ask_user_piece_choose(kinds)

			center = copy.copy(Piece.Piece.centers_init[kind])
			piece = Piece.Piece.factory(kind, center)

			boucle = True
			while boucle :
				if self.actual_turn % 2 == 1 :
					rotate = ask_user_rotate()
				else :
					rotate = ask_user_rotate()
				if rotate == "R":
					piece.rotate()
				elif rotate == "" :
					boucle = False

			boucle = True
			abscisse = 0
			while boucle :
				if self.actual_turn % 2 == 1 :
					abscisse = ask_user_abscisse()
				else :
					abscisse = ask_user_abscisse()
				boucle = not self.grid.is_piece_accepted_abscisse(piece, abscisse)

			center[0] = abscisse - piece.block_control[0]
			result = self.grid.drop_piece(piece, self.actual_turn % 2)
			print(self.grid)
			if not result :
				self.is_finished = True
				print("Game Lost !")

		def encode_to_Json(self) :
			dico = self.grid.encode_to_Json()
			tmp = {"pieces":[i for i in self.actual_pieces]}
			dico["pieces"]=tmp["pieces"]
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
	print("To rotate de piece enter 'R', else press 'Enter' : ")
	a = input()
	return a

maPartie = Game()
while(not maPartie.is_finished) :
	maPartie.turn()
