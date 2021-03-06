# coding : utf-8
import sys
sys.path.append('../')
import random
import copy

import GlobalParameters as gp
from Jeu import Piece
from Jeu import State
from Jeu import Subject


class Game(Subject.Subject):
    """Classe gérant le déroulement des parties,

    Hérite de Subject.Subject"""

    def __init__(self, gid, nb_players, nb_turn, nb_choices):
        """Créer une nouvelle Game.

        Attributs :
            - gid : int / ID de la Game.
            - nb_players : int / Nombre de joueurs dans la partie
            - nb_turn : int / Nombre de tour maximum dans la partie
            - nb_choice : int / Nombre de différentes pieces présentées aux joueurs à chaque tours 

        Retourne :
            - Game : nouvelle game"""
        super().__init__(gid)
        self.grid = State.State()
        self.actual_turn = 0
        self.actual_player = 0
        self.actual_pieces = list()
        self.step = "init"
        self.current_piece = None
        self.current_abscisse = None
        self.nb_turn = nb_turn
        self.nb_choices = nb_choices
        self.nb_players = nb_players

    def pieces_random(self, number_of_pieces=3):
        """Choisi aléatoirement number_of_pieces différentes pièces,

        Attributs :
            - number_of_pieces : int / Nombre de pièce à sélectionner

        Retourne :
            - list de 3 string parmi : ['O', 'I', 'L', 'T', 'S', 'Z', 'J']"""
        kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
        kinds_select = {}
        for _ in range(number_of_pieces):
            choice = random.choice(kinds)
            kinds.remove(choice)
            kinds_select[choice] = Piece.Piece.factory(
                choice, copy.copy(Piece.Piece.centers_init[choice]))
        return kinds_select

    async def update(self):
        """Mets à jour l'état du jeu en fonction de la piece courrante et de
        sa position choisie, notifie tous les observateurs"""
        self.grid.show_abscisse(self.current_piece, self.current_abscisse)
        self.grid.piece_show(self.current_piece)
        await self.notify_all_viewers()

    async def init_turn(self):
        """Initialise le début d'un tour de jeu"""
        self.actual_pieces = self.pieces_random(self.nb_choices)
        self.current_piece = self.actual_pieces[list(
            self.actual_pieces.keys())[0]]
        self.current_abscisse = self.current_piece.center[0] + \
            self.current_piece.blocks[0][0]
        return

    def choose_piece(self, kinds):
        """Selection de la pièce kinds pour le tour courant

        Attributs :
            - kinds : string parmi ['O', 'I', 'L', 'T', 'S', 'Z', 'J']"""
        if(self.actual_pieces[kinds]):
            self.current_piece = self.actual_pieces[kinds]
            self.current_abscisse = self.current_piece.center[0] + \
                self.current_piece.blocks[0][0]

    async def hor_move_piece(self, move):
        """Déplace la pièce courante horizontalement selon move.

        Attributs :
            - move : int / Réprésente le mouvement horizontale de la pièce
                    move > 0 : déplacement à droite
                    move < 0 : déplacement à gauche"""
        if State.is_piece_accepted_abscisse(self.current_piece, self.current_abscisse + move):
            self.current_abscisse = self.current_abscisse + move
            self.current_piece.center[0] += move

    def rotate_piece(self, rotate):
        """Fait tourner la pièce courante rotate fois.

        Attributs :
            - rotate : int / Nombre de rotation à effectuée 
                       (chaque rotation est dans le sens des aiguilles d'une montre"""
        for _ in range(rotate % 4):
            self.current_piece.rotate()
        self.current_abscisse = self.current_piece.center[0] + \
            self.current_piece.blocks[0][0]

    async def valid(self):
        """Valide le play (fait tomber la piece). Vérifie que le play n'a pas fini la partie
            (dans le cas d'un play qui dépasse la hauteur max"""
        valid = self.grid.drop_piece(
            self.current_piece, self.actual_turn % self.nb_players)
        if not valid:
            self.grid.score[self.actual_player] = gp.SCORE_DEPASSEMENT
            self.on_finish()
        elif self.actual_turn == self.nb_turn:
            self.on_finish()
        else:
            self.actual_turn += 1  # Le tour commence à 1
            self.actual_player = (self.actual_player + 1) % self.nb_players                
            await self.init_turn()

    async def set_action(self, command):
        """Effectue l'action command.

        Attributs :
            - command : list représentant une commande et ses paramètres.
                    Le premier paramètre (command[0]) doit être égale à l'une
                    des string suivantes ["choose", "rotate", "hor_move", "valid"]"""
        if command[0] == "choose":
            self.choose_piece(command[1])
        elif command[0] == "rotate":
            self.rotate_piece(command[1])
        elif command[0] == "hor_move":
            await self.hor_move_piece(command[1])
        elif command[0] == "valid":
            await self.valid()
        else:
            print("Modification d'état inconnu")
            return False
        await self.update()
        return True

    def get_etat(self):
        """Retourne l'état de la game sous forme de dictionnaire.

        Retourne :
            dictionnaire : représente l'état de la game"""
        dico = self.grid.encode_to_json(self.current_piece)
        tmp = {"pieces": list(self.actual_pieces.keys())}
        dico["gid"] = self.gid
        dico["pieces"] = tmp["pieces"]
        dico["actual_player"] = self.actual_player
        dico["turn"] = self.actual_turn
        dico["actual_pieces"] = self.current_piece.kind
        dico["actual_abscisse"] = self.current_abscisse[0]
        if self.is_finished:
            dico["step"] = "finished"
        else:
            dico["step"] = "game"
        return dico

    def on_finish(self) :
        self.is_finished = True


def ask_user_piece_choose(pieces_kind):
    test = False
    kind = ""
    while not test:
        print("Choose a piece from those pieces : ")
        for piece in pieces_kind:
            print(piece + " ")
        print("\n")
        kind = input()
        if kind in pieces_kind:
            test = True
    return kind


def ask_user_abscisse():
    print("Please enter an valid abscisse : ")
    choice = int(input())
    return choice


def ask_user_rotate():
    print("To rotate the piece enter 'R', else press 'Enter' : ")
    choice = input()
    return choice
