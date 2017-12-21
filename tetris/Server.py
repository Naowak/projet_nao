# coding : utf-8

import asyncio
import json
import websockets

import Client
import Game
import GlobalParameters as gp
import Piece
import IAClient


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

    async def unlink_game(self, client):
        client.game.unbind_client(client)

    async def link_game(self, client, gid):
        client.game.bind_client(client)
        client.game = self.games[gid]

    async def new_game(self, players_id, viewers, ias):
        #donner les ids in game et l'envoye dans le data_init_game
        players = []
        next_ids_in_game = 0
        for [pid, number] in players_id:
            #try:
            for _ in range(number):
                self.my_clients[pid].ids_in_game.append(next_ids_in_game)
                next_ids_in_game += 1
                players.append(self.my_clients[pid])
            #except keyError as e:
            #    print("Game cancelled : Player ",pid," doesn't exist")
            #    print(e)
        for [level, number] in ias:
            #try:
            for _ in range(number):
                self.my_ias[level].ids_in_game.append(next_ids_in_game)
                next_ids_in_game += 1
                players.append(self.my_ias[level])
            #except keyError as e:
            #   print("Game cancelled : IA ", level, " doesn't exist")
            #    print(e)
        gid = self.next_games_id
        game = self.games[gid] = Game.Game(gid, self,nb_players=gp.NOMBRE_DE_JOUEUR,\
                                            nb_turn=gp.NOMBRE_DE_TOUR,\
                                            nb_choices=gp.NOMBRE_DE_CHOIX)
        self.next_games_id += 1
        for client in players:
            data = self.data_init_game(game,client.ids_in_game)
            await self.send_message(client.ws,data)
        for viewer in viewers:
            viewer.game = game
            game.bind_viewer(viewer)
        for player in players:
            player.game = game
            game.bind_player(player)
        asyncio.ensure_future(self.run_game(game))  


    async def init_ia(self):
        for level in gp.LEVELS:
            asyncio.ensure_future(IAClient.run(name="IA"+level))
            


    async def connect(self, sock, path):
        mess = await sock.recv()
        mess = json.loads(mess)
        client = Client.Client(
            self, mess["name"], sock, self.next_connect_id)
        if mess["type"] == "IA_play":
            self.my_ias[mess["level"]] = client
        else:
            self.my_clients[client.id] = client                
        print(client, " is connect (id:", self.next_connect_id, ")")
        await self.send_message(sock, self.data_connect())
        self.next_connect_id += 1
        await self.actualise_server_info()
        await asyncio.ensure_future(client.request())
        await self.disconnect_client(client)

    def data_menu(self):
        data = {}
        data["step"] = "menu"
        data["clients"] = [str(i) for i in self.my_clients.values()]
        data["games"] = [str(i.gid) + " : " + str(i.clients)\
                        for i in self.games.values()]
        return data

    def data_connect(self):
        data = {}
        data["step"] = "connect"
        data["pid"] = self.next_connect_id
        return data

    def data_init_game(self, game, ids_in_game):
        data = {}
        data["nb_choices"] = game.nb_choices
        data["step"] = "init_game"
        data["gid"] = self.next_games_id
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
        print(ids_in_game)
        return data

    def accept_connections(self, port):
        # , timeout=100
        return websockets.serve(self.connect, 'localhost', port)

    async def disconnect_client(self, client):
        if client.in_game and client.game.unbind_client(client):
            del self.games[client.game.gid]
        client.ws.close()
        del self.my_clients[client.id]
        print(Client + " is unconnect")
        await self.actualise_server_info()

    async def actualise_server_info(self):
        for client in self.my_clients.values():
            await self.send_message(client.ws, self.data_menu())

    async def send_message(self, websocket, mess):
        # print("send")
        # print(mess)
        await websocket.send(json.dumps(mess))

    async def receive_command(self, game):
        #print(game.actual_turn % game.nb_players)
        mess = await self.my_clients["players"][game.actual_turn % game.nb_players].ws.recv()
        mess = json.loads(mess)
        # print("receive")
        # print(mess)
        await game.set_action(mess["action"])

SERVER = Server()
server_loop = asyncio.get_event_loop()
server_loop.run_until_complete(SERVER.accept_connections(gp.PORT))
server_loop.run_forever()
