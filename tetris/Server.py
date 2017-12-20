# coding : utf-8

import json

import Game
import asyncio
import websockets
import Client

import GlobalParameters as gp
import Piece


class Server:
    def __init__(self):
        self.my_clients = {}
        self.games = {}
        self.next_games_id = 0
        self.next_connect_id = 0

    #async def run_server(self):
        #await self.accept_connections(gp.PORT)
     #   print("Serveur running on")
      #  while not len(self.my_sockets["players"]) == gp.NOMBRE_DE_JOUEUR:
       #     await asyncio.sleep(0)
       # asyncio.ensure_future(self.run_game(
        #    self.my_sockets["players"], self.my_sockets["viewers"]))

    async def run_game(self, players, viewers,nb_player):
        gid = self.next_games_id
        game = self.games[gid] = Game.Game(gid, self, nb_player)
        self.next_games_id += 1
        for viewer in viewers:
            game.bind_viewer(viewer)
        for player in players:
            game.bind_player(player)
        await actualise_server_info()
        await game.init_turn()
        while not game.is_finished:
            await self.receive_command(game)
        game.quit()
        del self.games[game.gid]

    async def connect(self, sock, path):
        mess = await sock.recv()
        mess = json.loads(mess)
        self.my_clients[self.next_connect_id] = client = Client.Client(mess["name"],sock,self.next_connect_id,mess["active"])
        print(client ," is connect (id:",self.next_connect_id,")")
        await self.send_message(sock, self.data_connect())     
        self.next_connect_id += 1
        await self.actualise_server_info()
        await asyncio.ensure_future(client.request())
        await self.disconnect_client(client)
        
    
    def data_menu(self):
        data={}
        data["step"]="menu"
        data["clients"]=[str(i) for i in self.my_clients.values()] 
        data["games"]=[str(i.gid) + " : "  + str(i.clients) for i in self.games] 
        return data
    
    def data_connect(self):
        data ={}  
        data["step"]="connect"
        data["pid"]=self.next_connect_id  
        return data

    def data_init_game(self):
        data = {}
        data["nb_choose"] = gp.NOMBRE_DE_CHOIX
        data["step"] = "init_game"
        data["gid"] = self.next_connect_id
        data["nb_player"] = gp.NOMBRE_DE_JOUEUR
        data["kinds"] = {}
        for (key, blocks) in Piece.Piece.kinds.items():
            data["kinds"][key] = []
            for block in blocks:
                data["kinds"][key] += [[float(block[0][0]), float(block[1][0])]]
        data["color"] = {}
        for (key, color) in Piece.Piece.colors.items():
            data["color"][key] = color.value
        return data

    def accept_connections(self, port):
        # , timeout=100
        return websockets.serve(self.connect, 'localhost', port)

    async def disconnect_client(self, client):
        if client.in_game and client.game.unbind_client(client) :
            del games[client.game.gid]
        client.ws.close()
        del self.my_clients[client.id]
        print(Client +" is unconnect") 
        await actualise_server_info()
       
    async def actualise_server_info(self):
        for client in self.my_clients.values():
            await self.send_message(client.ws,self.data_menu())
        

    async def send_message(self, websocket, mess):
        #print("send")
        print(mess)
        await websocket.send(json.dumps(mess))

    async def receive_command(self, game):
        #print(game.actual_turn % game.nb_players)
        mess = await self.clients["players"][game.actual_turn % game.nb_players].ws.recv()
        mess = json.loads(mess)
        #print("receive")
        #print(mess)
        await game.set_action(mess["action"])

#SERVER = Server()
#loop = asyncio.get_event_loop()
#loop.run_until_complete(SERVER.accept_connections(gp.PORT))
#loop.run_forever()

