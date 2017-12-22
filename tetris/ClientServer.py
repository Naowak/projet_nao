import enum

import Client


class ClientServer(Client.Client):

    class State(enum.Enum):
        FREE = "Free"
        PLAY = "Play"
        OBSERVE = "Observe"

    def __init__(self, server, name, ws, cid):
        super().__init__(server, name, ws, cid)
        self.ids_in_game = []
        self.state = ClientServer.State.FREE
        self.game = None

    async def request_unlink(self, mess):
        if self.state == ClientServer.State.OBSERVE and self.game.gid == mess["gid"]:
            await self.server.unlink_game(self)
        else:
            super.print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): not observe this game", mess)

    async def request_new_game(self, mess):
        if self.state == ClientServer.State.FREE:
            await self.server.new_game(
                mess["players"], mess["observers"], mess["IAs"])
        else:
            super.print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_link(self, mess):
        if self.state == ClientServer.State.FREE:
            await self.server.link_game(self, mess["gid"])
        else:
            super.print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_action(self, mess):
        if self.game.actual_player in self.ids_in_game:
            await self.game.set_action(mess["action"])
        else:
            super.print_error("Error message receive IA_Server :" + self.name +\
                                "(" + str(self.id) + "): not his/her/its turn", mess)
            print(self.game.gid)
            print(self.ids_in_game)

    def on_quit_game(self, game):
        self.ids_in_game = []
        self.state = ClientServer.State.FREE
        self.game = None

    def on_begin_game(self, game, ids_in_game):
        self.ids_in_game = ids_in_game
        self.state = ClientServer.State.PLAY
        self.game = game

    def on_view_game(self, game):
        self.ids_in_game = []
        self.state = ClientServer.State.OBSERVE
        self.game = None
