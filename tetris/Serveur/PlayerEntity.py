import enum
import asyncio

from Serveur import Client


class PlayerEntity(Client.Client):

    class State(enum.Enum):
        FREE = "Free"
        PLAY = "Play"
        OBSERVE = "Observe"

    def __init__(self, server, name, socket, cid):
        super().__init__(server, name, socket, cid)
        self.ids_in_game = []
        self.state = PlayerEntity.State.FREE
        self.game = None
        self.unlink_request = False

    async def request_unlink(self, mess):
        if (self.state == PlayerEntity.State.OBSERVE or self.state == PlayerEntity.State.PLAY) and self.game.gid == mess["gid"]:
            self.unlink_request = True
            await self.server.unlink_game(self,self.game)
        else:
            super().print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): not observe/play this game", mess)

    async def request_new_game(self, mess):
        while self.unlink_request == True :
            await asyncio.sleep(0)
        if self.state == PlayerEntity.State.FREE:
            await self.server.new_game(
                mess["players"], mess["viewers"], mess["IAs"])
        else:
            super().print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_link(self, mess):
        if self.state == PlayerEntity.State.FREE:
            await self.server.link_game(self, mess["gid"])
        else:
            super().print_error("Error message receive :" + self.name +\
                        "(" + str(self.id) + "): already in game/observation", mess)

    async def request_action(self, mess):
        if self.game.actual_player in self.ids_in_game:
            await self.game.set_action(mess["action"])
        else:
            super().print_error("Error message receive IA_Server :" + self.name +\
                                "(" + str(self.id) + "): not his/her/its turn", mess)

    def on_quit_game(self, game):
        super().on_quit_game(game)
        self.ids_in_game = []
        self.game = None        
        self.state = PlayerEntity.State.FREE
        self.unlink_request = False

    def on_begin_game(self, game, ids_in_game):
        super().on_begin_game(game,ids_in_game)
        self.ids_in_game = ids_in_game
        self.game = game
        self.state = PlayerEntity.State.PLAY

    async def on_disconnect(self):
        if self.state == PlayerEntity.State.PLAY or\
            self.state == PlayerEntity.State.OBSERVE:
            await self.server.unlink_game(self,self.game)
        await super().on_disconnect()        

    def on_view_game(self, game):
        super().on_view_game(game)
        self.state = PlayerEntity.State.OBSERVE
        self.game = game
