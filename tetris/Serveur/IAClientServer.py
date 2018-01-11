from Serveur import Client

class IAClientServer(Client.Client):
    def __init__(self, server, name, ws, cid):
        super().__init__(server, name, ws, cid)
        self.ids_in_games = {}
        self.games = {}

    async def request_unlink(self, mess):
        print("IA doesn't do an unlink request")

    async def request_new_game(self, mess):
        print("IA doesn't do an new_game request")

    async def request_link(self, mess):
        print("IA doesn't do an link request")

    async def request_action(self, mess):
        if self.games[mess["gid"]].actual_player in self.ids_in_games[mess["gid"]]:
            await self.games[mess["gid"]].set_action(mess["action"])
        else:
            super.print_error("Error message receive IA_Server :" + self.name +\
                        "(" + str(self.id) + "): not his/her/its turn", mess)
            print(mess["gid"])
            print(self.ids_in_games[mess["gid"]])

    def on_quit_game(self, game):
        del self.games[game.gid]
        del self.ids_in_games[game.gid]

    def on_begin_game(self, game, ids_in_game):
        self.games[game.gid] = game
        self.ids_in_games[game.gid] = ids_in_game

    def on_disconnect(self):
        print("Houston nous avons un probleme!")
        super().on_disconnect()
        assert(False)

    def on_view_game(self, game):
        print("IA doesn't view game")