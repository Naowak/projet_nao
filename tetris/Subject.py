#coding : utf-8

class Subject:
    def __init__(self, gid):
        self.gid = gid
        self.is_finished = False
        self.clients = {"players": {}, "viewers": {}}

    def bind_player(self, client):
        #client.on_begin_game() deja appele par le serveur
        self.clients["players"][client.id] = client
        print(client.name, "play the game ", self.gid)

    def unbind_client(self, client):
        client.on_quit_game(self)
        print(client.name, "leave the game ", self.gid)
        if self.clients["players"][client.id]:
            print("game cancelled")
            self.finished = True
        elif self.clients["observers"][client.id]:
            del self.clients["observers"][client.id]

    def bind_viewer(self, viewer):
        viewer.on_view_game(self)
        self.clients["viewers"][viewer.id] = viewer
        print(viewer.name, "observe the game ", self.gid)

    async def notify_all_observers(self):
        mess = self.get_etat()
        print("actual_player: ", mess["actual_player"])
        for client in self.clients["players"].values():
            await client.send_message(mess)
        for viewer in self.clients["viewers"].values():
            await viewer.send_message(mess)

    async def notify_player(self):
        mess = self.get_etat()
        for player in self.clients["players"].values():
            await player.send_message(mess)

    async def notify_view(self):
        mess = self.get_etat()
        for viewer in self.clients["viewers"]:
            await viewer.send_message(mess)

    def quit(self):
        clients = []
        for client in self.clients["players"].values():
            clients.append(client)
        for client in self.clients["viewers"].values():
            clients.append(client)
        for client in clients:
            client.on_quit_game(self)
        print("game ", self.gid, "close")


    async def set_action(self, command):
        pass

    def get_etat(self):
        pass

    def __str__(self):
        string_ret = "players: {"
        for player in self.clients["players"].values():
            string_ret += str(player)+" "
        string_ret += "}; observers: {"
        for obs in self.clients["viewers"].values():
            string_ret += str(obs)+" "
        string_ret += "}"
        return string_ret
