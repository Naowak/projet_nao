#coding : utf-8
import asyncio
class Subject:
    def __init__(self, gid):
        self.gid = gid
        self.is_finished = False
        self.clients = {"players": {}, "viewers": {}}

    def bind_player(self, client):
        self.clients["players"][client.id] = client
        print(client.name, "playerbind to the game ", self.gid)

    def unbind_client(self, client):
        if client.id in self.clients["players"]:
            print("game cancelled")
            self.is_finished = True
        elif client.id in self.clients["viewers"]:
            client.on_quit_game(self)
            del self.clients["viewers"][client.id]
        else:
            print("Error, client key not find .")

    def bind_viewer(self, viewer):
        self.clients["viewers"][viewer.id] = viewer
        viewer.on_view_game(self)
        print(viewer.name, "observebind to the game ", self.gid)

    async def notify_all_viewers(self):
        mess = self.get_etat()
        for client in self.clients["players"].values():
            await client.send_message(mess)
        for viewer in self.clients["viewers"].values():
            await viewer.send_message(mess)

    async def notify_player(self):
        mess = self.get_etat()
        for player in self.clients["players"].values():
            await player.send_message(mess)

    async def notify_view(self,viewer_to_notify = None):
        mess = self.get_etat()
        if viewer_to_notify is None:
            for viewer in self.clients["viewers"]:
                await viewer.send_message(mess)
        else:
           await viewer_to_notify.send_message(mess) 

    def quit(self):
        clients = list(self.clients["viewers"].values())+list(self.clients["players"].values())
        for client in clients:
            client.on_quit_game(self)
        print("Game ", self.gid, "close")


    async def set_action(self, command):
        pass

    def get_etat(self):
        pass

    def __str__(self):
        string_ret = "players: {"
        for player in self.clients["players"].values():
            string_ret += str(player)+" "
        string_ret += "}; viewers: {"
        for obs in self.clients["viewers"].values():
            string_ret += str(obs)+" "
        string_ret += "}"
        return string_ret
