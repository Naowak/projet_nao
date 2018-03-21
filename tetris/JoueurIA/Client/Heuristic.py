import copy
import random
import sys
sys.path.append("../")
sys.path.append("../../")
import GlobalParameters as gp
from Jeu import Block
from Jeu import State
from Jeu import Piece


""" Dans ce fichier sont écrites toutes les heuristiques utilisées dans nos IA,
ainsi que quelques fonctions utiles à leurs bon fonctionnement.
Les heuristiques prennent toutes la forme :
	def mon_heuristique(grid_prec, grid_next, action) :
Où grid_prec est l'instance State.State avant le coup joué,
grid_next est l'instance State.State après le coup joué,
action est le coup jouer sous la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move}.
Tel que, si l'état actuel du jeu est grid_prec, et que l'on joue l'action action, on arrive dans 
l'état grid_next."""


def copy_grid(grid):
    """ Créer une copie d'une grille du jeu, et la retourne.
    
    Paramètres :
        - grid : liste double entrée : représente la grille du jeu.

    Retour :
        liste double entrée : Copie de grid """

    size = (len(grid), len(grid[0]))
    new_grid = list()
    for i in range(size[0]):
        new_grid += [list()]
        for j in range(size[1]):
            new_grid[i] += [copy.copy(grid[i][j])]
    return new_grid

def best_move(heuristic, weights, state):
        """ Teste toutes les coups et retourne le meilleurs selon les heuristiques et 
        l'état du jeu.
        
        Paramètres :
            - heuristic : liste de fonction : chaque fonction de la liste représente une heuristic
                et est de la forme : fonction(grid_prec, grid_next, action) .
            - weights : liste de poids (float) : cette liste doit être de la même taille que heuristic.
                Chaque poids indicé i dans la liste sera associé à l'heuristique indicée i.
            - state :  instance State.State : représente l'état du jeu au moment de choisir le l'action

        Retour :
            dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
               Représente la meilleur action calculée en fonction des heuristiques."""
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

def evaluate_play(grid_prec, grid_next, action, weights, heuristic) :
        """ Retourne la valeur d'un play en fonction des heuristiques choisies pour la calculer. 
            
            Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.
                - weights : liste de float : poids des heuristiques
                - heuristic : liste de fonction : fonctions représentants les heuristiques.

            Retour : 
                float : valeur du coup"""
        tot = 0
        for i,func in enumerate(heuristic):
            tot += weights[i]*func(grid_prec,grid_next,action)
        return tot

def hidden_empty_cells(g_prec=None, g_next, action=None) :
    """ Heuristique calculant le nombre de cellule vide inaccessible (recouverte par un block plein).
        Heuristiques post-action.
        
        Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        Retour :
            int : nombre de cellule vide"""
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE) :
            if g_next.grid[i][j] == Block.Block.Empty :
                for k in range(j+1, gp.TAILLE_Y_LIMITE) :
                    if g_next.grid[i][k] != Block.Block.Empty :
                        cpt += 1
                        break
    return cpt


def score(g_prec=None, g_next, action=None) :
    """ Heuristique qui retourne le score rapporté par le dernier coup.
        Heuristique post-action.

        Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        retour :
            int : score gagné        
        """
    a = g_next.score[0] - g_prec.score[0]
    b = g_next.score[1] - g_prec.score[1]
    if a != 0 :
        return a
    return b
    

def height(g_prec, g_next, action) :
    """ Heuristique qui retourne la hauteur du dernier coup joué.

       Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        retour :
            int : hauteur du dernier coup"""

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


def agregate_height(g_prec, g_next, action) :
    """ Heuristique : Somme de la hauteur de chaque colonne.
        
        Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        retour :
            - int : somme de la heuteur de chaque colonne de g_next """
    etat = State.state(g_next)
    somme = 0
    for i in range(gp.TAILLE_X) :
        for j in reverse(list(range(gp.TAILLE_Y_LIMITE-1))) :
            if etat.grid[i][j] != Block.Block.Empty :
                #première case de la colonne qui n'est pas vide
                somme += j
                break
    return somme


def erosion(g_prec, g_next, action):
    """ Heuristique : (nombre de line réalisée par action)*(nombre de block de la piece détuits).

    Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.
       
    retour :
        - int : (nombre de line réalisée par action)*(nombre de block de la piece détuits) """
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




def line_transition(g_prec, g_next, action):
    """Heuristique : Compte le nombre de transition vide/pleine et pleine/vide entre les cellules
        selon les lignes.

       Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.
    
        retour : 
             - int : nombre de transition vide/pleine et pleine/vide entre les cellules"""
    cpt = 0
    for j in range(gp.TAILLE_Y_LIMITE):
        for i in range(gp.TAILLE_X - 1) :
            if(g_next.grid[i][j] == Block.Block.Empty and g_next.grid[i+1][j] != Block.Block.Empty) or\
                (g_next.grid[i][j] != Block.Block.Empty and g_next.grid[i+1][j] == Block.Block.Empty) :
                cpt += 1
    return cpt

def column_transition(g_prec, g_next, action):
    """Heuristique : Compte le nombre de transition vide/pleine et pleine/vide entre les cellules
        selon les colonnes.

       Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.
    
        retour : 
             - int : nombre de transition vide/pleine et pleine/vide entre les cellules"""
    cpt = 0
    for i in range(gp.TAILLE_X) :
        for j in range(gp.TAILLE_Y_LIMITE-1) :
            if(g_next.grid[i][j] == Block.Block.Empty and g_next.grid[i][j+1] != Block.Block.Empty) or\
                (g_next.grid[i][j] != Block.Block.Empty and g_next.grid[i][j+1] == Block.Block.Empty) :
                cpt += 1
    return cpt

def holes(g_prec, g_next, action):
    """ Heuristique : compte le nombre de trou (cellule vide entourné de ses quatres cotés par une
            cellule pleine.

        Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        retour :
            - int : nombre de trou"""
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

def wells(g_prec, g_next, action) :
    """ Heuristique : compte la valeur des puits dans la grille :
            Un puit est un trou non recouvert de un de profondeur minimum. 
            La valeur d'un puit est égale à :
                (n*n+1)/2

        Paramètres :
                - grid_prec : instance State.State : Etat du jeu avant le coup 'action'.
                - grid_next : instance State.State : Etat du jeu après le coup 'action'.
                - action : dictionnaire de la forme {"choose" : kind, "rotate" : rotation, "hor_move" : move} :
                    action à jouer.

        retour  :
            valeur des puits"""

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

