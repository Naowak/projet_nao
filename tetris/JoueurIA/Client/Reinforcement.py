# coding: utf-8
import sys
import os
import asyncio
import time
import argparse

sys.path.append("../")
sys.path.append("../../")

from tensorforce.agents import DQNAgent
from GlobalParameters import *
from utilities import *

from JoueurIA.Client import ClientInterface, Heuristic, Stats
from Jeu import State


class Reinforcement(ClientInterface.ClientInterface):
    def __init__(self, name, load_file=None, is_stats=False, file_stats=None,
                 train_adversary_level=2, nb_batches=5000, nb_games_per_batch=2,
                 layer_size=15, nb_layers=3):
        """
        :param name: name of the IA/
        :param load_file: path and name of the model to load (without any extension).
        :param is_stats: boolean which tells whether the statistics are enabled.
        :param file_stats: name of the file where the statistics are written.
        :param train_adversary_level: integer indicating the AI to train against (corresponds to level in AICreator).
        :param nb_batches: number of batches. A batch is a group of successive games on which the ratio
        (nb_won_games / nb_games_per_batch) is computed and saved in score.txt.
        :param nb_games_per_batch: number of games per batch.
        :param layer_size: size of a neural network layer.
        :param nb_layers: number of layers in the neural network.
        """

        super().__init__(name, load_file)
        
        self.current_game_is_finish = None
        self.first_game = True
        
        # score
        self.score_self_old, self.score_self_new = 0, 0
        self.score_other_old, self.score_other_new = 0, 0
        self.file_scores = open('scores.txt', 'w')
        
        # AI parameters
        self.heuristics = [Heuristic.line_transition,
                           Heuristic.column_transition,
                           Heuristic.hidden_empty_cells,
                           Heuristic.wells,
                           Heuristic.holes,
                           Heuristic.highest_column,
                           Heuristic.columns_heights]

        state = State.State()
        heuristics_sizes = [heuristic(state, state, None) for heuristic in self.heuristics]
        self.nb_heuristics = len(flatten(heuristics_sizes))
        print('self.nb_heuristics', heuristics_sizes)
        self.train_adversary_level = train_adversary_level
        
        # iteration
        self.nb_batches = nb_batches
        self.nb_games_per_batch = nb_games_per_batch
        self.iteration = 0
        
        # neural network
        self.layer_size = layer_size
        self.nb_layers = nb_layers
        network_spec = [dict(type='dense', size=self.layer_size, activation='relu')] * self.nb_layers

        self.agent = DQNAgent(states_spec={'shape': (self.nb_heuristics + NOMBRE_DE_PIECES,), 'type': 'float'},
                              actions_spec={'hor_move': {'type': 'int', 'num_actions': 11},
                                            'rotate': {'type': 'int', 'num_actions': 4},
                                            'choose': {'type': 'int', 'num_actions': 3}},
                              network_spec=network_spec)
        
        # loading of a saved model
        if load_file is not None:
            self.load(load_file)
        
        # stats
        self.is_stats = is_stats
        self.my_stats = None
        self.file_stats = file_stats
        self.pid_stats = None

    async def play(self, state):
        """
        Associates an action to a state. Called by the server.
        :param state: dictionary containing information about the game, send by the server.
        :return: action to apply.
        """

        # update all the scores (self.score_self_new, self.score_self_old, self.score_other_new, self.score_other_old)
        self.update_scores(state)

        # format the state to make it compatible with tensorforce
        state_formatted = self.format_state(state)

        if self.first_game:  # at the first game and first call to function play, no action has been performed yet ->
            # nothing to observe
            self.first_game = False
            self.agent.reset()
        else:
            # pass observation to the agent
            terminal = False
            reward = (self.score_self_new - self.score_self_old) - (self.score_other_new - self.score_other_old)
            self.agent.observe(terminal, reward)

        # select the action (exploitation or exploration)
        action = self.agent.act(state_formatted)

        # format the action to make it exploitable by the Tetris game
        action_to_apply = self.format_action(action, state)

        return action_to_apply
        # return {"hor_move": -2, "rotate": 1, "choose": state["pieces"][0]}

    def on_init_game(self, data):
        """
        Called at the beginning of a game.
        :param data: dictionary containing information about the game, send by the server.
        """

        print()
        print(self.iteration)

        self.my_id_in_game = data["ids_in_game"][0]

    def on_finished_game(self, data):
        """
        Called at the end on a game.
        :param data: dictionary containing information about the game, send by the server.
        """

        self.iteration += 1

        self.current_game_is_finish = True

        # update all the scores
        self.update_scores(data)

        # pass observation to the agent
        terminal = True
        reward = (self.score_self_new - self.score_self_old) - (self.score_other_new - self.score_other_old)
        self.agent.observe(terminal, reward)

    def update_scores(self, state):
        """
        Updates the scores of the agent and of the the other player.
        :param state: dictionary containing information about the game.
        """

        # update the old scores
        self.score_self_old, self.score_other_old = self.score_other_new, self.score_other_new

        # get the new scores
        self.score_self_new, self.score_other_new = self.format_score(state)

    @staticmethod
    def format_action(action, state):
        """
        Formats the action returned by tensorforce so that it can be used in the play function.
        :param action: action returned by tensorforce (function act).
        :param state: dictionary containing information about the game, send by the server.
        :return: dictionary containing the action.
        """

        # convert int32 (which is not serializable) to standard int
        action_to_apply = {key: int(value) for key, value in action.items()}

        action_to_apply['hor_move'] -= 5  # [0, 10] -> [-5, 5]
        action_to_apply['choose'] = state['pieces'][action_to_apply['choose']]  # index to letter

        return action_to_apply

    def evaluate_heuristics(self, heuristics, g_prec, g_next, action):
        """
        Computes the current values of the heuristic.
        :param heuristics: list containing the heuristic functions.
        :param g_prec: previous state.
        :param g_next: current state.
        :param action: action which allows to go from g_prec to g_next.
        :return: flat list containing the heuristics values (flattening is necessary because some heuristics are lists).
        """

        return flatten([heuristic(g_prec, g_next, action) for heuristic in heuristics])

    def format_state(self, state):
        """
        Formats the state so that it can be used by tensorforce.
        :param state: dictionary containing information about the game, send by the server.
        :return: list containing the heuristics values. Represents the state.
        """

        state_bis = State.State(state['grid'])
        heuristics_values = self.evaluate_heuristics(self.heuristics, None, state_bis, None)

        # selectable pieces as a one-shot vector
        pieces_one_hot = self.format_pieces(state['pieces'])

        # state used by tensorforce
        state_formatted = heuristics_values + pieces_one_hot

        print('{}, {}'.format(heuristics_values, pieces_one_hot))
        return state_formatted

    def format_pieces(self, pieces):
        """
        Formats the available pieces so that they can be used by tensorforce.
        :param pieces: 3-elements list containing letters representing pieces (no repetition).
        :return: 7-elements one-hot list containing 1 or 0.
        """

        pieces_formatted = [0] * NOMBRE_DE_PIECES

        for piece in pieces:
            pieces_formatted[self.char_to_int(piece)] = 1

        return pieces_formatted

    def format_score(self, state):
        """
        Extracts the score of the AI and of the other player.
        :param state: dictionary containing information about the game, send by the server.
        :return: score_self, score_other.
        """

        id_self = self.my_id_in_game
        id_other = (id_self + 1) % 2
        score_self = state['score'][id_self]
        score_other = state['score'][id_other]

        return score_self, score_other

    @staticmethod
    def char_to_int(char):
        """
        Converts a letter whose shape looks like a tetromino to a corresponding integer.
        :param char: 'O', 'I', 'L', 'T', 'S', 'Z' or 'J'.
        :return: integer from 0 to 6.
        """

        lu_table = {'O': 0, 'I': 1, 'L': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6}
        return lu_table[char]

    async def train(self):
        """
        Triggers the training.
        """

        await super().init_train()
        if self.is_stats:
            self.my_stats = Stats.Stats()
            self.pid_stats = await self.my_stats.observe()

        for _ in range(self.nb_batches):
            wins = 0
            for _ in range(self.nb_games_per_batch):
                if self.is_stats:
                    await super().new_game(players=[[self.my_client.pid, 1]],
                                           ias=[[self.train_adversary_level, 1]],
                                           viewers=[0, self.pid_stats])
                else:
                    await super().new_game(players=[[self.my_client.pid, 1]],
                                           ias=[[self.train_adversary_level, 1]],
                                           viewers=[0])

                self.current_game_is_finish = False

                while not self.current_game_is_finish:
                    await asyncio.sleep(0)

                self.current_game_is_finish = False
                
                # increment wins when a game is won
                wins += 1 if self.score_self_new > self.score_other_new else 0
            
            # save the scores in a file
            self.file_scores.write('{}\n'.format(wins / self.nb_games_per_batch))
            self.file_scores.flush()

        self.save()

    def save(self):
        """
        Saves the current model in directory rein_learn_models as 3 files.
        """

        #TODO: Dire si on a bien chargé
        # directory = os.path.join(os.getcwd(), 'rein_learn_models')
        time_str = time.strftime('%Y%m%d_%H%M%S')
        directory = os.path.join(os.getcwd(), 'rein_learn_models', 'agent_' + time_str)
        checkpoint = self.agent.save_model(directory=directory, append_timestep=True)
        print('directory: {}'.format(directory))
        print('checkpoint: {}'.format(checkpoint))

    def load(self, load_file):
        """
        Loads a saved model.
        :param load_file: path and name of the model to load (without any extension).
        """

        # load_file represent the file path (without any extension)
        directory = os.path.dirname(load_file)
        file = os.path.basename(load_file)

        self.agent.restore_model(directory=directory, file=file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Beep boop.')
    parser.add_argument('load_file', nargs='?', default=None, type=str, help='file to load')
    parser.add_argument('--stats', dest='my_file_stats', default=None, type=str, help='stats')               
        
    args = parser.parse_args()

    my_file_stats = args.my_file_stats
    my_stats = my_file_stats is not None

    ia = Reinforcement('reinforcement', is_stats=my_stats,
                                        file_stats=my_file_stats,
                                        train_adversary_level=1,
                                        nb_batches=5000,
                                        nb_games_per_batch=1,
                                        layer_size=15,
                                        nb_layers=3)
    AI_LOOP = asyncio.get_event_loop()
    try:
        AI_LOOP.run_until_complete(ia.train())
        print("fini")
    except KeyboardInterrupt:
        print("\nEntrainement arrêté manuellement.")
        ia.save()

    if my_stats:
        print("\n\n", ia.my_stats)
        f = open(ia.file_stats, 'w')
        f.write(str(ia.my_stats))
