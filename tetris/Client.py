#coding : utf-8
import json
import random
import sys

import asyncio
import websockets

import GlobalParameters as gp

URI = gp.ADRESSE + str(gp.PORT)


class Client:
    def __init__(self, user="player", is_human=True):
        self.user = user
        self.my_socket = None
        self.keep_connection = True
        self.player_number = 0
        self.is_human = is_human

    async def connect(self, uri=URI):
        self.my_socket = await websockets.connect(uri)
        await self.send_message({"user": self.user, "name": "Pierre"})
        data = await self.receive_message()
        self.player_number = data["id"]
        while self.keep_connection:
            await asyncio.sleep(0)

    def make_connection_to_server(self):
        asyncio.ensure_future(self.connect())

    async def receive_message(self):
        mess = await self.my_socket.recv()
        return json.loads(mess)

    async def send_message(self, data):
        await self.my_socket.send(json.dumps(data))

    async def play(self):
        data = await self.receive_message()
        if data["actual_player"] == self.player_number:
            if data["step"] == "init":
                self.keep_connection = False
            elif data["step"] == "piece_choice":
                if self.is_human is True:
                    piece = ask_human_piece_to_choose(data["pieces"])
                else:
                    piece = ask_ia_piece_to_choose(data["pieces"])
                await self.send_message({"kind": piece})
            elif data["step"] == "rotation":
                if self.is_human is True:
                    rotate = ask_human_rotate()
                else:
                    rotate = ask_ia_rotate()
                await self.send_message({"rotate": rotate})
            elif data["step"] == "abscisse":
                if self.is_human is True:
                    abscisse = str(ask_human_abscisse())
                else:
                    abscisse = str(ask_ia_abscisse())
                await self.send_message({"abscisse": abscisse})
            elif data["step"] == "finished":
                self.keep_connection = False


def ask_human_piece_to_choose(kinds):
    test = False
    kind = ""
    while not test:
        print("Choose a piece from those pieces : ")
        for i in kinds:
            print(i + " ")
        print("\n")
        kind = input()
        if kind in kinds:
            test = True
    return kind


def ask_ia_piece_to_choose(kinds):
    return random.choice(kinds)


def ask_human_rotate():
    print("To rotate de piece enter 'R', else press 'Enter' : ")
    choose = input()
    return choose


def ask_ia_rotate():
    return random.choice(["R", ""])


def ask_human_abscisse():
    print("Please enter an valid abscisse : ")
    choose = int(input())
    return choose


def ask_ia_abscisse():
    return random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


async def main():
    mon_client = None
    if len(sys.argv) >= 2 and sys.argv[1] == "IA":
        mon_client = Client(is_human=False)
    else:
        mon_client = Client()
        mon_client.make_connection_to_server()
    while	mon_client.my_socket is None:
        await asyncio.sleep(0)
    while	mon_client.keep_connection:
        await	mon_client.play()
        await asyncio.sleep(0.3)

asyncio.get_event_loop().run_until_complete(main())
