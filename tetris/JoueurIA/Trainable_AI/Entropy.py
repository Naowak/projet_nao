# coding: utf-8
import sys
sys.path.append("../")
sys.path.append("../../")
import copy
import random
import numpy as np
import asyncio

from JoueurIA.Trainable_AI import Heuristic as H
from JoueurIA.Trainable_AI import Trainable_AI

class Genetic_IA(Trainable_AI.TrainableIA):
    def __init__(self, name, heuristic, weights = None, file=None, selection_size = 1, population_size = 1, evaluate_size = 1):
        super().__init__(name,file)
        self.weights = weights
        self.population = None
        self.evaluate_size = evaluate_size
        self.selection_size = selection_size
        self.population_size = population_size
        self.score = None
        self.heuristic = heuristic
        self.current_eval = None
        self.current_game_is_finish = None

    def generate_population(self):
        if self.weights is None:
            self.population = [np.random.randn(len(self.heuristic)) for _ in  range(self.population_size)]
        else:
            self.population = []
            for _ in range(self.population_size):
                self.population.append(np.random.randn(len(self.heuristic)) + self.weights)
    
    def make_selection(self):
        population = []
        score = copy.copy(self.score)
        for _ in range(self.selection_size):
            ind = np.argmax(score)
            population.append(self.population[ind])
            del self.population[ind]
            del score[ind]
        self.population = population
        #print(self.population)

    def reproduction(self):
        ave = np.average(self.population,axis=0)
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
                await super().new_game(2)
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
        await super().init_train()
        print("Train begin!")
        self.generate_population()
        last_score = [0 for i in range(len(self.population))]
        self.score = [0 for i in range(len(self.population))]
        begin = True
        #while np.mean(self.score)-np.mean(last_score) > 0.1 or begin:
        for _ in range(1) :
            if not begin :
                self.score = [0 for i in range(len(self.population))]
                self.reproduction()
                self.mutation()
                print("\nReproduction + mutation: ", self.population)
            begin = False
            last_score = self.score
            print("\nEvaluation : ", self.population)
            await self.evaluate()
            print("\nPopulation : ", self.population)
            print(self.score)
            self.make_selection()
            print("\nSélection : ", self.population)
        self.save()

    def play(self, state):
        if not self.my_client is None :
            return H.best_move(self.heuristic,self.population[self.current_eval],state)
        else :
            return H.best_move(self.heuristic,self.weights,state)

    def on_finished_game(self,data):
        if not self.my_client is None:
            ind = self.my_client.ids_in_games[data["gid"]][0]
            self.score[self.current_eval] += data["score"][ind] - data["score"][(ind+1)%2]
            self.current_game_is_finish = True

    def save(self):
        print(self.score)
        self.weights = self.population[np.argmax(self.score)]
        print("\nMeilleur vecteur final :", self.weights)
        if self.file is not None:
            pass

    def load(self,file):
        if self.file is not None:
            pass
            # on recpupere dans un fichier

if __name__ == "__main__":
    genetic_ia = Genetic_IA("genetic", [H.line_transition,H.column_transition,H.holes,H.wells],\
                            weights = np.array([-1.04341569,  0.19629992, -0.63325367, -1.0576598]))
    AI_LOOP = asyncio.get_event_loop()
    AI_LOOP.run_until_complete(genetic_ia.train())
