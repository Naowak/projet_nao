# coding: utf-8
import random
import GlobalParameters as gp
import State
import Piece
import copy
import random

URI = gp.ADRESSE + str(gp.PORT)


class IA:
    def __init__(self, strategy):
        self.strategy = strategy

    def play(self, state):
        return self.strategy(state)

def random_ia(state):
    piece = random.choice(state["pieces"])
    rotat = random.randrange(1, 4, 1)
    hor_move = random.randrange(0, 9, 1)-5
    return {"hor_move":hor_move, "rotate":rotat, "choose":piece}

def basic_smart_ia(state) :
	pieces = copy.copy(state["pieces"])
	scores = []
	compteur = 0

	for kind in pieces :
		for rotation in range(0,4,1) :
			for abscisse in range(0,10,1) :
				grid_tmp = State.State(copy.copy(state["grid"]))
				p = Piece.Piece.factory(kind, copy.copy(Piece.Piece.centers_init[kind]))
				for _ in range(rotation) :
					p.rotate()
				if(State.is_piece_accepted_abscisse(p, abscisse)) :
					r = grid_tmp.drop_piece(p, 0)
					play = {"choose":kind, "rotate":rotation, "hor_move":abscisse}
					scores += [[play, grid_tmp.score[0]]]
					print(r, grid_tmp)

	scores.sort(key=lambda x : x[1], reverse=True)
	best = scores[0][1]
	best_plays = []
	for s in scores :
		if s[1] >= best :
			best_plays += [s]
	print(best_plays)

	return random.choice(best_plays)[0]


my_grid = [['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White'], 
['Red', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White', 'White']]
pieces = ["O", "I", "L"]
state = {"pieces":pieces, "grid":my_grid}

print(basic_smart_ia(state))