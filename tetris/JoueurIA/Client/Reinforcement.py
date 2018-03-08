# coding: utf-8

import asyncio
from tensorforce.agents import DQNAgent

from Client import ClientInterface


class Reinforcement_IA(ClientInterface):
    def __init__(self, name, nb_rows, nb_cols, nb_pieces, file=None):
        super().__init__(name, file)

        self.current_game_is_finish = None
        self.first_game = True
        self.nb_games = 2
        self.score_self_old, self.score_self_new = 0, 0
        self.score_other_old, self.score_other_new = 0, 0
        self.scores_list = []
        self.file_scores = open('scores.txt', 'w')

        network_spec = [dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu'),
                        dict(type='dense', size=64, activation='relu')]

        nb_squares = nb_rows * nb_cols
        self.agent = DQNAgent(states_spec={'shape': (nb_squares+nb_pieces,), 'type': 'float'},
                              actions_spec={'hor_move': {'type': 'int', 'num_actions': 11},
                                            'rotate': {'type': 'int', 'num_actions': 4},
                                            'choose': {'type': 'int', 'num_actions': 3}},
                              network_spec=network_spec,
                              batch_size=64)

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

        print(action['rotate'])
        print(state['score'])
        print(self.my_client.ids_in_games)
        print(len(state_formatted))
        print(state['step'] == 'finished')
        print(action_to_apply)
        print({"hor_move": -2, "rotate": 1, "choose": state["pieces"][0]})
        print(state['step'])

        return action_to_apply
        #return {"hor_move": -2, "rotate": 1, "choose": state["pieces"][0]}

    def on_finished_game(self, data):
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
        self.file_scores.write("%d, %d\n" % (self.score_self_new, self.score_other_new))
        self.file_scores.flush()

    def update_scores(self, state):
        # update the old scores
        self.score_self_old, self.score_other_old = self.score_other_new, self.score_other_new

        # get the new scores
        self.score_self_new, self.score_other_new = self.format_score(state)

    def format_action(self, action, state):
        # convert int32 (which is not serializable) to standard int
        action_to_apply = {key: int(value) for key, value in
                           action.items()}

        action_to_apply['hor_move'] -= 5  # [0, 10] -> [-5, 5]
        action_to_apply['choose'] = state['pieces'][action_to_apply['choose']]  # index to letter

        return action_to_apply

    def format_state(self, state):
        # flattened and binary grid
        grid_flat = [int(j != 'White') for i in state['grid'] for j in i]

        # selectable pieces as a list of integers
        pieces_num = sorted([self.char_to_int(p) for p in state['pieces']])

        # state used by tensorforce
        state_formatted = grid_flat
        state_formatted.extend(pieces_num)

        return state_formatted

    def format_score(self, state):
        id_self = self.my_client.ids_in_games[state["gid"]][0]
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

        for _ in range(self.nb_games):
            await super().new_game(2)

            self.current_game_is_finish = False

            while not self.current_game_is_finish:
                await asyncio.sleep(0)

            self.current_game_is_finish = False

    def save(self):
        pass

    def load(self, file):
        pass


if __name__ == '__main__':
    ia = Reinforcement_IA('reinforcement', 22, 10, 3)
    ia.nb_games = 3000
    AI_LOOP = asyncio.get_event_loop()
    AI_LOOP.run_until_complete(ia.train())
