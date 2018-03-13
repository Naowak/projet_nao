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

from JoueurIA.Client import ClientInterface, Heuristic, Stats
from Jeu import State


class Reinforcement(ClientInterface.ClientInterface):
    def __init__(self, name, load_file=None, is_stats = False, file_stats = None):
        super().__init__(name, load_file)

        self.current_game_is_finish = None
        self.first_game = True
        self.nb_games = 5000
        self.score_self_old, self.score_self_new = 0, 0
        self.score_other_old, self.score_other_new = 0, 0
        self.scores_list = []
        self.file_scores = open('scores.txt', 'w')
        self.nb_heuristics = 4
        self.iteration = 0

        self.train_adversary_level = 1

        # Performance function
        self.wins = 0

        network_spec = [dict(type='dense', size=10, activation='relu'),
                        dict(type='dense', size=10, activation='relu'),
                        dict(type='dense', size=10, activation='relu'),
                        dict(type='dense', size=10, activation='relu')]

        self.agent = DQNAgent(states_spec={'shape': (self.nb_heuristics + NOMBRE_DE_CHOIX,), 'type': 'float'},
                              actions_spec={'hor_move': {'type': 'int', 'num_actions': 11},
                                            'rotate': {'type': 'int', 'num_actions': 4},
                                            'choose': {'type': 'int', 'num_actions': 3}},
                              network_spec=network_spec,
                              batch_size=64)

        if load_file is not None:
            self.load(load_file)
        
        self.is_stats = is_stats
        self.my_stats = None
        self.file_stats = file_stats
        self.pid_stats = None

    def play(self, state):
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
        print()
        print(self.iteration)

        self.my_id_in_game = data["ids_in_game"][0]

    def on_finished_game(self, data):
        self.iteration += 1

        self.current_game_is_finish = True

        # update all the scores (self.score_self_new, self.score_self_old, self.score_other_new, self.score_other_old)
        self.update_scores(data)

        # pass observation to the agent
        terminal = True
        reward = (self.score_self_new - self.score_self_old) - (self.score_other_new - self.score_other_old)
        self.agent.observe(terminal, reward)

        # update the list of scores
        self.scores_list.append([self.score_self_new, self.score_other_new])

        # save the scores in a file
        self.wins += 1 if self.score_self_new > self.score_other_new else 0
        self.file_scores.write("%f\n" % (self.wins / self.iteration))
        self.file_scores.flush()

    def update_scores(self, state):
        # update the old scores
        self.score_self_old, self.score_other_old = self.score_other_new, self.score_other_new

        # get the new scores
        self.score_self_new, self.score_other_new = self.format_score(state)

    @staticmethod
    def format_action(action, state):
        # convert int32 (which is not serializable) to standard int
        action_to_apply = {key: int(value) for key, value in action.items()}

        action_to_apply['hor_move'] -= 5  # [0, 10] -> [-5, 5]
        action_to_apply['choose'] = state['pieces'][action_to_apply['choose']]  # index to letter

        return action_to_apply

    def format_state(self, state):
        if self.nb_heuristics == 4:
            state_bis = State.State(state['grid'])
            heuristics = [Heuristic.line_transition(None, state_bis, None),
                          Heuristic.column_transition(None, state_bis, None),
                          Heuristic.holes(None, state_bis, None),
                          Heuristic.wells(None, state_bis, None)]
        # print('heuristics: ', heuristics)

        # selectable pieces as a list of integers
        pieces_num = sorted([self.char_to_int(p) for p in state['pieces']])

        # state used by tensorforce
        state_formatted = heuristics
        state_formatted.extend(pieces_num)

        return state_formatted

    def format_score(self, state):
        id_self = self.my_id_in_game
        id_other = (id_self + 1) % 2
        score_self = state['score'][id_self]
        score_other = state['score'][id_other]

        return score_self, score_other

    @staticmethod
    def char_to_int(char):
        lu_table = {'O': 0, 'I': 1, 'L': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6}
        return lu_table[char]

    async def train(self):
        await super().init_train()
        if self.is_stats :
            self.my_stats = Stats.Stats()
            self.pid_stats = await self.my_stats.observe()

        for _ in range(self.nb_games):
            if self.is_stats :
                await super().new_game(players=[[self.my_client.pid, 1]],
                                       ias=[[self.train_adversary_level, 1]],
                                       viewers=[0, self.pid_stats])
            else :
                await super().new_game(players=[[self.my_client.pid, 1]],
                                       ias=[[self.train_adversary_level, 1]],
                                       viewers=[0])

            self.current_game_is_finish = False

            while not self.current_game_is_finish:
                await asyncio.sleep(0)

            self.current_game_is_finish = False

        self.save()

    def save(self):
        #TODO: Dire si on a bien charger
        # directory = os.path.join(os.getcwd(), 'rein_learn_models')
        time_str = time.strftime('%Y%m%d_%H%M%S')
        directory = os.path.join(os.getcwd(), 'rein_learn_models', 'agent_' + time_str)
        checkpoint = self.agent.save_model(directory=directory, append_timestep=True)
        print('directory: {}'.format(directory))
        print('checkpoint: {}'.format(checkpoint))

    def load(self, load_file):
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


    ia = Reinforcement('reinforcement', is_stats = my_stats, file_stats = args.my_file_stats)
    ia.nb_games = 1000
    AI_LOOP = asyncio.get_event_loop()
    try:
        AI_LOOP.run_until_complete(ia.train())
        print("fini")
    except KeyboardInterrupt:
        print("\nEntrainement arrêté manuellement.")
        ia.save()

    if my_stats :
        print("\n\n", ia.my_stats)
        f = open(ia.file_stats, 'w')
        f.write(str(ia.my_stats))
