# coding: utf-8
import sys
sys.path.append("../../")
import asyncio
import random
from JoueurIA.Client import Nao as naopy
from JoueurIA.Client import ClientInterface

class NaoSpeech(ClientInterface.ClientInterface):
    def __init__(self, name = "NaoSpeech", file = None):
        super().__init__(name, file, active=False)
        self.score_player = 0
        self.score_nao = 0
        self.tour = 0
        self.winner = 3

        
    def update_play(self, data):
        if data['turn'] > self.tour :
            self.tour = data['turn'] 
            rdp = random.random()
            rdthink = random.random()
            if rdp > 0.8 :
                if random.random() > 0.5:
                    if data["actual_player"] == 0:
                        naopy.nao_talk("réfléchi bien")
                    else:
                        naopy.nao_talk("À moi de jouer")
                else:
                    if data["actual_player"] == 0:
                        #print("Attention à ce que tu fais")
                        naopy.nao_anim("animations/Sit/Emotions/Positive/Laugh_2")
                    else:
                        #print("Regardes ce coup de maitre")
                        naopy.nao_anim("animations/Sit/Waiting/ScratchBack_1")
            elif random.random() > 0.8:
                if rdthink < (1/3):
                    naopy.nao_anim("animations/Sit/Waiting/Think_1")
                elif rdthink > (2/3):
                    naopy.nao_anim("animations/Sit/Waiting/Think_2")

            if data['score'][0]> self.score_player:
                rd = random.random()
                if (data['score'][0]> data['score'][1] and self.winner != 0 ):
                        naopy.nao_talk("Mince, tu gagnes maintenant...")
                        self.winner = 0
                elif rd < (1/3):
                    naopy.nao_talk("Ah je n''avais pas vu")
                elif rd < (2/3):
                    naopy.nao_talk("Oh oh bien joué")
                else:
                    naopy.nao_talk("C''était ta dernière ligne.")
            if data['score'][1] > self.score_nao:
                rd = random.random()
                if (data['score'][1] > data['score'][0] and self.winner != 1):
                        naopy.nao_talk("La victoire m''appartient !")
                        self.winner = 1
                elif rd < (1/3):
                    naopy.nao_anim("animations/Sit/Emotions/Positive/Laugh_2")
                elif rd < (2/3):
                    naopy.nao_talk("Hop là ")
                else:
                   naopy.nao_talk("Je ne perdrais pas")

            self.score_nao = data['score'][1]
            self.score_player = data['score'][0]

    def play(data) :
        pass

    def on_init_game(self, data):
        rd = random.random()
        if rd < (1/3):
            naopy.nao_talk("C''est parti")
        elif rd < (2/3):
            naopy.nao_talk("Allons-y")
        else:
            naopy.nao_talk("J''espère que tu es prêt")
        self.score_player = 0
        self.score_nao = 0
        self.tour = 0


    def on_finished_game(self,data):
        if data['score'][1] > data['score'][0]:
            rd = random.random()
            if rd < (1/3):
                naopy.nao_talk("Hahahaha je t''ai eu")
                naopy.nao_anim("animations/Sit/Emotions/Positive/Winner_1")
            elif rd < (2/3):
                naopy.nao_talk("La machine à surpasser l''homme")
            else:
                naopy.nao_talk("Tu veux retenter ?")
                naopy.nao_anim("animations/Sit/Emotions/Positive/Happy_1")
        else:
            rd = random.random()
            if rd < (1/3):
                naopy.nao_talk("Mince j''ai perdu")
                naopy.nao_anim("animations/Sit/Emotions/Negative/Sad_1")
            elif rd < (1/3):
                naopy.nao_talk("Bien joué, je vais m''améliorer.")
                naopy.nao_anim("animations/Sit/Emotions/Negative/Hurt_1")
            else:
                naopy.nao_talk("Tu veux rejouer ?")

    def save(self):
        pass

    def load(self):
        pass

    async def run(self):
        await super().init_train()
        while True:
            await asyncio.sleep(0)

if __name__ == '__main__':
    speech = NaoSpeech()
    AI_LOOP = asyncio.get_event_loop()
    try :
        AI_LOOP.run_until_complete(speech.run())
        print("fini")
    except KeyboardInterrupt :
        print("\nNao Speech killed.")
