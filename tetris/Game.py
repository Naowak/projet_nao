# coding : utf-8

import State
import Piece
import random
import copy



absi = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

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

def pieces_random() :
	kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
	kinds_select = []
	for _ in range(3) : 
		k = random.choice(kinds)
		kinds.remove(k)
		kinds_select.append(k)
	return kinds_select

def ask_user_abscisse() :
	print("Please enter an valid abscisse : ")
	a = int(input())
	return a


# def main() :
# 	grid = State.State()
# 	for _ in range(30) :
# 		kind = random.choice(kinds)
# 		center = copy.copy(Piece.Piece.centers_init[kind])
# 		piece = Piece.Piece.factory(kind, center)

# 		boucle = True
# 		abscisse = 0
# 		while boucle :
# 			abscisse = random.choice(absi)
# 			boucle = not grid.is_piece_accepted_abscisse(piece, abscisse)
			
# 		center[0] = abscisse - piece.block_control[0]
# 		result = grid.drop_piece(piece)
# 		print(grid)
# 		if(not result) :
# 			print("Game Lost !")
# 			break

def main() :
	grid = State.State()
	test = True
	print(grid)
	while test :
		kinds = pieces_random()
		kind = ask_user_piece_choose(kinds)

		center = copy.copy(Piece.Piece.centers_init[kind])
		piece = Piece.Piece.factory(kind, center)

		boucle = True
		abscisse = 0
		while boucle :
			abscisse = ask_user_abscisse()
			boucle = not grid.is_piece_accepted_abscisse(piece, abscisse)

		center[0] = abscisse - piece.block_control[0]
		result = grid.drop_piece(piece)
		print(grid)
		if not result :
			print("Game Lost !")
			break

main()