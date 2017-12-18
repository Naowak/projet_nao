# coding : utf-8

import random

import GlobalParameters as gp
import Piece
import State
import Subject


# absi = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

class Game(Subject.Subject):

    def __init__(self, gid, server, nb_players):
        super().__init__(gid, server)
        self.grid = State.State()
        self.is_finished = False
        self.actual_turn = 0
        self.actual_pieces = list()
        self.step = "init"
        self.current_piece = None
        self.current_abscisse = None
        self.nb_players = nb_players

    def pieces_random(self, number_of_pieces=3):
        kinds = ['O', 'I', 'L', 'T', 'S', 'Z', 'J']
        kinds_select = {}
        for _ in range(number_of_pieces):
            choice = random.choice(kinds)
            kinds.remove(choice)
            kinds_select[choice] = Piece.Piece.factory(choice,Piece.Piece.centers_init[choice])
        return kinds_select

    async def update(self):
        self.grid.piece_show(self.current_piece)
        self.grid.show_abscisse(self.current_piece, self.current_abscisse)
        await self.notify_all_observers()

    async def init_turn(self):
        self.actual_pieces = self.pieces_random()
        self.current_piece = self.actual_pieces[list(self.actual_pieces.keys())[0]]
        self.current_abscisse = self.current_piece.center[0]
        await self.update()
        return

    def choose_piece(self, kinds):
        if(self.actual_pieces[kinds]):
            self.current_piece = self.actual_pieces[kinds]
            self.current_abscisse = 4

    async def hor_move_piece(self, move):
        if State.is_piece_accepted_abscisse(self.current_piece, self.current_abscisse + move):
            self.current_abscisse = self.current_abscisse - \
                self.current_piece.block_control[0]

    def rotate_piece(self, rotate):
        for _ in range(rotate % 4):
            self.current_piece.rotate()

    async def valid(self):
        result = self.grid.drop_piece(\
        self.current_piece, self.actual_turn % gp.NOMBRE_DE_JOUEUR)
        self.actual_turn += 1  # Le tour commence à 1
        if not result:
            self.is_finished = True
            print("Game Lost !")
        else:
            await self.init_turn()

    async def set_action(self, command):
        if command[0] == "choose":
            self.choose_piece(command[1])
        elif command[0] == "rotate":
            self.rotate_piece(command[1])
        elif command[0] == "hor_move":
            await self.hor_move_piece(command[1])
        elif command[0] == "valid" :
            await self.valid()
        else:
            print("Modification d'état inconnu")
            return False
        await self.update()
        return True

    # async def turn(self) :
    #     if self.step != "init" :
    #         await self.notify_view()
    #     print(self.grid)
    #     if not self.is_finished :
    #         self.actual_turn += 1 #Le tour commence à 1
    #
    #         self.step = "piece_choice"
    #         kinds = self.pieces_random()
    #         await self.notify_all_observers()
    #         kind = await self.server.ask_user_piece_choose(kinds)
    #
    #         center = copy.copy(Piece.Piece.centers_init[kind])
    #         piece = Piece.Piece.factory(kind, center)
    #         self.grid.piece_show(piece)
    #
    #         self.step = "rotation"
    #         boucle = True
    #         while boucle :
    #             await self.notify_all_observers()
    #             rotate = await self.server.ask_user_rotate()
    #             if rotate == "R":
    #                 piece.rotate()
    #                 self.grid.piece_show(piece)
    #             elif rotate == "" :
    #                 boucle = False
    #
    #         self.step = "abscisse"
    #         boucle = True
    #         abscisse = 0
    #         while boucle :
    #             await self.notify_all_observers()
    #             abscisse = await self.server.ask_user_abscisse()
    #             boucle = not self.grid.is_piece_accepted_abscisse(piece, abscisse)
    #
    #
    #         center[0] = abscisse - piece.block_control[0]
    #         self.grid.show_abscisse(piece, abscisse)
    #         self.step = "end_turn"
    #         await self.notify_view()
    #         result = self.grid.drop_piece(piece, self.actual_turn %gp.NOMBRE_DE_JOUEUR)
    #         if not result :
    #             self.step = "finished"
    #             self.is_finished = True
    #             await self.notify_view()
    #             print("Game Lost !")

    def get_etat(self):
        dico = self.grid.encode_to_json()
        tmp = {"pieces": list(self.actual_pieces.keys())}
        dico["gid"] = self.gid
        dico["pieces"] = tmp["pieces"]
        dico["actual_player"] = self.observers["players"][self.actual_turn % gp.NOMBRE_DE_JOUEUR][2]
        if self.is_finished:
            dico["step"] = "finished"
        else:
            dico["step"] = "game"
        return dico


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
