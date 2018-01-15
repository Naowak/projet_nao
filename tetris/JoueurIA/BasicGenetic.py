import random
import sys

sys.path.append('../')

import GlobalParameters as gp

#from JoueurIA import IA
from Jeu import Block


#N : taille population
#P : partie jouer par individu
#K : Nombre d'individu sélectionné aléatoirement
#R : Nombre d'individu remplacé
def training(N = 100, P = 10, K = 10, R = 30) :
	pass
	#On créer N individu

	#On joue 10 partie par individu

	#On selection K individu pour la reproduction

	#On remplace les R pires individus par les R nouveaux

def two_ia_make_love(iag_1, score_1, iag_2, score_2) :
	coef1 = score_1/(score_1 + score_2)
	coef2 = score_2/(score_1 + score_2)
	poids1 = iag_1.poids1*coef1 + iag_2.poids1*coef2
	poids2 = iag_1.poids2*coef1 + iag_2.poids2*coef2
	poids3 = iag_1.poids3*coef1 + iag_2.poids3*coef2
	poids4 = iag_1.poids4*coef1 + iag_2.poids4*coef2
	return GeneticAI(ia)

class GeneticAI() :
	def __init__(self, p1 = random.random(), p2 = random.random(), p3 = random.random(), p4 = random.random()) :
		self.poids1 = p1
		self.poids2 = p2
		self.poids3 = p3
		self.poids4 = p4

	#evalue le play
	def evaluate_play(self, grid_prec, grid_next, action) :
		h = Heuristic(grid_prec, grid_next, action)
		return h.line_transition()*poids1 +\
			h.column_transition()*poids2 +\
			h.holes()*poids3 +\
			h.wells()*poids4

	def play_one_game(self, game) :

	def best_move(state) :
		pieces = copy.copy(state["pieces"])
		scores = []
		compteur = 0

		for kind in pieces :
			for rotation in range(0,4,1) :
				for move in range(-5,7,1) :
					play = {"choose":kind, "rotate":rotation, "hor_move":move}
					grid_tmp = State.State(copy_grid(state["grid"]))
					grid_prec = State.State(copy_grid(state["grid"]))
					p = Piece.Piece.factory(kind, copy.copy(Piece.Piece.centers_init[kind]))
					for _ in range(rotation) :
						p.rotate()
					if(State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + move)) :
						p.center[0] += move
						r = grid_tmp.drop_piece(p, 0)
						scores += [[play, self.evaluate_play(grid_prec, grid_tmp, play)]]

		scores.sort(key=lambda x : x[1], reverse=True)
		best = scores[0][1]
		best_plays = []
		for s in scores :
			if s[1] >= best :
				best_plays += [s]
		play_send = random.choice(best_plays)[0]
		return play_send
		



class Heuristic :
	def __init__(self, grid_prec, grid_next, action) :
		self.g_next = grid_next
		self.g_prec = grid_prec
		self.action = action

	#Return the latest action's height
	def height(self) :
		pass

	#(number of line last action)*(number of cells eliminated from the las piece)
	def erosion(self) :
		pass

	#number of empty/filled or filled/empty cells transition
	def line_transition(self) :
		cpt = 0
		for j in range(gp.TAILLE_Y_LIMITE) :
			for i in range(gp.TAILLE_X - 1) :
				if(self.g_next[i][j] == Block.Block.Empty and self.g_next[i+1][j] != Block.Block.Empty) or\
					(self.g_next[i][j] != Block.Block.Empty and self.g_next[i+1][j] == Block.Block.Empty) :
					cpt += 1
		return cpt

	#number of empty/filled or filled/empty cells transition
	def column_transition(self) :
		cpt = 0
		for i in range(gp.TAILLE_X) :
			for j in range(gp.TAILLE_Y_LIMITE-1) :
				if(self.g_next[i][j] == Block.Block.Empty and self.g_next[i][j+1] != Block.Block.Empty) or\
					(self.g_next[i][j] != Block.Block.Empty and self.g_next[i][j+1] == Block.Block.Empty) :
					cpt += 1
		return cpt

	#number of holes
	def holes(self) :
		cpt = 0
		for i in range(gp.TAILLE_X) :
			for j in range(gp.TAILLE_Y_LIMITE) :
				if(self.g_next[i][j] == Block.Block.Empty) :
					is_hole = True
					try :
						if(self.g_next[i][j+1] == Block.Block.Empty) :
							is_hole = False
					except IndexError :
						pass
					try :
						if(self.g_next[i][j-1] == Block.Block.Empty) :
							is_hole = False
					except IndexError :
						pass
					try :
						if(self.g_next[i+1][j] == Block.Block.Empty) :
							is_hole = False
					except IndexError :
						pass
					try :
						if(self.g_next[i-1][j] == Block.Block.Empty) :
							is_hole = False
					except IndexError :
						pass
					if is_hole :
						cpt += 1
		return cpt

	#number of wells :
	def wells(self) :
		cpt = 0
		#on compte les puits dans l'intérieur de la grille (attention dépassement indice)
		for i in range(1, gp.TAILLE_X-1) :
			for j in range(1, gp.TAILLE_Y_LIMITE) :
				#si on est à la source d'un puit
				if(self.g_next[i][j] == Block.Block.Empty and\
					self.g_next[i-1][j] != Block.Block.Empty and\
					self.g_next[i+1][j] != Block.Block.Empty and\
					self.g_next[i][j-1] != Block.Block.Empty and\
					self.g_next[i-1][j-1] != Block.Block.Empty and\
					self.g_next[i+1][j-1] != Block.Block.Empty) :
					#On trouve un puit ! On compte une case
					cpt += 1
					#puis on compte toute les autre en remontant le puit
					add = 2
					for k in range(j+1, gp.TAILLE_Y_LIMITE) :
						if self.g_next[i][k] == Block.Block.Empty and\
							self.g_next[i-1][k] != Block.Block.Empty and\
							self.g_next[i+1][k] != Block.Block.Empty :
							cpt += add
							add += 1
						else :
							break
					print("Puit en " + str(i) + " rapporte " + str(cpt))
					break


		#cas si le puit est tout à gauche
		for j in range(1, gp.TAILLE_Y_LIMITE) :
			if(self.g_next[0][j] == Block.Block.Empty and\
				self.g_next[0][j-1] != Block.Block.Empty and\
				self.g_next[1][j] != Block.Block.Empty and\
				self.g_next[1][j-1] != Block.Block.Empty) :
				#on détecte un puit, on compte un case
				cpt += 1
				#on remonte le puit
				add = 2
				for k in range(j+1, gp.TAILLE_Y_LIMITE) :
					if self.g_next[0][k] == Block.Block.Empty and\
						self.g_next[1][k] != Block.Block.Empty :
						cpt += add
						add += 1
					else :
						break
				print("Puit en " + str(0) + " rapporte " + str(cpt))
				break

		#cas tout à droite
		for j in range(1, gp.TAILLE_Y_LIMITE) :
			if(self.g_next[gp.TAILLE_X-1][j] == Block.Block.Empty and\
				self.g_next[gp.TAILLE_X-1][j-1] != Block.Block.Empty and\
				self.g_next[gp.TAILLE_X-2][j] != Block.Block.Empty and\
				self.g_next[gp.TAILLE_X-2][j-1] != Block.Block.Empty) :
				#on détecte un puit, on compte un case
				cpt += 1
				#on remonte le puit
				add = 2
				for k in range(j+1, gp.TAILLE_Y_LIMITE) :
					if self.g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
						self.g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
						cpt += add
						add += 1
					else :
						break
				print("Puit en " + str(0) + " rapporte " + str(cpt))
				break

		#coin gauche bas
		if self.g_next[0][0] == Block.Block.Empty and\
			self.g_next[1][0] != Block.Block.Empty :
			cpt += 1
			add = 2
			for k in range(1, gp.TAILLE_Y_LIMITE) :
				if self.g_next[0][k] == Block.Block.Empty and\
					self.g_next[1][k] != Block.Block.Empty :
						cpt += add
						add += 2
				else :
					break
			print("Puit en " + str(0) + " rapporte " + str(cpt))

		#coin droite bas
		if self.g_next[gp.TAILLE_X-1][0] == Block.Block.Empty and\
			self.g_next[gp.TAILLE_X-2][0] != Block.Block.Empty :
			cpt += 1
			add = 2
			for k in range(1, gp.TAILLE_Y_LIMITE) :
				if self.g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
					self.g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
						cpt += add
						add += 2
				else :
					break
			print("Puit en " + str(gp.TAILLE_X-1) + " rapporte " + str(cpt))

		return cpt

if __name__ == "__main__" :
	my_grid = [[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Red, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Red, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
	[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty]]

	h = Heuristic(None, my_grid, None)
	print(h.line_transition(), h.column_transition(), h.wells(), h.holes())