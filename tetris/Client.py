import enum
import json
import websockets


class Client:
    class State(enum.Enum):
        FREE = "Free"
        PLAY = "Play"
        OBSERVE = "Observe"

    def __init__(self, server, name, ws, cid):
        self.server = server
        self.ws = ws
        self.name = name
        self.id = cid
        self.id_in_game = []
        self.state = Client.State.FREE
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
                await self.request_action(mess)
            elif mess["mess_type"] == "new_game":
                await self.request_new_game(mess)
            elif mess["mess_type"] == "unlink_game":
                await self.request_unlink(mess)
            elif mess["mess_type"] == "link_game":
                await self.request_link(mess)
            else:
                print("Error message receive : step unknown")

    async def request_unlink(self, mess):
        if self.state == Client.State.OBSERVE and self.game.gid == mess["gid"]:
            await self.server.unlink_game(self)
        else:
            print_error("Error message receive :" + self.name +
                        "(" + str(self.id) + "): not observe this game", mess)

    async def request_new_game(self, mess):
        if self.state == Client.State.FREE:
            await self.server.new_game(
                mess["players"], mess["observers"], mess["IAs"])
        else:
            print_error("Error message receive :" + self.name +
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_link(self, mess):
        if self.state == Client.State.FREE:
            await self.server.link_game(self, mess["gid"])
        else:
            print_error("Error message receive :" + self.name +
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_action(self, mess):
        if self.state == Client.State.PLAY and self.game.actual_player in self.id_in_game:
            await self.game.set_action(mess["action"])
        else:
            if self.state == Client.State.PLAY:
                print_error("Error message receive :" + self.name +
                            "(" + str(self.id) + "): not in game", mess)
            else:
                print_error("Error message receive :" + self.name +
                            "(" + str(self.id) + "): not his/her/its turn", mess)


def print_error(error, mess):
    print(error)
    print(mess)
