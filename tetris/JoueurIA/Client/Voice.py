# coding: utf-8
import sys
import os
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
import copy
import random
import numpy as np
import asyncio
from collections import Counter

from JoueurIA.Client import Nao as naopy
from JoueurIA.Client import Heuristic as H
from JoueurIA.Client import ClientInterface
from JoueurIA.Client import Grammar

import speech_recognition as sr
import re

from concurrent.futures import ThreadPoolExecutor

class VoiceControl(ClientInterface.ClientInterface):
    def __init__(self):
        super().__init__("VoiceControl", None)
        self.recog = sr.Recognizer()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.play_coro = None

    async def record(self):
        def _record(self):
            audio = None
            while True:
                with sr.Microphone() as source:
                    self.recog.adjust_for_ambient_noise(source)
                    print("Say something!")
                    try:
                        audio = self.recog.listen(source,timeout=10, phrase_time_limit=10)
                    except sr.WaitTimeoutError:
                        print("Timeout exception")
                        continue
                    print("Record done !")
                    return audio
        return await asyncio.wrap_future(self.executor.submit(_record, self))
    
    async def recognize(self,audio):
        def _recognize(self, audio):
            spoken = []
            try:
                alternative = self.recog.recognize_google(audio, language="fr-FR", show_all=True)
                print("You said: ")
                if not alternative:
                    return
                for transcript in alternative["alternative"]:
                    spoken.append(transcript["transcript"])
                print(spoken)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                return
            return spoken
        return await asyncio.wrap_future(self.executor.submit(_recognize, self, audio))

    def interpret(self, spoken, state):
        interprets = []
        UnvalaibleChooseException = False
        ShapeAndColorNotMatchException = False
        HorMoveException = False
        for sentence in spoken:
            try:
                parse_tree = Grammar.parser.parse(sentence.lower())
            except Grammar.peg.NoMatch as e:
                print("NoMatchError: ",e)
                continue
            try:
                visit = Grammar.Visit(colors = self.colors,state=state,debug=True)
                result = Grammar.peg.visit_parse_tree(parse_tree,visit)
                print ("result",result)
                print("visit: ",visit.mess)
                interprets.append(visit.mess)
            except Grammar.ShapeAndColorNotMatchException:
                print("Grammar.ShapeAndColorNotMatchException")
                ShapeAndColorNotMatchException = True
                continue
            except Grammar.HorMoveException:
                print("Grammar.HorMoveException")
                HorMoveException = True
                continue
            except Grammar.UnvalaibleChooseException:
                print("Grammar.UnvalaibleChooseException")
                UnvalaibleChooseException = True
                continue
        if not interprets :
            if UnvalaibleChooseException:
                naopy.nao_talk(
                    "La pièce sélectionnée n''est pas disponible ce tour-ci.")
            elif ShapeAndColorNotMatchException:
                naopy.nao_talk(
                    "La forme et la couleur ne correspondent à aucune pièce.")
            elif HorMoveException:
                naopy.nao_talk(
                    "Problème inconnu avec le déplacement horizontal.")
            else :
                naopy.nao_talk("Je n''ai pas compris ce que tu voulais faire.")
            return
        else :
            command = {}
            for d in interprets:
                for k in d:
                    try:
                        command[k].append(d[k])
                    except KeyError :
                        command[k]=[d[k]]
                        continue
            for key in command:
                command[key] = Counter(command[key]).most_common(1)[0][0]
            print("command",command)
            return command
        
    async def play(self, state):
        while True:
            asyncio.sleep(0)
            try:
                audio_coro = asyncio.Task(self.record())
                audio = await audio_coro
            except asyncio.CancelledError:
                audio_coro.cancel()
                return
            try:
                spoken_coro = asyncio.Task(self.recognize(audio))
                spoken = await spoken_coro
            except asyncio.CancelledError:
                spoken_coro.cancel()
                return
            if spoken is not None:
                action = self.interpret(spoken, state)
                if action:
                    return action

    async def run(self):
        await super().init_train()
        await super().new_game(players=[[self.my_client.pid, 1]], viewers=[0], ias=[[2, 1]])
        while True:
            await asyncio.sleep(0)

    def on_init_game(self, data):
        self.ids_in_game = data["ids_in_game"]
        self.colors = {v: k for k,v in data["color"].items()}

    def update_play(self, data):
        if data["actual_player"] not in self.ids_in_game:
            self.play_coro.cancel()

if __name__ == '__main__':
    voice = VoiceControl()
    AI_LOOP = asyncio.get_event_loop()
    try :
        AI_LOOP.run_until_complete(voice.run())
        print("fini")
    except KeyboardInterrupt :
        print("\nVoice control killed.")
