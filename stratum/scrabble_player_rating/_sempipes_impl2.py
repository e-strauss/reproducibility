import warnings

import lightgbm as lgb
import pandas as pd
import stratum as skrub
from scipy.special import boxcox  # pylint: disable=no-name-in-module
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor

import sempipes  # pylint: disable=unused-import

warnings.filterwarnings("ignore")

nl_prompt="""
Create additional features that could help predict the rating of a player. The two players for a game can be found by checking the rows with the same game_id.

Definitely include the following:
    - the average time spent on each turn
    - the average points per second
    - a binary feature indicating whether the rating_mode is RATED or not
    - a binary feature indicating whether the game_end_reason is STANDARD or not
    - a binary feature indicating whether the time_control_name is regular or not
"""

def sempipes_pipeline2(data_file=None, n_choices=1):
    games = skrub.var("games", "data/games.csv").skb.apply_func(pd.read_csv)
    df_turns = skrub.var("turns", "data/turns.csv").skb.apply_func(pd.read_csv)
    data = skrub.var("data_file", data_file) if data_file else skrub.var("data_file")
    data = data.skb.apply_func(pd.read_csv)

    data = data.merge(games, on="game_id", how="inner")

    # adding a column with the len of the move
    def transform_move(tamanho):
        return len(str(tamanho))

    df_turns = df_turns.assign(len_move=df_turns["move"].map(transform_move))
    df_turns_agg1 = df_turns.groupby(["game_id", "nickname"], as_index=False).agg(
        {"turn_number": "count", "len_move": "mean"}
    )
    df_turns_agg2 = df_turns.groupby(["game_id", "nickname"], as_index=False).agg({"points": ["mean", "min", "max"]})
    df_turns_agg2 = df_turns_agg2["points"].rename(
        columns={"mean": "points_mean", "min": "points_min", "max": "points_max"}
    )
    df_turns_agg = df_turns_agg1.skb.concat([df_turns_agg2])

    data = data.merge(df_turns_agg, how="inner", on=["game_id", "nickname"])

    def add_other(X):
        # adding a column with the player's average points
        df_adiciona2 = X.groupby(["nickname"], as_index=False).agg({"score": "mean"})
        df_adiciona2 = df_adiciona2.rename(columns={"score": "mean_score"})
        X = X.merge(df_adiciona2, how="inner", on="nickname")

        X["Win"] = 0
        X["score_diff"] = 0
        X["other_mean_score"] = 0.0
        for i in range(0, len(X), 2):
            X["score_diff"][i] = X["score"][i] - X["score"][i + 1]
            X["score_diff"][i + 1] = X["score"][i + 1] - X["score"][i]

            X["other_mean_score"][i] = X["mean_score"][i + 1]
            X["other_mean_score"][i + 1] = X["mean_score"][i]
            if X["score_diff"][i] > 0:
                X["Win"][i] = 1
            else:
                X["Win"][i + 1] = 1

        # adding a column with the average points difference between the player and the opponent
        X["diff_mean_score"] = X["mean_score"] - X["other_mean_score"]

        # # adding a column of 1 if the player started the match and 0 if the opponent started
        X["first_num"] = 0
        for i in range(0, len(X), 2):
            if X["first"][i] == X["nickname"][i]:
                X["first_num"][i] = 1
                X["first_num"][i + 1] = 0
            else:
                X["first_num"][i] = 0
                X["first_num"][i + 1] = 1

        # adding a column with the initial_time_seconds and the duration of the game
        X["time_difference"] = X["initial_time_seconds"] - X["game_duration_seconds"]

        return X

    data = data.skb.apply_func(add_other)
    data = data[~data.nickname.str.endswith("Bot")]

    y = data["rating"].skb.mark_as_y().skb.apply_func(lambda y: boxcox(y, -1.4))
    X_d = data.drop(columns=["rating"]).skb.mark_as_X()

    Xvariaveis = [
        "score",
        "Win",
        "game_duration_seconds",
        "initial_time_seconds",
        "max_overtime_minutes",
        "first_num",
        "time_difference",
        "points_mean",
        "turn_number",
        "len_move",
        "score_diff",
        "mean_score",
        "other_mean_score",
        "diff_mean_score",
        "lexicon",
        "rating_mode",
        "time_control_name",
        "game_end_reason",
    ]
    X_d = X_d[Xvariaveis]
    if n_choices == 1:
        X_d = X_d.sem_gen_features(name="player_features", nl_prompt=nl_prompt, how_many=15)
    else:
        pipelines = {f"iter:{i}": X_d.sem_gen_features(name=f"player_features_{i}", nl_prompt="empty", how_many=15) for i in range(n_choices)}
        X_d = skrub.choose_from(pipelines, name="sempipes_iterations").as_data_op()

    X_d = X_d.skb.apply(skrub.TableVectorizer())
    X_d = X_d.fillna(-1)
    X_d = X_d.replace([float("inf"), -float("inf")], -1)
    model1 = ExtraTreesRegressor(random_state=42)
    model2a = lgb.LGBMRegressor(
        learning_rate=0.08797697229790209,
        num_leaves=12,
        min_child_samples=2,
        subsample=0.29682698086764914,
        colsample_bytree=0.2789636201075709,
        verbosity=-1,
        random_state=42,
    )
    predictions = X_d.skb.apply(model2a, y=y)
    # model2b = lgb.LGBMRegressor(random_state=42)
    model3 = RandomForestRegressor(random_state=42)

    model4a = GradientBoostingRegressor(learning_rate=0.01, n_estimators=100, max_depth=6, random_state=42)
    # model4b = GradientBoostingRegressor(random_state=42)

    pred1 = X_d.skb.apply(model1, y=y)
    pred2a = X_d.skb.apply(model2a, y=y)
    # pred2b = X_d.skb.apply(model2b, y=y)
    # pred2 = skrub.choose_from([pred2a, pred2b], name="lgbm_model").as_data_op()
    # pred2 = pred2a
    pred3 = X_d.skb.apply(model3, y=y)
    pred4a = X_d.skb.apply(model4a, y=y)
    # pred4b = X_d.skb.apply(model4b, y=y)
    # pred4 = skrub.choose_from([pred4a, pred4b], name="n_estm").as_data_op()
    ensemble_pred = pred1.skb.apply_func(lambda x1, x2, x3, x4, mode: (x1 + x2 + x3 + x4) / 4.0 if mode != "fit" else -1, x2=pred2a, x3=pred3, x4=pred4a, mode=skrub.eval_mode())
    # #predictions = skrub.choose_from({"ensemble": ensemble_pred, "lgbm": pred2b, "lgbm_special": pred2a}, name="ensemble_or_lgbm").as_data_op()
    predictions = ensemble_pred
    return predictions