# coding : utf-8
import sys
sys.path.append('../')
import asyncio
import json
import websockets

from Jeu import Game
import GlobalParameters as gp
from Jeu import Piece
from Serveur import AI_creator
from Serveur import IAClientServer
from Serveur import ClientServer


class Server:
    def __init__(self):
        self.my_clients = {}
        self.games = {}
        self.next_games_id = 0
        self.next_connect_id = 0
        self.my_ias = {}

    async def run_game(self, game):
        await self.actualise_server_info()
        await game.init_turn()
        await game.update()
        while not game.is_finished:
            #print("sleep")
            await asyncio.sleep(0)
        del self.games[game.gid]
        game.quit()
        print("Game ",game.gid," finished")
        await self.actualise_server_info()

    async def unlink_game(self, client, game):
        game.unbind_client(client)
    async def link_game(self, client, gid):
        self.games[gid].bind_client(client)

    async def new_game(self, players_id, viewers_id, ias):
        #donner les ids in game et l'envoye dans le data_init_game
        players = {}
        next_ids_in_game = 0
        for [pid, number] in players_id:
            try:
                for _ in range(number):
                    if self.my_clients[pid] in players:
                        players[self.my_clients[pid]] += [next_ids_in_game]
                    else:
                        players[self.my_clients[pid]] = [next_ids_in_game]
                    next_ids_in_game += 1
            except KeyError as e:
                print("Game cancelled : Player ",pid," doesn't exist")
                print(e)
                return

        for [level, number] in ias:
            try:
                for _ in range(number):
                    if self.my_ias[level] in players:
                        players[self.my_ias[level]] += [next_ids_in_game]
                    else:
                        players[self.my_ias[level]] = [next_ids_in_game]
                    next_ids_in_game += 1
            except KeyError as e:
                print("Game cancelled : IA level:",level," doesn't exist")
                print(e)
                return

        game = self.games[self.next_games_id] = \
                Game.Game(self.next_games_id,\
                        nb_players=gp.NOMBRE_DE_JOUEUR,\
                        nb_turn=gp.NOMBRE_DE_TOUR,\
                        nb_choices=gp.NOMBRE_DE_CHOIX)
        self.next_games_id += 1
        for player, ids_in_game in players.items():
            player.on_begin_game(game, ids_in_game)
            data = Server.data_init_game(game, ids_in_game)
            await player.send_message(data)
            game.bind_player(player)

        for vid in viewers_id:
            self.my_clients[vid].on_view_game(game)
            game.bind_viewer(self.my_clients[vid])
            data = Server.data_init_game(game, [])
            await self.my_clients[vid].send_message(data)
        asyncio.ensure_future(self.run_game(game))

    async def init_ia(self):
        for [level, levelname] in enumerate(gp.LEVELS):
            asyncio.ensure_future(AI_creator.create_ia("IA_SERVER_LVL"+levelname, level))

    async def connect(self, sock, path):
        mess = await sock.recv()
        mess = json.loads(mess)
        if "level" in mess:
            client = IAClientServer.IAClientServer(\
                self, mess["name"], sock, self.next_connect_id)
            mess["level"]
            self.my_ias[mess["level"]] = client
        else:
            client = ClientServer.ClientServer(\
                self, mess["name"], sock, self.next_connect_id)
            self.my_clients[client.id] = client
        #client.on_connect()
        print(client, " is connect (id:", client.id, ")")
        await client.send_message(self.data_connect(client))
        self.next_connect_id += 1
        await self.actualise_server_info()
        await asyncio.ensure_future(client.request())   

    def data_update(self):
        data = {}
        data["step"] = "update"
        data["clients"] = {k:val.name for k, val in self.my_clients.items()}
        data["games"] = {k:str(val) for k, val in self.games.items()}
        return data

    def data_connect(self, client):
        data = {}
        data["step"] = "connect"
        data["pid"] = client.id
        data["levels"] = gp.LEVELS
        return data

    @classmethod
    def data_init_game(cls, game, ids_in_game):
        data = {}
        data["nb_choices"] = game.nb_choices
        data["step"] = "init_game"
        data["gid"] = game.gid
        data["ids_in_game"] = ids_in_game
        data["nb_player"] = game.nb_players
        data["kinds"] = {}
        for (key, blocks) in Piece.Piece.kinds.items():
            data["kinds"][key] = []
            for block in blocks:
                data["kinds"][key] += [[float(block[0][0]),
                                        float(block[1][0])]]
        data["color"] = {}
        for (key, color) in Piece.Piece.colors.items():
            data["color"][key] = color
        return data

    def accept_connections(self, port):
        return websockets.serve(self.connect, 'localhost', port)

    async def disconnect_client(self, client):
        await client.on_disconnect()
        del self.my_clients[client.id]
        print(str(client), " is unconnect")
        await self.actualise_server_info()

    async def actualise_server_info(self):
        data = self.data_update()
        clients = self.my_clients.values()
        ias = self.my_ias.values()
        for client in clients:
            await client.send_message(data)
        for ia_client in ias:
            await ia_client.send_message(data)

if __name__ == "__main__" :
    SERVER = Server()
    SERVER_LOOP = asyncio.get_event_loop()
    SERVER_LOOP.run_until_complete(SERVER.accept_connections(gp.PORT))
    asyncio.ensure_future(SERVER.init_ia())
    SERVER_LOOP.run_forever()
