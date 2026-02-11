import logging
from sklearn.model_selection import ShuffleSplit
from utils import PlayerBasedFolds
from sempipes.optimisers.trajectory import load_trajectory_from_json
from _sempipes_impl2 import sempipes_pipeline2
logging.basicConfig(level=logging.DEBUG)
import stratum as st
from time import perf_counter
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="stratum")
parser.add_argument("--cv", type=int, default=3)
args = parser.parse_args()


trajectory = load_trajectory_from_json(".sempipes_trajectories/optimize2_20260209_221644_13679bf2.json")

outcomes_by_trial = sorted(trajectory.outcomes, key=lambda x: (x.search_node.trial))

states = [outcomes_by_trial[i].state for i in range(10)]

pipeline_batch1 = sempipes_pipeline2(n_choices=5)
pipeline_batch1.skb.draw_graph().open()
pipeline_batch2 = sempipes_pipeline2(n_choices=4)
pipeline_single = sempipes_pipeline2(n_choices=1)

pipeline_env1 = pipeline_batch1.skb.get_data()
pipeline_env2 = pipeline_batch2.skb.get_data()
pipeline_env_single = pipeline_single.skb.get_data()

env1 = {f"sempipes_prefitted_state__player_features_{i}": states[i] for i in range(5)}
env2 = {f"sempipes_prefitted_state__player_features_{i-5}": states[i] for i in range(5, 9)}
pipeline_env1.update(env1)
pipeline_env2.update(env2)
pipeline_env1["data_file"] = "data/train.csv"
pipeline_env2["data_file"] = "data/train.csv"
pipeline_env_single["data_file"] = "data/train.csv"

cv = ShuffleSplit(n_splits=1,test_size=0.4,random_state=42) if args.cv == 1 else PlayerBasedFolds(args.cv)

t0 = perf_counter()

def search_skrub():
    search1 = pipeline_batch1.skb.make_grid_search(cv=cv, fitted=False, scoring="neg_root_mean_squared_error")
    search2 = pipeline_batch2.skb.make_grid_search(cv=cv, fitted=False, scoring="neg_root_mean_squared_error")
    search1.fit(pipeline_env1)
    search2.fit(pipeline_env2)

def search_stratum():
    with st.config(scheduler=True, stats=30):
        search1 = pipeline_batch1.skb.make_grid_search(cv=cv, fitted=True, environment=pipeline_env1, scoring="neg_root_mean_squared_error")
        search2 = pipeline_batch2.skb.make_grid_search(cv=cv, fitted=True, environment=pipeline_env2, scoring="neg_root_mean_squared_error")

def search_base():
    for i in range(9):
        env = pipeline_env_single.copy()
        env[f"sempipes_prefitted_state__player_features"] = states[i]
        search_single = pipeline_single.skb.make_grid_search(cv=cv, fitted=False, scoring="neg_root_mean_squared_error")
        search_single.fit(env)

if args.mode == "skrub":
    search_skrub()
elif args.mode == "stratum":
    search_stratum()
elif args.mode == "base":
    search_base()
elif args.mode == "all":
    t0 = perf_counter()
    search_skrub()
    t1 = perf_counter()
    print(f"Time taken for skrub: {t1 - t0} seconds")
    search_stratum()
    t2 = perf_counter()
    print(f"Time taken for stratum: {t2 - t1} seconds")
    search_base()
    t3 = perf_counter()
    print(f"Time taken for base: {t3 - t2} seconds")
else:
    raise ValueError(f"Invalid mode: {args.mode}")
t1 = perf_counter()

print(f"Time taken: {t1 - t0} seconds")
