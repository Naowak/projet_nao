# coding: utf-8
import sys
sys.path.append('../')
import random
from JoueurIA import Trainable_AI

class Genetic_IA(Trainable_AI.TrainableIA):
    def __init__(self, name, heuristic, weights = None, file=None, selection_size = 10, population_size = 100):
        super().__init__(name,file)
        self.weights = weights
        self.population = None
        self.selection_size = selection_size
        self.population_size = population_size
        self.score = None
        self.current_eval = None
        self.current_game_is_finish = None

    def generate_population(self):
        self.population = [np.random.randn(1, len(self.heuristic)) for _ in  range(self.population_size)]

    def make_selection(self):
        population = []
        for _ in range(self.selection_size):
            ind += argmax(self.score)
            population += self.population[ind]
            del self.population[ind]
            del self.score[ind]
        self.population = population

    def reproduction(self):
        ave = average(self.population)
        var = cov(self.polutation)
        self.population = []
        for _ in range(self.population_size):
            self.population += [np.random.randn(1, len(self.heuristic)]) .* ave + var]


    def evaluate(self):
        for i in range(len(self.population))
            self.score[i] = 0
            self.current_game_is_finish = False
            for _ in range(self.evaluate_size)
                super().new_game(1)
                while self.current_game_is_finish:
                    await asyncio.sleep(0)
        return score
    
    def mutation():
        for vect in self.population:
            vect += np.random.randn(1, len(self.heuristic))

    def train(self,features):
        super().init_train()
        self.generate_population()
        while average(score-last_score) > 0.1:
            last_score = self.score
            score = self.evaluate(features)
            self.make_selection()
            self.reproduction()
            self.mutation()
        self.save()

    def play(self, state):
        return self.best_move(self.population[self.current_eval],self.heuristic)

    def on_finished_game(self,data):
        if self.my_client.ids_in_games[0] == argmax(data["score"]):
            self.score += 1
        self.current_game_is_finish = True

    def save(self):
        self.weights = self.population[argmax(self.score)]
        print(self.weights)
        if self.file is not None:
            pass

    def load(self,file):
        if self.file is not None:
            # on recpupere dans un fichier

if __name__ == "__main__":
    genetic_ia = Genetic_IA("genetic")
    genetic_ia.train()
