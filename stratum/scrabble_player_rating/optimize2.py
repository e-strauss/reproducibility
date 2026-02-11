import warnings
import sempipes
from utils import PlayerBasedFolds
from _sempipes_impl2 import sempipes_pipeline2
from sempipes.optimisers import optimise_colopro

warnings.filterwarnings("ignore")

sempipes.update_config(
    llm_for_code_generation=sempipes.LLM(
        name="gemini/gemini-2.5-flash",
        parameters={"temperature": 0.8},
    ),
)

pipeline = sempipes_pipeline2("data/train.csv")

outcomes = optimise_colopro(
    pipeline,
    "player_features",
    num_trials=10,
    scoring="neg_root_mean_squared_error",
    cv=PlayerBasedFolds(3),
    pipeline_definition=sempipes_pipeline2,
    run_name="optimize2"
)

best_outcome = max(outcomes, key=lambda x: x.score)
print(f"Lowest score: {-1 * best_outcome.score}\n\n")
final_code = "\n".join(best_outcome.state["generated_code"])
print(final_code)