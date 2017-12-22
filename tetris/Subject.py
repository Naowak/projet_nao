#coding : utf-8

class Subject:
    def __init__(self, gid, server):
        self.gid = gid
        self.clients = {"players": {}, "viewers": {}}
        self.server = server

    def bind_player(self, client):
        #client.on_begin_game() deja appele par le serveur
        self.clients["players"][client.id] = client
        print(client.name, "play the game ", self.gid)

    def unbind_client(self, client):
        client.on_quit_game(self)
        print(client.name, "leave the game ", self.gid)
        if self.clients["players"][client.id]:
            print("game cancelled")
            self.quit()
        elif self.clients["observers"][client.id]:
            del self.clients["observers"][client.id]

    def bind_viewer(self, viewer):
        viewer.on_view_game()
        self.clients["viewers"][viewer.id] = viewer
        print(viewer.name, "observe the game ", self.gid)

    async def notify_all_observers(self):
        mess = self.get_etat()
        print("actual_player: ", mess["actual_player"])
        for client in self.clients["players"].values():
            await self.server.send_message(client.ws, mess)
        for viewer in self.clients["viewers"].values():
            await self.server.send_message(viewer.ws, mess)

    async def notify_player(self):
        mess = self.get_etat()
        for player in self.clients["players"].values():
            await self.server.send_message(player.ws, mess)

    async def notify_view(self):
        mess = self.get_etat()
        for viewers in self.clients["viewers"]:
            await self.server.send_message(viewers.ws, mess)

    def quit(self):
        clients = []
        for client in self.clients["players"].values():
            clients.append(client)
        for client in self.clients["viewers"].values():
            clients.append(client)
        for client in clients:
            self.unbind_client(client)
        print("game ", self.gid, "close")

    async def set_action(self, command):
        pass

    def get_etat(self):
        pass
