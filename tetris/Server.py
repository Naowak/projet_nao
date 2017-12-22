# coding : utf-8

import asyncio
import json
import websockets

import Game
import GlobalParameters as gp
import Piece
import IAClientClient
import IAClientServer
import ClientServer


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
            await asyncio.sleep(0)
        game.quit()
        del self.games[game.gid]
        await self.actualise_server_info()

    async def unlink_game(self, client, game):
        game.unbind_client(client)
    async def link_game(self, client, gid):
        self.games[gid].bind_client(client)

    async def new_game(self, players_id, viewers_id, ias):
        #donner les ids in game et l'envoye dans le data_init_game
        players = {}
        next_ids_in_game = 0
        for [pid, number] in players_id + ias:
            #try:
            for _ in range(number):
                players[self.my_clients[pid]] += [next_ids_in_game]
                next_ids_in_game += 1
            #except keyError as e:
            #    print("Game cancelled : Player ",pid," doesn't exist")
            #    print(e)
        game = self.games[self.next_games_id] = \
                Game.Game(self.next_games_id, self,\
                        nb_players=gp.NOMBRE_DE_JOUEUR,\
                        nb_turn=gp.NOMBRE_DE_TOUR,\
                        nb_choices=gp.NOMBRE_DE_CHOIX)
        self.next_games_id += 1
        for [player, ids_in_game] in players:
            player.on_begin_game(game, ids_in_game)
            data = Server.data_init_game(game, ids_in_game)
            await self.send_message(player.ws, data)
            game.bind_player(player)

        for vid in viewers_id:
            self.my_clients[vid].on_view_game()
            game.bind_viewer(self.my_clients[vid])
        asyncio.ensure_future(self.run_game(game)) 

    async def init_ia(self):
        for [level, levelname] in enumerate(gp.LEVELS):
            asyncio.ensure_future(IAClientClient.create_ia("IA_SERVER_LVL"+levelname, level))

    async def connect(self, sock, path):
        mess = await sock.recv()
        mess = json.loads(mess)
        if "level" in mess:
            client = IAClientServer.IAClientServer(\
                self, mess["name"], sock, self.next_connect_id)
            self.my_ias[mess["level"]] = client
        else:
            client = ClientServer.ClientServer(\
                self, mess["name"], sock, self.next_connect_id)
            self.my_clients[client.id] = client

        print(client, " is connect (id:", client.id, ")")
        await self.send_message(sock, self.data_connect())
        self.next_connect_id += 1
        await self.actualise_server_info()
        await asyncio.ensure_future(client.request())
        await self.disconnect_client(client)

    def data_update(self):
        data = {}
        data["step"] = "update"
        print(self.my_clients)
        data["clients"] = {key:value.name for [key, value] in self.my_clients}
        data["games"] = {key:str(value.clients) for [key, value] in self.my_clients}
        return data
    def data_connect(self):
        data = {}
        data["step"] = "connect"
        data["pid"] = self.next_connect_id
        return data

    @classmethod
    def data_init_game(game, ids_in_game):
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
            data["color"][key] = color.value
        #print(ids_in_game)
        return data

    def accept_connections(self, port):
        # , timeout=100
        return websockets.serve(self.connect, 'localhost', port)

    async def disconnect_client(self, client):
        client.ws.close()
        del self.my_clients[client.id]
        print(client + " is unconnect")
        await self.actualise_server_info()

    async def actualise_server_info(self):
        for client in (self.my_clients + self.my_ias).values():
            await self.send_message(client.ws, self.data_update())

    async def send_message(self, websocket, mess):
        # print("send")
        # print(mess)
        await websocket.send(json.dumps(mess))

SERVER = Server()
server_loop = asyncio.get_event_loop()
server_loop.run_until_complete(SERVER.accept_connections(gp.PORT))
asyncio.ensure_future(SERVER.init_ia())
server_loop.run_forever()
