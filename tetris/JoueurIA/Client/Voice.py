# coding: utf-8
import sys
import os
sys.path.append("../")
sys.path.append("../../")
import copy
import random
import numpy as np
import asyncio
from collections import Counter

from JoueurIA.Client import Heuristic as H
from JoueurIA.Client import ClientInterface
from JoueurIA.Client import Grammar

import speech_recognition as sr
import re

class VoiceControl(ClientInterface.ClientInterface):
    def __init__(self):
        super().__init__("VoiceControl", None)
        self.recog = sr.Recognizer()

    def record(self):
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
    
    def recognize(self,audio):
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

    @classmethod
    def interpret(cls, spoken, state):
        extract_info = {"piece":[],"colonne":[],"direction":[],"rotate":[]}
        for sentence in spoken:
            sentence = sentence.lower()
            extract_info["piece"].append(Grammar.apply_basic_rule(Grammar.rule_piece,sentence))
            extract_info["colonne"].append(Grammar.apply_basic_rule(Grammar.rule_colonne, sentence))
            extract_info["direction"].append(Grammar.apply_basic_rule(Grammar.rule_direction, sentence))
            extract_info["rotate"].append(Grammar.apply_basic_rule(Grammar.rule_rotate, sentence))
            extract_info["valid"].append(Grammar.apply_basic_rule(Grammar.rule_valid, sentence))

        best_interpret = {}
        for k in extract_info:
            extract_info[k] = list(filter(None, extract_info[k]))
            if extract_info[k]:
                best_interpret[k] = Counter(extract_info[k]).most_common(1)[0][0]
            else:
                best_interpret[k] = None
        print(best_interpret)

    def traitement(self,interpret,state):
        action = {}
        if interpret["piece"] is not None:
            action["choose"] = state["pieces"][interpret["piece"] - 1]
        if interpret["colonne"] is not None:
            if interpret["direction"] is not None:
                action["hor_move"] = interpret["colonne"] * interpret["direction"]
        if interpret["rotate"] is not None:
            action["rotate"] = interpret["rotate"]
        if interpret["valid"] is not None:
            action["valid"] = interpret["valid"]
        return action
    
    def play(self, state):
        print("play")
        print(self.colors)
        while True:
            try:
                audio = self.record()
                spoken = self.recognize(audio)
                if spoken is not None:
                    interpret = VoiceControl.interpret(spoken, state)
                    action = self.traitement(interpret,state)
                    if action:
                        return action
            except KeyboardInterrupt:
                print("Would you cancel the record or quit ? (C/q)")
                rep = input()
                if rep == "" or rep == "C" or rep == "c":
                    continue
                else:
                    exit()

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
