
# coding: utf-8

# In[128]:

import enum
import json
import functools as ft
import numpy as np
import itertools as it
from collections import namedtuple, defaultdict
from fractions import Fraction


# In[67]:

Point = lambda x,y: np.array([[x,y]]).T


# In[68]:

class Block(enum.Enum):
    Empty = ""
    Red = "red"
    Blue = "blue"
    Green = "green"
    #...


# In[106]:

class Piece:    
    kinds = {'O': [Point(-1/2,-1/2), Point(1/2,-1/2),
                   Point(-1/2,1/2),  Point(1/2,1/2)],
             'I': [Point(-3/2,1/2),  Point(-1/2,1/2),
                   Point(1/2,1/2),   Point(3/2,1/2)],
             'L': [Point(-1,0),      Point(0,0),
                   Point( 1,0),      Point(1,1)],
             'T': [Point(-1,0),      Point(0,0),
                   Point( 0,1),      Point(1,0)],
             'S': [Point(-1,0),      Point(0,0),
                   Point( 0,1),      Point(1,0)]}
    symmetry = np.array([[-1,0],[0,1]]).dot
    kinds['Z'] = list(map(symmetry, kinds['S']))
    kinds['J'] = list(map(symmetry, kinds['L']))
    
    colors = {'O': Block.Red,
              'I': Block.Red,
              'L': Block.Red,
              'T': Block.Red,
              'S': Block.Red,
              'Z': Block.Red,
              'J': Block.Red}
    
    def __init__(self, center):
        self.center = center
        self.blocks = []
    
    @classmethod
    def factory(cls, kind, center):
        p = Piece(center)
        p.blocks = cls.kinds[kind]
        return p
    
    def blocks_abs(self):
        return [(p+self.center) for p in self.blocks]


# In[140]:

class State:
    def __init__(self):
        


# In[ ]:



