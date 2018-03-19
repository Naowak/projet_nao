import copy
import random
import sys
sys.path.append("../")
sys.path.append("../../")
import GlobalParameters as gp
from Jeu import Block
from Jeu import State
from Jeu import Piece


def copy_grid(grid):
    size = (len(grid), len(grid[0]))
    new_grid = list()
    for i in range(size[0]):
        new_grid += [list()]
        for j in range(size[1]):
            new_grid[i] += [copy.copy(grid[i][j])]
    return new_grid

def best_move(heuristic, weights, state):
        pieces = copy.copy(state["pieces"])
        scores_valid = []
        scores_non_valid = []
        compteur = 0

        for kind in pieces:
            for rotation in range(0, 4, 1):
                for move in range(-5, 5, 1):
                    play = {"choose": kind,
                            "rotate": rotation, "hor_move": move}
                    grid_tmp = State.State(copy_grid(state["grid"]))
                    grid_prec = State.State(copy_grid(state["grid"]))
                    p = Piece.Piece.factory(
                        kind, copy.copy(Piece.Piece.centers_init[kind]))
                    for _ in range(rotation):
                        p.rotate()
                    if(State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + move)):
                        p.center[0] += move
                        r = grid_tmp.drop_piece(p, 0)
                        if r :
                            #ne prends pas en compte les coups perdants
                            scores_valid += [[play,
                                        evaluate_play(grid_prec, grid_tmp, play, weights, heuristic)]]
                        else :
                            #prends tous les coups perdants
                            scores_non_valid += [[play,
                                        evaluate_play(grid_prec, grid_tmp, play, weights, heuristic)]]

        scores = []
        if len(scores_valid) > 0 :
            #On ne veut choisir un play que parmis ceux qui ne font pas perdre
            scores = scores_valid
        else :
            #s'il n'existe pas de play valid, alors on doit en choisir un parmis tous ceux qui font perdre
            scores = scores_non_valid

        scores.sort(key=lambda x: x[1], reverse=True)
        best = scores[0][1]
        best_plays = []
        for s in scores:
            if s[1] >= best:
                best_plays += [s]
        play_send = random.choice(best_plays)[0]
        return play_send

#retourne le coup d'un play en fonction des heuristics choisi pour le calculer
def evaluate_play(grid_prec, grid_next, action, weights, heuristic) :
        tot = 0
        for i,func in enumerate(heuristic):
            tot += weights[i]*func(grid_prec,grid_next,action)
        return tot

#Calcul du nombre de cellule vide inaccessible (recouverte par un block plein)
def hidden_empty_cells(g_prec, g_next, action) :
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE) :
            if g_next.grid[i][j] == Block.Block.Empty :
                for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                    if g_next.grid[i][k] != Block.Block.Empty :
                        cpt += 1
                        break
    return cpt

#Return the score won by the latest action
def score(g_prec, g_next, action) :
    a = g_next.score[0] - g_prec.score[0]
    b = g_next.score[1] - g_prec.score[1]
    if a != 0 :
        return a
    return b
    
#Return the latest action's height
def height(g_prec, g_next, action) :
    kind = action["choose"]
    rotation = action["rotate"]
    hor_move = action["hor_move"]

    p = Piece.Piece.factory(kind, copy.copy(Piece.Piece.centers_init[kind]))
    etat = State.State(g_prec.grid)
    hauteur = 0
    for _ in range(rotation) :
        p.rotate()

    if(State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + hor_move)):
        p.center[0] += hor_move
        r = etat.drop_piece(p, 0)
        for b in p.blocks : 
            h_tmp = p.center[1] + b[1]
            if h_tmp > hauteur :
                hauteur = h_tmp
        return hauteur
    return gp.TAILLE_Y_LIMITE - 1

#Retourne the sum of each column hight
def agregate_height(g_prec, g_next, action) :
    etat = State.state(g_next)
    somme = 0
    for i in range(gp.TAILLE_X) :
        for j in reverse(list(range(gp.TAILLE_Y_LIMITE-1))) :
            if etat.grid[i][j] != Block.Block.Empty :
                somme += j
                break
    return somme


#(number of line last action)*(number of cells eliminated from the last piece)
def erosion(g_prec, g_next, action):
    kind = action["choose"]
    rotation = action["rotate"]
    hor_move = action["hor_move"]

    #on recréer la piece et l'état précédent
    p = Piece.Piece.factory(kind, copy.copy(Piece.Piece.centers_init[kind]))
    etat = State.State(g_prec.grid)
    hauteur = 0
    for _ in range(rotation) :
        p.rotate()

    #si elle dépasse, return 0
    if(not State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + hor_move)):
        return 0

    #on descend la piece
    p.center[0] += hor_move
    while not etat.is_piece_blocked(p):
        p.center[1] -= 1

    #on calcul tous les indices d'ordonne de la piece qui est tombé
    indices_ordonnee_piece = []
    for block in p.blocks:
        indices_ordonnee_piece += [int(p.center[1] + block[1])]
        etat.grid[int(p.center[0] + block[0])
                  ][int(p.center[1] + block[1])] = p.color
    set_ordonnee_piece = list(set(indices_ordonnee_piece))

    #on compte le nombre de block détruit et le nombre de ligne réalisées.
    nb_block_detruit = 0
    nb_lines_complete = 0
    for j in set_ordonnee_piece :
        line_complete = True
        for i in range(gp.TAILLE_X) :
            if etat.grid[i][j] == Block.Block.Empty :
                line_complete = False
        if line_complete :
            nb_lines_complete += 1
            nb_block_detruit += indices_ordonnee_piece.count(j)

    return nb_lines_complete*nb_block_detruit




#number of empty/filled or filled/empty cells transition
def line_transition(g_prec, g_next, action):
    cpt = 0
    for j in range(gp.TAILLE_Y_LIMITE):
        for i in range(gp.TAILLE_X - 1) :
            if(g_next.grid[i][j] == Block.Block.Empty and g_next.grid[i+1][j] != Block.Block.Empty) or\
                (g_next.grid[i][j] != Block.Block.Empty and g_next.grid[i+1][j] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of empty/filled or filled/empty cells transition
def column_transition(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE-1) :
            if(g_next.grid[i][j] == Block.Block.Empty and g_next.grid[i][j+1] != Block.Block.Empty) or\
                (g_next.grid[i][j] != Block.Block.Empty and g_next.grid[i][j+1] == Block.Block.Empty) :
                cpt += 1
    return cpt

#number of holes
def holes(g_prec, g_next, action):
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE) :
            if(g_next.grid[i][j] == Block.Block.Empty) :
                is_hole = True
                try :
                    if(g_next.grid[i][j+1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next.grid[i][j-1] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next.grid[i+1][j] == Block.Block.Empty) :
                        is_hole = False
                except IndexError :
                    pass
                try :
                    if(g_next.grid[i-1][j] == Block.Block.Empty) :
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
            if( g_next.grid[i][j] == Block.Block.Empty and\
                g_next.grid[i-1][j] != Block.Block.Empty and\
                g_next.grid[i+1][j] != Block.Block.Empty and\
                g_next.grid[i][j-1] != Block.Block.Empty and\
                g_next.grid[i-1][j-1] != Block.Block.Empty and\
                g_next.grid[i+1][j-1] != Block.Block.Empty) :
                #On trouve un puit ! On compte une case
                cpt += 1
                #puis on compte toute les autre en remontant le puit
                add = 2
                for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                    if g_next.grid[i][k] == Block.Block.Empty and\
                        g_next.grid[i-1][k] != Block.Block.Empty and\
                        g_next.grid[i+1][k] != Block.Block.Empty :
                        cpt += add
                        add += 1
                    else :
                        break
                break


    #cas si le puit est tout à gauche
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next.grid[0][j] == Block.Block.Empty and\
            g_next.grid[0][j-1] != Block.Block.Empty and\
            g_next.grid[1][j] != Block.Block.Empty and\
            g_next.grid[1][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next.grid[0][k] == Block.Block.Empty and\
                    g_next.grid[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            break

    #cas tout à droite
    for j in range(1, gp.TAILLE_Y_LIMITE) :
        if(g_next.grid[gp.TAILLE_X-1][j] == Block.Block.Empty and\
            g_next.grid[gp.TAILLE_X-1][j-1] != Block.Block.Empty and\
            g_next.grid[gp.TAILLE_X-2][j] != Block.Block.Empty and\
            g_next.grid[gp.TAILLE_X-2][j-1] != Block.Block.Empty) :
            #on détecte un puit, on compte un case
            cpt += 1
            #on remonte le puit
            add = 2
            for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                if g_next.grid[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                    g_next.grid[gp.TAILLE_X-2][k] != Block.Block.Empty :
                    cpt += add
                    add += 1
                else :
                    break
            break

    #coin gauche bas
    if g_next.grid[0][0] == Block.Block.Empty and\
        g_next.grid[1][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next.grid[0][k] == Block.Block.Empty and\
                g_next.grid[1][k] != Block.Block.Empty :
                    cpt += add
                    add += 2
            else :
                break

    #coin droite bas
    if g_next.grid[gp.TAILLE_X-1][0] == Block.Block.Empty and\
        g_next.grid[gp.TAILLE_X-2][0] != Block.Block.Empty :
        cpt += 1
        add = 2
        for k in range(1, gp.TAILLE_Y_LIMITE) :
            if g_next.grid[gp.TAILLE_X-1][k] == Block.Block.Empty and\
                g_next.grid[gp.TAILLE_X-2][k] != Block.Block.Empty :
                    cpt += add
                    add += 2
            else :
                break
    return cpt


if __name__ == "__main__" :
    my_grid = [[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Red, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty]]

    action = {"hor_move" : 1, "choose" : 'L', "rotate" : 1}
    # etat = State.State(my_grid)
    # etat.score[0] = 125
    # etat.score[1] = 168
    # print(etat)

    # etat2 = State.State(my_grid)
    # etat2.score[0] = 125
    # etat2.score[1] = 365
    # print(score(etat, etat2, None))

    etat = State.State(my_grid)
    print(etat)
    print("Erosion : ", erosion(etat, None, action))

