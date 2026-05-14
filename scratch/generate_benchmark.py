import pandas as pd
import numpy as np
import json
from pathlib import Path

# Load data
base_path = Path("reports/published/latest/example_a_public_demo")
checkpoints = pd.read_csv(base_path / "yearly_checkpoints.csv")
transitions = pd.read_csv(base_path / "yearly_transitions.csv")

# Create a mapping for easy lookup
# (year, world_id, freq_model, sev_model) -> rmse
ckpt_map = {}
for _, row in checkpoints.iterrows():
    ckpt_map[(row['year'], row['world_id'], row['frequency_model_family'], row['severity_model_family'])] = row['pure_premium_rmse']

# (boundary_year, source_world_id, target_world_id) -> list of possible transitions
trans_map = {}
for _, row in transitions.iterrows():
    key = (row['boundary_year'], row['source_world_id'], row['target_world_id'])
    if key not in trans_map:
        trans_map[key] = []
    trans_map[key].append(row)

worlds = checkpoints['world_id'].unique()
models = checkpoints['frequency_model_family'].unique()

def simulate_expert_path(seed):
    rng = np.random.default_rng(seed)
    
    # 1. Generate a world path (simulated hidden path)
    world_path = ["stable_baseline"]
    world_order = ["stable_baseline", "good_years", "mobility_suppression", "pandemic_recovery_inflation", "self_drive_revolution"]
    current_idx = 0
    for year in range(1, 10):
        draw = rng.random()
        if draw < 0.58:
            pass # stay
        elif draw < 0.82:
            current_idx = min(current_idx + 1, len(world_order) - 1)
        elif draw < 0.92:
            current_idx = max(current_idx - 1, 0)
        else:
            current_idx = min(current_idx + 2, len(world_order) - 1)
        world_path.append(world_order[current_idx])
    
    # 2. Simulate expert model choices
    total_rmse = 0
    current_freq = rng.choice(models)
    current_sev = rng.choice(models)
    
    for year in range(1, 11):
        world = world_path[year-1]
        
        # Expert choice: pick a model that likely works well for this world
        # We'll just pick randomly among GLM and XGBoost (experts don't use Baseline Tariff usually)
        expert_models = ["GLM", "XGBoost"]
        current_freq = rng.choice(expert_models)
        current_sev = rng.choice(expert_models)
        
        rmse = ckpt_map[(year, world, current_freq, current_sev)]
        total_rmse += rmse
        
    return total_rmse

# Generate 100 expert tries
expert_tries = []
for i in range(100):
    expert_tries.append(simulate_expert_path(20260513 + i))

expert_tries.sort()
# Round to 3 decimal places
expert_tries = [round(x, 3) for x in expert_tries]

print(json.dumps(expert_tries))
