# coding: utf-8
import sys
sys.path.append('../')
import copy

import GlobalParameters as gp
from Jeu import Block

def copy_grid(grid) :
    """Retourne une copie de la grille passée en paramètre.

    Attributs :
        -grid : liste de deux dimensions"""    
    size = (len(grid), len(grid[0]))
    new_grid = list()
    for i in range(size[0]) :
        new_grid += [list()]
        for j in range(size[1]) :
            new_grid[i] += [grid[i][j]]
    return new_grid

class State:
    """State repérésente l'Etat du Jeu (la grille du jeu)."""
    
    grid_init = [[Block.Block.Empty]*gp.TAILLE_Y for i in range(gp.TAILLE_X)]

    def __init__(self, grid = grid_init):
        """Retourne une nouvelle grille, si grid != None, retourne une copie de grid.

        Attributs :
            -grid : liste deux dimensions"""
        self.grid = copy_grid(grid)
        self.score = [0]*gp.NOMBRE_DE_JOUEUR    
        self.indices_lines_complete_this_turn = list()

    def drop_piece(self, piece, player):
        """Fait tomber une pièce dans la grille, si celle-ci réalise une (ou plusieurs)
        lignes, le joueur player passé en paramètre gagne les points.

        Attributs :
            - piece : instance Piece
            - player : int représentant l'ID du joueur"""
        self.clear_rotation_vue()
        while not self.is_piece_blocked(piece):
            piece.center[1] -= 1
        for block in piece.blocks:
            self.grid[int(piece.center[0] + block[0])
                      ][int(piece.center[1] + block[1])] = piece.color
        if not is_piece_accepted_ordonne(piece):
            return False
        [nb_ligne_delete, indices] = self.line_complete()
        self.indices_lines_complete_this_turn = indices
        self.maj_score(nb_ligne_delete, player)
        return True

    def clear_rotation_vue(self):
        """Nettoi la zone de rotation et de placement des pièces (les 4 lignes du dessus), 
        ce qui reviens à supprimer toutes pîèces dans cette zone."""
        for j in range(gp.TAILLE_Y_LIMITE, gp.TAILLE_Y):
            for i in range(gp.TAILLE_X):
                self.grid[i][j] = Block.Block.Empty

    def piece_show(self, piece):
        """Ajoute une pièce dans la grille, la pièce est placé en piece.center.

        Attributs :
            - piece : instance Piece"""
        self.clear_rotation_vue()
        for block in piece.blocks:
            self.grid[int(block[0] + piece.center[0])
                      ][int(block[1] + piece.center[1])] = piece.color

    def show_abscisse(self, piece, abscisse):
        """ Déplace une pièce horizontalement en fonction de abscisse.

        Attributs :
            - piece : instance Piece
            - abscisse : int (négatif pour déplacement à gauche par rapport au centre, 
                        positif pour un déplacement à droite du centre."""
        if is_piece_accepted_abscisse(piece, abscisse):
            self.clear_rotation_vue()
            for block in piece.blocks:
                self.grid[int(abscisse + block[0] - piece.block_control[0])
                          ][int(block[1] + piece.center[1])] = piece.color

    def maj_score(self, nb_ligne_delete, player):
        """Ajoute au score du joueur player les points correspondants au nombre de lignes réalisées.

        Attributs :
            - nb_ligne_delete : int représentant le nombre de ligne réalisées.
            - player : int représentant l'ID du joueur."""
        if nb_ligne_delete == 1:
            self.score[player] += 40
        elif nb_ligne_delete == 2:
            self.score[player] += 100
        elif nb_ligne_delete == 3:
            self.score[player] += 300
        elif nb_ligne_delete == 4:
            self.score[player] += 1200

    def is_piece_blocked(self, piece):
        """Vérifie si une pièce est bloquée ou non (si elle ne peut plus descendre plus bas ou non).

        Attributs :
            - piece : instance Piece.

        Retour : 
            - boolean : True si la piece est bloquée, False sinon"""
        for block in piece.blocks:
            # Arrive en bas de la grille
            if piece.center[1] + block[1] == 0:
                return True
            #La case en dessous n'est pas vide
            if self.grid[int(piece.center[0] + block[0])][int(piece.center[1] + block[1] - 1)] != Block.Block.Empty :
                return True
        return False

    def line_complete(self):
        """Vérifie si des lignes sont complètes dans la grille, si oui gère la suppression de celles-ci et les compte.

        Retour :
            - int : nombre de lignes réalisées
	    - liste int : indices des lignes réalisées"""
        j = 0
        compteur = 0
        indices = []
        while j < gp.TAILLE_Y_LIMITE:
            test = True
            for i in range(gp.TAILLE_X):
                if(Block.Block.Empty == self.grid[i][j]):
                    test = False
            if test:
                # ligne numero j complète
                indices += [j + len(indices)]
                compteur += 1
                for k in range(j + 1, gp.TAILLE_Y_LIMITE):
                    for i in range(gp.TAILLE_X):
                        # On descend tout ce qui est au dessus de j
                        self.grid[i][k - 1] = self.grid[i][k]
                for i in range(gp.TAILLE_X):
                    # on a tout descendu, donc la ligne du dessus est propre.
                    self.grid[i][gp.TAILLE_Y_LIMITE - 1] = Block.Block.Empty
            else:
                # si l'on a supprimé la ligne j, \
                                # pas besoin d'augmenter d'ordonnee (ce serait une erreur)
                j += 1
        return compteur, indices

    def __str__(self):
        """Retourne un string représentant l'état actuel."""
        string = ""
        for i in range(gp.TAILLE_X):
            string += str(i) + " "
        string += "\n"
        for i in range(gp.TAILLE_X):
            string += "--"
        string += "\n"
        for j in reversed(range(gp.TAILLE_Y_LIMITE, gp.TAILLE_Y)):
            for i in range(gp.TAILLE_X):
                color = self.grid[i][j][0]
                if color == 'W':
                    color = '_'
                string += str(color) + " "
            string += "\n"
        for i in range(gp.TAILLE_X):
            string += "--"
        string += "\n"
        for j in reversed(range(gp.TAILLE_Y_LIMITE)):
            for i in range(gp.TAILLE_X):
                color = self.grid[i][j][0]
                if color == 'W':
                    color = '_'
                string += str(color) + " "
            string += "\n"
        string += "SCORE:: " + str(self.score) + "\n"
        return string

    def encode_to_json(self, piece):
        """Convertit en json l'état

        Retourne :
            - json : représantant une instance State"""
        coord_blocks = []
        my_piece = copy.copy(piece)
        while not self.is_piece_blocked(my_piece):
            my_piece.center[1] -= 1
        for block in my_piece.blocks:
            coord_blocks += [[int(my_piece.center[0] + block[0]), int(my_piece.center[1] + block[1])]]
       

        serialize = {"score":self.score, "grid":[[j for j in i] for i in self.grid], \
         "lines_complete_this_turn" : self.indices_lines_complete_this_turn, \
         "preview" : coord_blocks}
        
        #ATTENTION : moyen pas beau d'envoyer les lignes correctement au serveur
        #à corriger potentiellement plus tard
        if len(self.indices_lines_complete_this_turn) > 0 :
            self.indices_lines_complete_this_turn = []
        return serialize

    


def is_piece_accepted_ordonne(piece):
    """Vérifie si une pièce a une ordonnée valide.

    Attributs : 
        - piece : instance Piece

    Retour :
        - boolean : True si l'ordonnée de la piece est valide,
                    False sinon."""
    for block in piece.blocks:
        if int(piece.center[1] + block[1]) >= gp.TAILLE_Y_LIMITE:
            return False
    return True


def is_piece_accepted_abscisse(piece, abscisse):
    """Vérifie si une pièce a une abscisse valide.

    Attributs :
        - piece : instance Piece

    Retour :
        - boolean : True si l'abscisse de la piece est valide,
                    False sinon."""
    for block in piece.blocks:
        if abscisse + block[0] - piece.block_control[0] \
                >= gp.TAILLE_X or abscisse + block[0] - piece.block_control[0] < 0:
            return False
    return True
