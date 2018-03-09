# coding: utf-8
import sys
sys.path.append('../')
import copy

import numpy as np

from Jeu import Block
import GlobalParameters as gp


def Point(x, y) :
    """ Retourne un tableau représentant les coordonnées de nos blocks,

    Attributs :
        - x : int / abscisse 
        - y : int / ordonnee

    Retourne :
        - numpy.array : tableau 2D de coordonnée"""
    return np.array([[x, y]]).T


class Piece:
    """Défini chacune des différentes pièces qui peuvent être jouer dans
    le tetris : O, I, L, T, S, Z, J"""
    kinds = {'O': [Point(-1 / 2, -1 / 2), Point(1 / 2, -1 / 2),
                   Point(-1 / 2, 1 / 2), Point(1 / 2, 1 / 2)], \
             # Violet
             'I': [Point(-3 / 2, 1 / 2), Point(-1 / 2, 1 / 2), \
                   Point(1 / 2, 1 / 2), Point(3 / 2, 1 / 2)], \
             # Rouge
             'L': [Point(-1, 0), Point(0, 0), \
                   Point(1, 0), Point(1, 1)], \
             # Green
             'T': [Point(-1, 0), Point(0, 0), \
                   Point(0, 1), Point(1, 0)], \
             # Orange
             'S': [Point(-1, 0), Point(0, 0), \
                   Point(0, 1), Point(1, 1)], \
             # Cyan
             'Z': [Point(-1, 1), Point(0, 0), \
                   Point(0, 1), Point(1, 0)], \
             # Blue
             'J': [Point(-1, 0), Point(1, 0), \
                   Point(0, 0), Point(-1, 1)]}
    # Yellow

    centers_init = {'O': Point((gp.TAILLE_X - 1) / 2 + 0.5, gp.TAILLE_Y - 2.5),
                    'I': Point((gp.TAILLE_X - 1) / 2 + 0.5, gp.TAILLE_Y - 2.5),
                    'L': Point((gp.TAILLE_X - 1) / 2, gp.TAILLE_Y - 2),
                    'T': Point((gp.TAILLE_X - 1) / 2, gp.TAILLE_Y - 2),
                    'S': Point((gp.TAILLE_X - 1) / 2, gp.TAILLE_Y - 2),
                    'Z': Point((gp.TAILLE_X - 1) / 2, gp.TAILLE_Y - 2),
                    'J': Point((gp.TAILLE_X - 1) / 2, gp.TAILLE_Y - 2)}

    blocks_controls = {'O': Point(-1 / 2, -1 / 2),
                       'I': Point(-3 / 2, 1 / 2),
                       'L': Point(-1, 0),
                       'T': Point(-1, 0),
                       'S': Point(-1, 0),
                       'Z': Point(-1, 1),
                       'J': Point(-1, 0)}  # A REVOIR

    colors = {'O': Block.Block.Violet,
              'I': Block.Block.Red,
              'L': Block.Block.Green,
              'T': Block.Block.Orange,
              'S': Block.Block.Cyan,
              'Z': Block.Block.Blue,
              'J': Block.Block.Yellow}

    def __init__(self, center):
        """Créer une pièce, centrée en center.

        Attributs :
            - center : tableau 2D de coordonnée, généralement égale à 
                        Piece.centers_init[kind]

        Retour :
            - piece : instance Piece / nouvelle piece"""
        self.center = center
        self.blocks = []
        self.kind = ""
        self.block_control = None
        self.color = ""

    @classmethod
    def factory(cls, kind, center):
        """Méthode de classe, retourne une nouvelle pièce de type kind
        et centrée en center.

        Attributs :
            - kind : string parmi ["O", "I", "L", "T", "S", "Z", "J"]
            - center : coordonnee 2D.

        Retourne :
            - piece : instance Piece / nouvelle piece"""
        piece = Piece(center)
        piece.kind = kind
        piece.blocks = cls.kinds[kind]
        piece.color = cls.colors[kind]
        piece.block_control = copy.copy(Piece.blocks_controls[kind])
        return piece

    def rotate(self):
        """Fait tourner une pièce dans le sens des aiguillles d'une montre"""
        new_blocks = []
        coef = np.array([[0, 1], [-1, 0]])
        test = True
        for b in self.blocks :
          new_blocks.append(np.dot(coef, b))
        for b in new_blocks :
            if (b[0] + self.center[0]) > 9 or (b[0] + self.center[0]) < 0 :
              #print("ad :", b[0])
              test = False
        if test :
          self.blocks = new_blocks
          self.block_control = np.dot(coef, self.block_control)

    def __str__(self) :
      """Retourne une description str d'une pièce.

      Retourne :
        - string : représente la pièce et ses informations."""
      string = "[Kinds : " + self.kind
      string += ", Blocks : " + str(self.blocks)
      string += ", Center : " + str(self.center)
      string += "]"
      return string
