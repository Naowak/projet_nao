import asyncio
from tensorforce.agents import DQNAgent

from Trainable_AI import TrainableIA

import speech_recognition as sr
import re

class VoiceControl(TrainableIA):
    def __init__(self):
        super().__init__("VoiceControl", None)
        self.recog = sr.Recognizer()

    def play(self, state):
        print(state)
        print(self.colors)

        with sr.Microphone() as source:
            print("Say something!")
            audio = self.recog.listen(source)
        spoken = ""
        try:
            spoken = self.recog.recognize_google(audio, language="fr-FR")
            print("You said: " + spoken)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        piece = re.findall()

    async def run(self):
        await super().init_train()
        await super().new_game(players=[[self.my_client.id, 1]], viewers=[5], ias=[[2, 1]])
        while True:
            await asyncio.sleep(0)

    def on_init_game(self, data):
        self.colors = data["colors"]

if __name__ == '__main__':
    voice = VoiceControl()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(voice.run())
