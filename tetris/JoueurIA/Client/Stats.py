# coding: utf-8
import sys
sys.path.append("../../")
import asyncio


from JoueurIA.Client import ClientInterface
import GlobalParameters as gp

class Stats(ClientInterface.ClientInterface):
    def __init__(self, name = "statistique", file = None):
        super().__init__(name, file, active=False)
        self.is_finished = False
        self.stats_first = MyStats(0) #stats liées à l'ia level 1  
        self.stats_second = MyStats(1) #stats liées à l'ia level 2 


    def update_play(self, data):
        player = data["actual_player"]
        nb_points_gagne = 0
        nb_lines = 0

        if player == 0 :
            nb_points_gagne = data["score"][self.stats_first.id] - self.stats_first.score_last_turn
        else :
            nb_points_gagne = data["score"][self.stats_second.id] - self.stats_first.score_last_turn

        if nb_points_gagne == 40 :
            nb_lines = 1
        elif nb_points_gagne == 100 :
            nb_lines = 2
        elif nb_points_gagne == 300 :
            nb_lines = 3
        elif nb_points_gagne == 1200 :
            nb_lines = 4

        if player == self.stats_first.id :
            self.stats_first.score_last_turn = data["score"][self.stats_first.id]
            self.stats_first.nb_line_current_game += nb_lines
        else :
            self.stats_second.score_last_turn = data["score"][self.stats_second.id]
            self.stats_second.nb_line_current_game += nb_lines

    async def play(data) :
        pass

    def on_init_game(self, data):
        pass

    def on_finished_game(self,data):
        self.score_last_turn = 0
        self.is_finished = True

        #On gère les scores et les wins
        score_player1 = data["score"][self.stats_first.id]
        score_player2 = data["score"][self.stats_second.id]

        self.stats_first.scores += [score_player1]
        self.stats_second.scores += [score_player2]

        if score_player1 == gp.SCORE_DEPASSEMENT :
            self.stats_first.loose_by_height += 1
            self.stats_second.win_by_height += 1

        elif score_player2 == gp.SCORE_DEPASSEMENT :
            self.stats_second.loose_by_height += 1
            self.stats_first.win_by_height += 1

        elif score_player1 > score_player2 :
            self.stats_first.wins_by_points += 1
            self.stats_second.loose_by_points += 1

        elif score_player2 > score_player1 :
            self.stats_first.loose_by_points += 1
            self.stats_second.wins_by_points += 1

        elif score_player2 == score_player1 :
            self.stats_first.egalite += 1
            self.stats_second.egalite += 1

        #on gère les lignes réalisées
        self.stats_first.nb_lines += [self.stats_first.nb_line_current_game]
        self.stats_second.nb_lines += [self.stats_second.nb_line_current_game]
        self.stats_first.nb_line_current_game = 0
        self.stats_second.nb_line_current_game = 0



    async def run(self, level1, level2, nb_games_to_observe = 10) :
        await super().init_train()
        for _ in range(nb_games_to_observe) :
            if level1==level2:
                ias=[[level1,2]]
            else:
                ias=[[level1,1],[level2,1]]
            await super().new_game(ias=ias,viewers=[0,self.my_client.pid])
            self.is_finished = False
            while not self.is_finished :
                await asyncio.sleep(0)

    async def observe(self) :
        await super().init_train()
        while self.my_client == None :
            asyncio.sleep(0)
        return self.my_client.pid


    def save(self):
        pass

    def load(self):
        pass

    def __str__(self) :
        return str(self.stats_first) + "\n\n" + str(self.stats_second)

class MyStats() :
    def __init__(self, id) :
        self.id = id

        self.nb_line_current_game = 0
        self.score_last_turn = 0

        self.nb_lines = list()
        self.scores = list()
        self.wins_by_points = 0
        self.loose_by_points = 0
        self.win_by_height = 0
        self.loose_by_height = 0
        self.egalite = 0

    def __str__(self) :
        string = "ID = " + str(self.id) + "\n"
        string += "Parties gagnées (points, ko) : " + str(self.wins_by_points + self.win_by_height) \
            + "(" + str(self.wins_by_points) + ", " + str(self.win_by_height) + ")\n"
        string += "Parties perdues (points, ko) : " + str(self.loose_by_points + self.loose_by_height) \
            + "(" + str(self.loose_by_points) + ", " + str(self.loose_by_height) + ")\n"
        string += "Egalité : " + str(self.egalite) + "\n"
        string += "Nombre de lignes réalisées : " + str(self.nb_lines) + "\n"
        string += "Scores obtenus : " + str(self.scores) + "\n"
        return string


if __name__ == "__main__":
    statistique = Stats()
    AI_LOOP = asyncio.get_event_loop()
    AI_LOOP.run_until_complete(statistique.run(3, 3))
    print(statistique.stats_first, "\n\n" , statistique.stats_second)
