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
from JoueurIA.Client import Stats


class Train_Entropy(ClientInterface.ClientInterface):
    def __init__(self, name, heuristic = [], load_file = None, selection_size = 10, population_size = 50, evaluate_size = 5, nb_generation = 10, is_stats = False, file_stats = None):
        super().__init__(name,load_file)
        self.weights = list()
        self.heuristic = {}
        self.population = list()
        self.evaluate_size = evaluate_size
        self.selection_size = selection_size
        self.population_size = population_size
        self.score = list()
        self.current_eval = None
        self.current_game_is_finish = None
        self.nb_generation = nb_generation
        self.is_stats = is_stats
        self.my_stats = None
        self.pid_stats = None
        self.file_stats = file_stats

        if load_file != None :
            #si on charge une Level
            self.load()
        elif len(heuristic) > 0 :
            #Level non existante, on doit en créer une nouvelle aléatoire
            self.define_heuristic(heuristic)
        else :
            #pas d'ia chargé et aucune heuristic donné : erreur
            raise Exception("ERROR : Aucun fichier n'a été passé en paramètre pour charger une Level et aucune heuristique n'a été définie, l'Level ne peut se créer.")

    def define_heuristic(self, heuristic_list) :
        for h in heuristic_list : 
            if h == "line_transition" :
                self.heuristic[h] = H.line_transition
            elif h == "column_transition" :
                self.heuristic[h] = H.column_transition
            elif h == "holes" : 
                self.heuristic[h] = H.holes
            elif h == "wells" :
                self.heuristic[h] = H.wells
            elif h == "score" :
                self.heuristic[h] = H.score
            elif h == "height" :
                self.heuristic[h] = H.height
            elif h == "hidden_empty_cells" :
                self.heuristic[h] = H.hidden_empty_cells
            elif h == "erosion" :
                self.heuristic[h] = H.erosion
            else :
                raise NameError("This heuristic ", h, " is not defined")
        

    def generate_population(self):
        #si l'Level est déjà définie
        if self.weights is None:
            self.population = [np.random.randn(len(self.heuristic)) for _ in  range(self.population_size)]
        #Sinon elle est définie aléatoirement 
        else:
            self.population = []
            for _ in range(self.population_size):
                self.population.append(np.random.randn(len(self.heuristic)))
    
    def make_selection(self):
        population = []
        score = []
        for _ in range(self.selection_size):
            ind = np.argmax(self.score)
            population.append(self.population[ind])
            score.append(self.score[ind])
            del self.population[ind]
            del self.score[ind]
        self.population = population
        self.score = score

    def reproduction(self):
        ave = np.average(self.population,axis=0,weights = self.score)
        var = np.cov(self.population,rowvar=False)
        self.population = []
        for _ in range(self.population_size):
            self.population.append(np.dot(np.random.randn(len(self.heuristic)),var) + ave)

    async def evaluate(self):
        self.score = [0 for i in range(len(self.population))]
        for i in range(len(self.population)):
            self.current_game_is_finish = False
            self.current_eval = i
            for _ in range(self.evaluate_size):
                if self.is_stats :
                    #Si on récupère les stats de l'entrainement, on l'ajoute au spec
                    await super().new_game(players=[[self.my_client.pid,1]],ias=[[3,1]],viewers=[0, self.pid_stats])
                else :
                    await super().new_game(players=[[self.my_client.pid,1]],ias=[[3,1]],viewers=[0])
                while not self.current_game_is_finish:
                    await asyncio.sleep(0)
                self.current_game_is_finish = False
    
    def mutation(self):
        for vect in self.population:
            #une chance sur 5 de subir une mutation
            if random.random() < 0.2 :
                #on choisie une composante du vect aléatoirement
                ind = random.choice(list(range(len(vect))))
                #une chance sur deux que ce soit un retrait ou un ajout
                if random.random() < 0.5 :
                    vect[ind] += random.random()*0.2
                else :
                    vect[ind] += random.random()*(-0.2)

    async def train(self):
        if self.is_stats :
            self.my_stats = Stats.Stats()
            self.pid_stats = await self.my_stats.observe()

        await super().init_train()
        print("Train begin!")
        self.generate_population()
        self.score = [0 for i in range(len(self.population))]
        begin = True
        #while np.mean(self.score)-np.mean(last_score) > 0.1 or begin:
        for _ in range(self.nb_generation) :
            if not begin :
                self.reproduction()
                self.mutation()
                print("\nReproduction + mutation: ", self.population)
            begin = False
            print("\nEvaluation : ", self.population)
            await self.evaluate()
            print("\nPopulation : ", self.population)
            self.make_selection()
            print("\nSélection : ", self.population)
        self.save()

    async def play(self, state):
        return H.best_move(list(self.heuristic.values()),self.population[self.current_eval],state)

    def on_finished_game(self,data):
        ind = self.my_client.ids_in_games[data["gid"]][0]
        diff = data["score"][ind] - data["score"][(ind+1)%2]
        diff_square = np.power(diff, 2)
        if diff < 0 :
            self.score[self.current_eval] -= diff_square
        else :
            self.score[self.current_eval] += diff_square
        self.current_game_is_finish = True

    def save(self):
        print("Would you like to save this current AI ? (Y/n)")
        rep = input()
        file_name = ""
        if rep == "" or rep == "y" or  rep == "Y":
            self.weights = self.population[np.argmax(self.score)]
            print("\nMeilleur vecteur final :", self.weights)
            path = "backup/"
            name = "entropy_"
            extension = ".save"
            f = None

            #open a file
            if self.file == None :
                for i in range(10000) :
                    file_name = path + name + str(i) + extension
                    if not os.path.isfile(file_name) :
                        f = open(file_name, "w+")
                        break
                #si tout est pris on écrase
                if f == None :
                    f = open(file_name, "w+")
            else :
                file_name = self.file
                f = open(self.file, "w+")

            #on enregistre dedans
            for i in range(len(self.weights)) :
                keys = list(self.heuristic.keys())
                f.write(keys[i] + " " + str(self.weights[i]) + "\n")
            f.close()
            print("Current Level saved in : ", file_name)
        
    def load(self):
        #on vérifie que le fichier existe :
        if os.path.isfile(self.file) :
            f = open(self.file, "r")
            cpt = 0
            heuristic_list = list()
            #on charge les heuristics demandées ainsi que leur poids
            for line in f :
                tab = line.split(" ")
                heuristic_list.append(tab[0])
                self.weights.append(float(tab[1]))
            self.define_heuristic(heuristic_list)
        #sinon erreur               
        else :
            raise FileNotFoundError(self.file + " doesn't exist.")


#------------------------ Pour deux IAs -------------------------------------------


async def evaluate_two_ias(ia_one, ia_two, is_stats, pid_stats):
    ia_one.score = [0 for i in range(len(ia_one.population))]
    ia_two.score = [0 for i in range(len(ia_two.population))]

    nb_games_one = [0 for i in range(len(ia_one.population))]
    nb_games_two = [0 for i in range(len(ia_two.population))]

    #idée : on prends chacun des éléments de la population et on le fait s'affronter contre evaluate_size élems de la population de l'IA concurrente
    for i in range(len(ia_one.population)) :
        ia_one.current_game_is_finish = False
        ia_one.current_eval = i
        for _ in range(ia_one.evaluate_size) :
            ia_two.current_game_is_finish = False
            ia_two.current_eval = random.choice(list(range(len(ia_two.population))))
            nb_games_one[ia_one.current_eval] += 1
            nb_games_two[ia_two.current_eval] += 1
            if is_stats :
                #Si on récupère les stats de l'entrainement, on l'ajoute au spec
                await ia_one.new_game(players=[[ia_one.my_client.pid,1], [ia_two.my_client.pid, 1]],ias=[],viewers=[0, pid_stats])
            else :
                await ia_one.new_game(players=[[ia_one.my_client.pid,1], [ia_two.my_client.pid, 1]],ias=[],viewers=[0])
            while not ia_one.current_game_is_finish :
                await asyncio.sleep(0)
            ia_one.current_game_is_finish = False
            ia_two.current_game_is_finish = False

    for i in range(len(ia_two.population)) :
        ia_two.current_game_is_finish = False
        ia_two.current_eval = i
        for _ in range(ia_one.evaluate_size) :
            ia_one.current_game_is_finish = False
            ia_one.current_eval = random.choice(list(range(len(ia_one.population))))
            nb_games_one[ia_one.current_eval] += 1
            nb_games_two[ia_two.current_eval] += 1
            if is_stats :
                #Si on récupère les stats de l'entrainement, on l'ajoute au spec
                await ia_two.new_game(players=[[ia_two.my_client.pid,1], [ia_one.my_client.pid, 1]],ias=[],viewers=[0, pid_stats])
            else :
                await ia_two.new_game(players=[[ia_two.my_client.pid,1], [ia_one.my_client.pid, 1]],ias=[],viewers=[0])
            while not ia_two.current_game_is_finish :
                await asyncio.sleep(0)
            ia_one.current_game_is_finish = False
            ia_two.current_game_is_finish = False

    #Toutes les ia ne font pas nécessairement le même nombre de partie, donc on prends le score moyen
    for i in range(len(ia_one.population)) :
        ia_one.score[i] /= nb_games_one[i]

    for i in range(len(ia_two.population)) :
        ia_two.score[i] /= nb_games_two[i]



async def train_two_ias(ia_one, ia_two, is_stats = False, file_stats = None):
    if ia_one.nb_generation != ia_two.nb_generation :
        return

    nb_generation = ia_one.nb_generation

    my_stats = None
    pid_stats = None
    if is_stats :
        my_stats = Stats.Stats()
        pid_stats = await my_stats.observe()

    await ia_one.init_train()
    await ia_two.init_train()
    print("Train begin!")

    ia_one.generate_population()
    ia_two.generate_population()

    ia_one.score = [0 for i in range(len(ia_one.population))]
    ia_two.score = [0 for i in range(len(ia_one.population))]

    begin = True
    for _ in range(nb_generation) :
        if not begin :
            ia_one.reproduction()
            ia_one.mutation()
            print("\nReproduction + mutation de IA-ONE: ", ia_one.population)
            ia_two.reproduction()
            ia_two.mutation()
            print("\nReproduction + mutation de IA-TWO: ", ia_two.population)
        begin = False

        print("\nEvaluation IA-ONE: ", ia_one.population)
        print("\nEvaluation IA-TWO: ", ia_two.population)
        await evaluate_two_ias(ia_one, ia_two, is_stats, pid_stats)

        print("\nPopulation IA-ONE: ", ia_one.population)
        print("\nPopulation IA-TWO: ", ia_two.population)
        ia_one.make_selection()
        ia_two.make_selection()

        print("\nSélection IA-ONE: ", ia_one.population)
        print("\nSélection IA-TWO: ", ia_two.population)
    ia_one.save()
    ia_two.save()

    print("Train over !")

    if is_stats :
        print("\n\n", my_stats)
        f = open(file_stats, 'w')
        f.write(str(my_stats))


if __name__ == "__main__":
    stats = False
    my_file_stats = None
    if len(sys.argv) == 2 and sys.argv[1] == "--stats" :
        stats = True
    elif len(sys.argv) == 3 and sys.argv[1] == "--stats" :
        stats = True
        my_file_stats = sys.argv[2]

    #genetic_ia = Train_Entropy("genetic", load_file = "./backup/6_heuristic.save", is_stats = stats, file_stats = my_file_stats)
    ia_one = Train_Entropy("genetic", heuristic=["line_transition", "column_transition", "holes",  \
        "wells", "score", "height", "hidden_empty_cells", "erosion"],  \
        selection_size = 2, population_size = 5, evaluate_size = 1, nb_generation = 3)
    ia_two = Train_Entropy("genetic", heuristic=["line_transition", "column_transition", "holes",  \
        "wells", "score", "height", "hidden_empty_cells", "erosion"],  \
        selection_size = 2, population_size = 5, evaluate_size = 1, nb_generation = 3)


    AI_LOOP = asyncio.get_event_loop()
    
    try :
        AI_LOOP.run_until_complete(train_two_ias(ia_one, ia_two, stats, my_file_stats))
    except KeyboardInterrupt :
        print("\nEntrainement arrêté manuellement.")
        genetic_ia.save()
    # if stats :
    #     print("\n\n", my_stats)
    #     f = open(file_stats, 'w')
    #     f.write(str(genetic_ia.my_stats))
