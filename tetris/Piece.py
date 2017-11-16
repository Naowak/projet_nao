# coding: utf-8
import numpy as np
import Block
import GlobalParameters as gp
import copy

Point = lambda x,y: np.array([[x,y]]).T

class Piece:
    kinds = {'O': [Point(-1/2,-1/2), Point(1/2,-1/2),\
                   Point(-1/2,1/2),  Point(1/2,1/2)],\
                   #Violet
             'I': [Point(-3/2,1/2),  Point(-1/2,1/2),\
                   Point(1/2,1/2),   Point(3/2,1/2)],\
                   #Rouge
             'L': [Point(-1,0),      Point(0,0),\
                   Point( 1,0),      Point(1,1)],\
                   #Green
             'T': [Point(-1,0),      Point(0,0),\
                   Point( 0,1),      Point(1,0)],\
                   #Orange
             'S': [Point(-1,0),      Point(0,0),\
                   Point( 0,1),      Point(1,1)]}
                   #Cyan
    symmetry = np.array([[-1,0],[0,1]]).dot
    kinds['Z'] = list(map(symmetry, kinds['S']))
    #blue
    kinds['J'] = list(map(symmetry, kinds['L']))
    #Yellow

    centers_init = {'O' : Point((gp.TAILLE_X-1)/2 + 0.5, gp.TAILLE_Y-2.5),
                    'I' : Point((gp.TAILLE_X-1)/2 + 0.5, gp.TAILLE_Y-2.5),
                    'L' : Point((gp.TAILLE_X-1)/2, gp.TAILLE_Y-2),
                    'T' : Point((gp.TAILLE_X-1)/2, gp.TAILLE_Y-2),
                    'S' : Point((gp.TAILLE_X-1)/2, gp.TAILLE_Y-2),
                    'Z' : Point((gp.TAILLE_X-1)/2, gp.TAILLE_Y-2),
                    'J' : Point((gp.TAILLE_X-1)/2, gp.TAILLE_Y-2)}

    blocks_controls = {'O' : Point(-1/2, -1/2),
                     'I' : Point(-3/2, 1/2),
                     'L' : Point(-1, 0),
                     'T' : Point(-1, 0),
                     'S' : Point(-1, 0),
                     'Z' : Point(-1, 1),
                     'J' : Point(-1, 1)} # A REVOIR

    colors = {'O': Block.Block.Violet,
              'I': Block.Block.Red,
              'L': Block.Block.Green,
              'T': Block.Block.Orange,
              'S': Block.Block.Cyan,
              'Z': Block.Block.Blue,
              'J': Block.Block.Yellow}

    def __init__(self, center):
        self.center = center
        self.blocks = []
        self.kind = ""
        self.block_control = None
        self.color = ""

    @classmethod
    def factory(cls, kind, center):
        p = Piece(center)
        p.kind = kind
        p.blocks = cls.kinds[kind]
        p.color = cls.colors[kind]
        p.block_control = copy.copy(Piece.blocks_controls[kind])
        return p

    def rotate(self) :
        new_blocks = []
        coef = np.array([[0, 1], [-1, 0]])
        for b in self.blocks :
          new_blocks.append(np.dot(coef, b))
        self.blocks = new_blocks
        self.block_control = np.dot(coef, self.block_control)
