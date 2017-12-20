import enum
import json
import websockets


class Client:
    class State(enum.Enum):
        FREE = "Free"
        PLAY = "Play"
        OBSERVE = "Observe"

    def __init__(self, server, name, ws, cid, active):
        self.server = server
        self.ws = ws
        self.name = name
        self.id = cid
        self.id_in_game = None
        self.state = Client.State.FREE
        self.active = active
        self.connect = True
        self.game = None

    def __str__(self):
        return self.name + "(" + str(self.id) + "): " + str(self.state)

    async def request(self):
        while self.connect:
            try:
                mess = await self.ws.recv()
                # print("receive")
                # print(mess)
            except websockets.exceptions.ConnectionClosed as e:
                print("WebSocketException: client disconnect! ")
                print(e)

            mess = json.loads(mess)
            if mess["mess_type"] == "action":
                if self.state == Client.State.PLAY and self.game.actual_turn % self.game.nb_players == self.id_in_game:
                    await self.game.set_action(mess["action"])
                else:
                    print("Error message receive :" + self.name +
                          "(" + str(self.id) + "): not in game")

            elif mess["mess_type"] == "new_game":
                if self.state == Client.State.FREE:
                    self.server.new_game(
                        mess["players"], mess["observers", mess["IA"]])
                else:
                    print("Error message receive :" + self.name +
                          "(" + str(self.id) + "): already in game")

            elif mess["mess_type"] == "unlink_game":
                if self.state == Client.State.OBSERVE:
                    self.server.unlink_game(self, mess["gid"])
                else:
                    print("Error message receive :" + self.name +
                          "(" + str(self.id) + "): not in game")

            elif mess["mess_type"] == "link_game":
                if self.state == Client.State.FREE:
                    self.server.link_game(self, mess["gid"])
                else:
                    print("Error message receive :" + self.name +
                          "(" + str(self.id) + "): already in game")
            else:
                print("Error message receive : step unknown")
