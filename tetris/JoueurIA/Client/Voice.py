# coding: utf-8
import sys
import os
sys.path.append("../")
sys.path.append("../../")
import copy
import random
import numpy as np
import asyncio

from JoueurIA.Client import Heuristic as H
from JoueurIA.Client import ClientInterface

import speech_recognition as sr
import re

class VoiceControl(ClientInterface.ClientInterface):
    def __init__(self):
        super().__init__("VoiceControl", None)
        self.recog = sr.Recognizer()

    def play(self, state):
        print("play")
        print(self.colors)

        while True:
            with sr.Microphone() as source:
                self.recog.adjust_for_ambient_noise(source)
                print("Say something!")
                audio = self.recog.listen(source, timeout=10, phrase_time_limit=10)
            spoken = ""
            try:
                spoken = self.recog.recognize_google(audio, language="fr-FR")
                print("You said: " + spoken)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            spoken = spoken.lower()
            #match = re.findall("poser la pièces? (\w+) (\w+) colonnes? à (\w+)(?: tourn(?:é|ée|és|ez|er) (\w+) fois)?",
            #                   "poser la pièce une deux colonnes à droite")
            match = re.findall("poser la pièces? (\w+) (\w+) colonnes? à (\w+)(?: tourn(?:é|ée|és|ez|er) (\w+) fois)?", spoken)
            if(len(match) != 0):
                items = list(match[0])
                transform = {"un":1, "une":1, "de":2, "deux":2, "trois":3, "quatre":4, "cinq":5, "six":6, "sept":7, "huit":8, "neuf":9, "dix":10}
                items = [(transform[i] if i in transform else i) for i in items]
                if(items[3] == ""):
                    items[3] = 0


                if (items[0] not in [1,2,3]) or (items[1] not in [0,1,2,3,4,5]) or (items[2] not in ["droite","gauche"]) or (items[3] not in [0,1,2,3,4]):
                    continue
                print(items[0],items[1],items[2],items[3])
                return {"hor_move": items[1]*(-1 if items[2]=="gauche" else 1), "rotate": items[3], "choose": state["pieces"][items[0]-1]}
            else:
                continue



    async def run(self):
        await super().init_train()
        await super().new_game(players=[[self.my_client.pid, 1]], viewers=[4], ias=[[2, 1]])
        while True:
            await asyncio.sleep(0)

    def on_init_game(self, data):
        self.colors = data["color"]

if __name__ == '__main__':
    voice = VoiceControl()
    AI_LOOP = asyncio.get_event_loop()
    try :
        AI_LOOP.run_until_complete(voice.run())
        print("fini")
    except KeyboardInterrupt :
        print("\nVoice control killed.")