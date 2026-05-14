# French Motor MTPL Risk Simulator

An interactive simulation platform designed to test actuarial model resilience under uncertainty. The simulator uses the public French Motor Third-Party Liability (MTPL) dataset as a foundation to create a 10-year insurance future lattice.

## Objective
**Can you manage MTPL risk under uncertainty?**
As an actuary, you must choose between different frequency and severity model families (GLM, XGBoost, etc.) to minimize the **Pure Premium RMSE** as the underlying insurance "world" shifts around you.

## Live Demo (Example A)
The simulator is built as a static, self-contained HTML/JS bundle that can be hosted on GitHub Pages or Netlify.

- **[Public Simulator (index.html)](reports/published/latest/example_a_public_demo/index.html)**: The main interactive experience. Hides the "next world" until the year is advanced, forcing decisions under uncertainty.
- **[Admin View (admin.html)](reports/published/latest/example_a_public_demo/admin.html)**: A full transparency view of the underlying transition lattice and precomputed checkpoints.
- **[Detailed Assumptions (info.html)](reports/published/latest/example_a_public_demo/info.html)**: Documentation of the risk physics, model credits, and world transition probabilities.

## Risk Physics & Mechanics
- **Established Portfolio**: No maturity ramp-up; models operate at full potential from Year 1.
- **2-Year Rolling Window**: Models are retrained using the most recent 2 years of history (where available), rewarding models that adapt quickly to regime shifts.
- **Cyclic World Loop**: The simulation features a continuous Markov-chain world path (W1-W5-W1) with no artificial boundaries.
- **Pure Premium RMSE**: Performance is measured by the pricing error relative to the true world state.

## Core Components
- **Lattice Engine**: `src/example_a_public_demo.py` manages the stochastic path generation and RMSE calculations.
- **Dashboard Renderer**: `src/example_a_public_demo_dashboard.py` generates the premium glassmorphism UI.
- **Artifacts**: All simulation data is stored in `reports/published/latest/example_a_public_demo/` as CSV and JSON lattices.

## How to Run

### 1. Build Artifacts
Generate the underlying simulation lattice (checkpoints and transitions):
```bash
python scripts/build_example_a_public_demo_dashboard.py --regenerate-artifacts
```

### 2. Update Dashboard UI
Refresh the HTML files without regenerating the underlying simulation data:
```bash
python scripts/build_example_a_public_demo_dashboard.py
```

### 3. Run Tests
```bash
python -m unittest tests/test_example_a_public_demo.py
```

## Data Policy
This project utilizes the public French Motor Third-Party Liability dataset (`freMTPL2freq.csv` and `freMTPL2sev.csv`). 
- **Simulated Layers**: All yearly paths, world shifts, and model benchmarks are synthetic simulation layers designed for demonstration purposes.
- **Redistribution**: Original raw source data should be kept in `data/raw/` and not redistributed. Published outputs are clearly marked as derived/simulated.

## Design Philosophy
This project demonstrates the principle of **artifact-first simulation**: storing reusable yearly nodes and edges in a finite lattice rather than generating open-ended trajectories. This allows for instant "replay" and auditability of any possible insurance future within the defined parameters.
