# coding: utf-8
import sys
sys.path.append("../../")
import asyncio


from JoueurIA.Client import ClientInterface
import GlobalParameters as gp

class Stats(ClientInterface.ClientInterface):
    """ Classe Observatrice des parties, elle permet de calculer des statistiques."""

    def __init__(self, name = "statistique", file = None):
        """ Création d'une nouvelle instance d'observateur statistique.

        Paramètres :
            - name : String : nom de l'observateur
            - file : String : nom du fichier dans lequel écrire les statistiques

        Retour :
            Une nouvelle instance de Stats."""
        super().__init__(name, file, active=False)
        self.is_finished = False
        self.stats_first = MyStats(0) #stats liées à l'ia level 1  
        self.stats_second = MyStats(1) #stats liées à l'ia level 2 


    def update_play(self, data):
        """ Cette fonction est appelée à chaque tour après chaque action.
        Son comportement ici est de calculé les statistiques dépendantes de chacun de tours.

        Paramètres :
            - data : dictionnaire : message reçu de la part du serveur

        """
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
        """ Cette fonction est appelée à la fin de chaque partie. 
        Son comportement ici est de calculé des statistiques dépendantes de la fin de partie.

        Paramètres : 
            - data : dictionnaire : message reçu de la part du serveur.

            """
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
        """ Lance l'observation de (nb_games_to_observe) parties level1 vs level2

        Paramètres :
            - level1 : instance Level : représente une IA
            - level2 : instance Levek : représente une IA
            - nb_games_to_observe : int : nombre de partie que l'on souhaite observer entre ces deux adversaires.
        """
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
        """ Initialise l'observation pour pouvoir être appelé de l'extérieur pour observer des parties.
        Exemple : pour pouvoir être appelé pendant les entrainements."""
        await super().init_train()
        while self.my_client == None :
            asyncio.sleep(0)
        return self.my_client.pid


    def save(self):
        pass

    def load(self):
        pass

    def __str__(self) :
        """ Retourne une String représentant les statistiques observées."""
        return str(self.stats_first) + "\n\n" + str(self.stats_second)

class MyStats() :
    """ Classe nécessaire à Stats, c'est elle qui retient les informations observées pour calculer les statistiques. """

    def __init__(self, id) :
        """ Initialise une instance de MyStats et la retourne

        Paramètre : 
            - id : int : identifiant de l'instance
        """
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
        """ Retourne une String représentant les statistiques observées."""
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
    AI_LOOP = asyncio.get_event_loop()
    nb_game = 10
    for i in range(6):
        statistique = Stats()   
        AI_LOOP.run_until_complete(statistique.run(i, 0, nb_game))
        first = statistique.stats_first
        print("###########################################################")
        print(gp.LEVELS[i], 
             (first.wins_by_points + first.win_by_height)/nb_game,
             first.wins_by_points, first.win_by_height,
             sum(first.nb_lines)/nb_game,
             sum(first.scores)/nb_game,
             sep=", ")
        print("###########################################################")
        #print(statistique.stats_first, "\n\n" , statistique.stats_second)
