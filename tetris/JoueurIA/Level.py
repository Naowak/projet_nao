# coding: utf-8
import sys
sys.path.append('../')
import random
import copy

import GlobalParameters as gp
from Jeu import State
from Jeu import Piece
from Jeu import Block

URI = gp.ADRESSE + str(gp.PORT)


class Level:
    """ Une instance de cette classe représente un niveau d'une IA sélectionnable par le client javascript, en l'ajoutant 
    dans le fichier AI_creator"""

    def __init__(self, strategy):
        """ Créer un object Level 

        Paramètres :
            - strategy : fonction de la forme fonction fonction(state), 
            où state est un objet State.State :
            Cette fonction stategy est la fonction appeler à chaque fois que l'IA doit jouer un coup.

        Retour :
            une instance de Level.Level"""
        self.strategy = strategy
        
    async def play(self,state):
        """ Demande à l'IA de jouer un coup

        Paramètres :
            - state : instance State.State : état du jeu

        Retour :
         Un play de la forme {"hor_move":hor_move, "rotate":rotat, "choose":piece}"""
        return self.strategy(state)
    
    def on_finished_game(self, data):
        """Fonction appelée lors de la fin de la partie, à redéfinir si l'on souhaite définir un comportement
        particulier pour l'IA à la fin de chaque partie.

        Paramètres : 
            - data : dictionnaire : message reçu de la part du serveur

        Retour :
            None"""
        pass

    def update_play(self, data) :
        """Fonction appelée après chaque coup, à redéfinir si l'on souhaite définir un comportement
        particulier pour l'IA après chaque coup.

        Paramètres : 
            - data : dictionnaire : message reçu de la part du serveur

        Retour :
            None"""
        pass

    def on_init_game(self, data) :
        """Fonction appelée lors de l'initialisation d'une partie, à redéfinir si l'on souhaite définir un comportement
        particulier pour l'IA lors l'initialisation d'une partie.

        Paramètres : 
            - data : dictionnaire : message reçu de la part du serveur

        Retour :
            None"""
        pass



def random_ia(state):
    """ Stratégie de l'IA aléatoire 

    Paramètres :
        - state :  instance State.State : etat du jeu

    Retour :
        Un play de la forme {"hor_move":hor_move, "rotate":rotat, "choose":piece}"""
    piece = random.choice(state["pieces"])
    rotat = random.randrange(1, 4, 1)
    hor_move = random.randrange(0, 9, 1)-5
    return {"hor_move":hor_move, "rotate":rotat, "choose":piece}

def basic_smart_ia(state) :
    """ Stratégie IA aléatoire smart : Elle joue aléatoirement, sauf si elle peut prendre une ligne.
    Dans ce cas, elle complète la ligne;

    Paramètres :
        - state :  instance State.State : etat du jeu

    Retour :
        Un play de la forme {"hor_move":hor_move, "rotate":rotat, "choose":piece}"""
    pieces = copy.copy(state["pieces"])
    scores = []
    compteur = 0

    for kind in pieces :
        for rotation in range(0,4,1) :
            for move in range(-5,7,1) :
                play = {"choose":kind, "rotate":rotation, "hor_move":move}
                grid_tmp = State.State(copy_grid(state["grid"]))
                p = Piece.Piece.factory(kind, copy.copy(Piece.Piece.centers_init[kind]))
                for _ in range(rotation) :
                    p.rotate()
                if(State.is_piece_accepted_abscisse(p, p.center[0] + p.block_control[0] + move)) :
                    p.center[0] += move
                    r = grid_tmp.drop_piece(p, 0)
                    scores += [[play, grid_tmp.score[0]]]

    scores.sort(key=lambda x : x[1], reverse=True)
    best = scores[0][1]
    best_plays = []
    for s in scores :
        if s[1] >= best :
            best_plays += [s]
    play_send = random.choice(best_plays)[0]
    return play_send


def copy_grid(grid) :
    """ Copie une grille et chacun de ses blocks 

    Paramètres :
        -grid : tableau deux dimension : représente la grille du jeu

    Retour :
        Une nouvelle grille du jeu en tout point exact à grid."""
    size = (len(grid), len(grid[0]))
    new_grid = list()
    for i in range(size[0]) :
        new_grid += [list()]
        for j in range(size[1]) :
            new_grid[i] += [copy.copy(grid[i][j])]
    return new_grid



if __name__ == "__main__" :
    my_grid = [[Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty], 
    [Block.Block.Red, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty, Block.Block.Empty]]

    pieces = ["O", "I", "L"]

    state = {"pieces":pieces, "grid":my_grid}

    print(basic_smart_ia(state))
