#coding : utf-8
import Game

class Subject:
    def __init__(self):
        self.observers={"players": [],"viewers": []}

    def bind_player(self,player) :
        if(instanceofviewer(player)):
            self.observers["players"].append(player)

    def unbind_player(self,player) :
        if(instanceofviewer(player)):
            self.observers["players"].remove(player)

    def bind_player(self,viewer) :
        if(instanceofviewer(viewer)):
            self.observers["viewers"].append(viewer)

    def unbind_player(self,viewer) :
        if(instanceofviewer(viewer)):
            self.observers["viewers"].remove(viewer)

    def notify_all_observers(self) :
        notify_view(self)
        notify_player(self)

    def notify_player(self) :
        for player in self.observers["players"].value() :
            #envoie de paquet
            pass

    def notify_view(self) :
        for viewer in self.observers["viewers"].value() :
            #envoie de paquet
            pass


    def get_state(self) :
        pass

    def get_rules(self) :
        pass
