from sklearn.model_selection import train_test_split
import numpy as np


BOT_NAMES = {"BetterBot", "HastyBot", "MasterBot", "STEEBot"}

def custom_splitter(all_data, y, random_state, test_size):  # pylint: disable=unused-argument
    all_players = all_data.nickname.unique()
    non_bot_players = [player for player in all_players if player not in BOT_NAMES]
    train_players, test_players = train_test_split(non_bot_players, test_size=test_size, random_state=random_state)
    train_game_ids = all_data[all_data.nickname.isin(train_players)].game_id.unique()
    test_game_ids = all_data[all_data.nickname.isin(test_players)].game_id.unique()

    train = all_data[all_data.game_id.isin(train_game_ids)]
    test = all_data[all_data.game_id.isin(test_game_ids)]

    return train, test, train.rating, test.rating


class PlayerBasedFolds:
    def __init__(self, n_splits=5):
        self.n_splits = n_splits

    def get_n_splits(self, X=None, y=None, groups=None):  # pylint: disable=unused-argument
        return self.n_splits

    def __str__(self):
        return f"player-based-{self.n_splits}"

    def split(self, X, y=None, groups=None):  # pylint: disable=unused-argument
        all_players = X.nickname.unique()
        non_bot_players = [player for player in all_players if player not in BOT_NAMES]

        # Partition non-bot players into n_splits folds
        player_folds = np.array_split(non_bot_players, self.n_splits)

        for k in range(self.n_splits):
            valid_players = player_folds[k]
            valid_player_game_ids = X[X.nickname.isin(valid_players)].game_id.unique()
            valid_idx = np.where(X.game_id.isin(valid_player_game_ids))[0]
            train_players = np.concatenate([player_folds[i] for i in range(self.n_splits) if i != k])
            train_player_game_ids = X[X.nickname.isin(train_players)].game_id.unique()
            train_idx = np.where(X.game_id.isin(train_player_game_ids))[0]

            yield train_idx, valid_idx

__all__ = ["BOT_NAMES", "custom_splitter"]