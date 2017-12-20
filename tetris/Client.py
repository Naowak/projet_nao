import enum
import Game
import asyncio
import websockets
import json

class Client:
    class State(enum.Enum):
        FREE = "Free"
        PLAY = "Play"
        OBSERVE = "Observe"

    def __init__(self,name,ws,cid,active):
        self.ws = ws
        self.name = name
        self.id = cid
        self.id_in_game = None
        self.state = Client.State.FREE
        self.active = active
        self.connect = True
        self.game = None
    
    def __str__(self):
        return self.name + "(" + str(self.id) +"): " + str(self.state)

    async def request(self):
        while(self.connect):
            try:
                mess = await self.ws.recv()
                #print("receive")
                #print(mess)
            except ConnectionClosed :
                print(self.name + "(" + str(self.id) +"): disconnected")
                return
            mess = json.loads(mess)
            if mess["type"]=="action":
                if self.state == Client.State.PLAY and self.game.actual_turn % self.game.nb_players == self.id_in_game:
                    await self.game.set_action(mess["action"])
                else:
                    print("Error message receive :"+self.name + "(" + str(self.id) +"): not in game")
            elif mess["type"]=="menu":
                if self.state == Client.State.FREE :
                    pass
                else:
                    print("Error message receive :"+self.name + "(" + str(self.id) +"): not in game")
            else :
                    print("Error message receive : step unknown")



