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
        pass

class Heuristic :
    def __init__(self, grid_prec, grid_next, action) :
        self.g_next = grid_next
        self.g_prec = grid_prec
        self.action = action

#Return the latest action's height
def height(g_prec, g_next, action) :
    pass

#(number of line last action)*(number of cells eliminated from the las piece)
def erosion(g_prec, g_next, action):
    pass

#number of empty/filled or filled/empty cells transition
def line_transition(g_prec, g_next, action):
    cpt = 0
    for j in range(gp.TAILLE_Y_LIMITE) :
        for i in range(gp.TAILLE_X - 1) :
            if(g_next[i][j] == Block.Block.Empty and g_next[i+1][j] != Block.Block.Empty) or\
                (g_next[i][j] != Block.Block.Empty and g_next[i+1][j] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of empty/filled or filled/empty cells transition
def column_transition(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE-1) :
            if(g_next[i][j] == Block.Block.Empty and g_next[i][j+1] != Block.Block.Empty) or\
                (g_next[i][j] != Block.Block.Empty and g_next[i][j+1] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of holes
def holes(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE) :
            if(g_next[i][j] == Block.Block.Empty) :
                is_hole = True
                try :
                    if(g_next[i][j+1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i][j-1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i+1][j] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next[i-1][j] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                if is_hole :
                    cpt += 1
    return cpt

#number of wells :
def wells(g_prec, g_next, action) :
    cpt = 0
    #on compte les puits dans l'intérieur de la grille (attention dépassement indice)
    for i in range(1, gp.TAILLE_X-1) :
        for j in range(1, gp.TAILLE_Y_LIMITE) :
            #si on est à la source d'un puit
            if( g_next[i][j] == Block.Block.Empty and\
                g_next[i-1][j] != Block.Block.Empty and\
                g_next[i+1][j] != Block.Block.Empty and\
                g_next[i][j-1] != Block.Block.Empty and\
                g_next[i-1][j-1] != Block.Block.Empty and\
                g_next[i+1][j-1] != Block.Block.Empty) :
                #On trouve un puit ! On compte une case
                cpt += 1
                #puis on compte toute les autre en remontant le puit
                add = 2
                for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                    if g_next[i][k] == Block.Block.Empty and\
                        g_next[i-1][k] != Block.Block.Empty and\
                        g_next[i+1][k] != Block.Block.Empty :
                        cpt += add
                        add += 1
                    else :
                        break
                print("Puit en " + str(i) + " rapporte " + str(cpt))
                break


    #cas si le puit est tout à gauche
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next[0][j] == Block.Block.Empty and\
            g_next[0][j-1] != Block.Block.Empty and\
            g_next[1][j] != Block.Block.Empty and\
            g_next[1][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next[0][k] == Block.Block.Empty and\
                    g_next[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            print("Puit en " + str(0) + " rapporte " + str(cpt))
            break

    #cas tout à droite
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next[gp.TAILLE_X-1][j] == Block.Block.Empty and\
            g_next[gp.TAILLE_X-1][j-1] != Block.Block.Empty and\
            g_next[gp.TAILLE_X-2][j] != Block.Block.Empty and\
            g_next[gp.TAILLE_X-2][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                    g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            print("Puit en " + str(0) + " rapporte " + str(cpt))
            break

    #coin gauche bas
    if g_next[0][0] == Block.Block.Empty and\
        g_next[1][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next[0][k] == Block.Block.Empty and\
                g_next[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 2
            else :
                break
        print("Puit en " + str(0) + " rapporte " + str(cpt))

    #coin droite bas
    if g_next[gp.TAILLE_X-1][0] == Block.Block.Empty and\
        g_next[gp.TAILLE_X-2][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                g_next[gp.TAILLE_X-2][k] != Block.Block.Empty :
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
