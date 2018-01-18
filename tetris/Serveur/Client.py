import json
import websockets


class Client:

    def __init__(self, server, name, socket, cid):
        self.server = server
        self.socket = socket
        self.name = name
        self.id = cid
        self.connect = True

    def __str__(self):
        return self.name + "(" + str(self.id) + ")"

    async def request(self):
        while self.connect:
            try:
                mess = await self.socket.recv()
                #print("receive from ", self.name)
                #print(mess)
                mess = json.loads(mess)
                if mess["mess_type"] == "action":
                    await self.request_action(mess)
                elif mess["mess_type"] == "new_game":
                    await self.request_new_game(mess)
                elif mess["mess_type"] == "unlink_game":
                    await self.request_unlink(mess)
                elif mess["mess_type"] == "link_game":
                    await self.request_link(mess)
                else:
                    print("Error Server message receive : step unknown")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocketException: client disconnect! ")
                self.connect = False
                await self.server.disconnect_client(self)
            except Exception as e:
                print(e)
                raise e

    async def request_unlink(self, mess):
        pass

    async def request_new_game(self, mess):
        pass

    async def request_link(self, mess):
        pass

    async def request_action(self, mess):
        pass

    def on_quit_game(self, game):
        print(self.name," quit the game :",game.gid)

    def on_begin_game(self, game, ids_in_game):
        print(self.name," begin the game :",game.gid)

    def on_view_game(self, game):
        pass

    async def on_disconnect(self):
        self.socket.close()

    async def send_message(self, mess):
        try:
            # if self.id == 5 or self.id == 3:
            #     print(mess)
            #     print("address to ", self.name)
            #if not (mess["step"] == "game") :
             #   print(mess)
            await self.socket.send(json.dumps(mess))
        except websockets.exceptions.ConnectionClosed:
            print("WebSocketException: client disconnect! ")
            self.connect = False
            await self.server.disconnect_client(self)

    @classmethod
    def print_error(cls, error, mess):
        print(error)
        print(mess)
