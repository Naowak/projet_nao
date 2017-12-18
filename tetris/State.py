# coding: utf-8
import Block

import GlobalParameters as gp

class State:
    def __init__(self):
        self.grid = [[Block.Block.Empty]*gp.TAILLE_Y for i in range(gp.TAILLE_X)]
        self.score = [0]*gp.NOMBRE_DE_JOUEUR

    def drop_piece(self, piece, player):
        self.clear_rotation_vue()
        while not self.is_piece_blocked(piece):
            piece.center[1] -= 1
        #if self.is_piece_accepted_ordonne(piece):
        for block in piece.blocks:
            self.grid[int(piece.center[0] + block[0])]\
			[int(piece.center[1] + block[1])] = piece.color
        if not is_piece_accepted_ordonne(piece):
            return False
        nb_ligne_delete = self.line_complete()
        self.maj_score(nb_ligne_delete, player)
        return True

    def clear_rotation_vue(self):
        for j in range(gp.TAILLE_Y_LIMITE, gp.TAILLE_Y):
            for i in range(gp.TAILLE_X):
                self.grid[i][j] = Block.Block.Empty

    def piece_show(self, piece):
        self.clear_rotation_vue()
        for block in piece.blocks: 
            if block[0] == piece.block_control[0] and block[1] == piece.block_control[1]:
                self.grid[int(block[0] + piece.center[0])]\
				[int(block[1] + piece.center[1])] = Block.Block.Black
            else:
                self.grid[int(block[0] + piece.center[0])]\
				[int(block[1] + piece.center[1])] = piece.color

    def show_abscisse(self, piece, abscisse):
        if is_piece_accepted_abscisse(piece, abscisse):
            self.clear_rotation_vue()
            for block in piece.blocks:
                self.grid[int(abscisse + block[0] - piece.block_control[0])]\
				[int(block[1] + piece.center[1])] = piece.color

    def maj_score(self, nb_ligne_delete, player):
        if nb_ligne_delete == 1:
            self.score[player] += 40
        elif nb_ligne_delete == 2:
            self.score[player] += 100
        elif nb_ligne_delete == 3:
            self.score[player] += 300
        elif nb_ligne_delete == 4:
            self.score[player] += 1200

    def is_piece_blocked(self, piece):
        for block in piece.blocks:
            #Arrive en bas de la grille
            if piece.center[1] + block[1] == 0:
                return True
            #La case en dessous n'est pas vide
            if self.grid[int(piece.center[0] + block[0])]\
			[int(piece.center[1] + block[1] - 1)] != Block.Block.Empty:
                return True
        return False

    def line_complete(self):
        j = 0
        compteur = 0
        while j < gp.TAILLE_Y_LIMITE:
            test = True
            for i in range(gp.TAILLE_X):
                if self.grid[i][j] == Block.Block.Empty:
                    #ligne pas complète
                    test = False
            if test:
                #ligne numero j complète
                compteur += 1
                for k in range(j+1, gp.TAILLE_Y_LIMITE - 1):
                    for i in range(gp.TAILLE_X):
                        #On descend tout ce qui est au dessus de j
                        self.grid[i][k-1] = self.grid[i][k]
                for i in range(gp.TAILLE_X):
                    #on a tout descendu, donc la ligne du dessus est propre.
                    self.grid[i][gp.TAILLE_Y_LIMITE-1] = Block.Block.Empty
            else:
                #si l'on a supprimé la ligne j, \
				# pas besoin d'augmenter d'ordonnee (ce serait une erreur)
                j += 1
        return compteur


    def __str__(self):
        string = ""
        for i in range(gp.TAILLE_X):
            string += str(i) + " "
        string += "\n"
        for i in range(gp.TAILLE_X):
            string += "--"
        string += "\n"
        for j in reversed(range(gp.TAILLE_Y_LIMITE, gp.TAILLE_Y)):
            for i in range(gp.TAILLE_X):
                color = self.grid[i][j].value[0]
                if color == 'W':
                    color = '_'
                string += color + " "
            string += "\n"
        for i in range(gp.TAILLE_X):
            string += "--"
        string += "\n"
        for j in reversed(range(gp.TAILLE_Y_LIMITE)):
            for i in range(gp.TAILLE_X):
                color = self.grid[i][j].value[0]
                if color == 'W':
                    color = '_'
                string += color + " "
            string += "\n"
        string += "SCORE:: " + str(self.score) + "\n"
        return string

    def encode_to_json(self):
        serialize = {"score":self.score, "grid":[[j.value for j in i] for i in self.grid]}
        return serialize


def is_piece_accepted_ordonne(piece):
    for block in piece.blocks:
        if int(piece.center[1] + block[1]) >= gp.TAILLE_Y_LIMITE:
            return False
    return True


def is_piece_accepted_abscisse(piece, abscisse):
    for block in piece.blocks:
        if abscisse + block[0] - piece.block_control[0] \
                >= gp.TAILLE_X or abscisse + block[0] - piece.block_control[0] < 0:
            return False
    return True
