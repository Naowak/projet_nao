#coding : utf-8
import Client
class Subject:
    def __init__(self, gid, server):
        self.gid = gid
        self.clients = {"players": {}, "viewers": {}}
        self.server = server

    def bind_player(self, client):
        client.state = Client.State.PLAY
        self.clients["players"][client.id]=client
        print(viewer.name + "play the game " + gid)

    def unbind_client(self, client):
        client.state = Client.State.FREE
        print(client.name + "leave the game " + gid)
        if self.clients["players"][client.id] :
            del self.clients["players"][client.id]
            return True
        elif self.clients["observers"][client.id] :
            del self.clients["observers"][client.id]
        return False

    def bind_viewer(self, viewer):
        client.state = Client.State.PLAY
        self.clients["viewers"][viewer.id]=viewer
        print(viewer.name + "observe the game " + gid)

    async def notify_all_observers(self):
        mess = self.get_etat()    
        for clients in self.observers["players"]:
            await self.server.send_message(player.ws, mess)
        for viewers in self.observers["viewers"]:
            await self.server.send_message(viewers.ws, mess)

    async def notify_player(self):
        mess = self.get_etat()
        for player in self.observers["players"]:
            await self.server.send_message(player.ws, mess)

    async def notify_view(self):
        mess = self.get_etat()
        for viewers in self.observers["viewers"]:
            await self.server.send_message(viewers.ws, mess)
    
    def quit(self, client):
        for client in self.clients:
            unbind_client(client)
        print("game " + gid + "close")

    async def set_action(self, command, value):
        pass

    def get_etat(self):
        pass
