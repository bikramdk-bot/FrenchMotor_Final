# Example A Simulation And Risk Design

This note documents the current demos in this repository. It focuses on what the current code builds and renders today:

- Example A public demo: `reports/published/latest/example_a_public_demo/index.html`
- Example A public GUI: `reports/published/latest/example_a_public_demo/public.html`
- World-Switching Lab demo scenario: `examples/insurance_futures_studio/demo_world_switching_lab_20y.json`

The current demos are synthetic, artifact-first simulations built on a continuing insurance portfolio.

## Short Answer

Yes, portfolio risk changes through parameters.

The hidden world path chooses which world type is active for each year. Each world type has fixed stress parameters. Those world parameters are combined with the selected frequency model and severity model parameters to calculate:

- `frequency_rmse`: claim count model error
- `severity_rmse`: claim size model error
- `pure_premium_rmse`: combined pricing error, lower is better
- `net_strategic_value`: `100 - pure_premium_rmse * 100`

So if the user chooses the same model in Year 1 and Year 2, but the world path gives World Type 1 in Year 1 and World Type 5 in Year 2, the risk changes because the Year 2 checkpoint uses the World Type 5 parameters.

## Current Demo Pages

Example A publishes two pages:

| Page | Path | Purpose |
| --- | --- | --- |
| Admin lattice view | `reports/published/latest/example_a_public_demo/index.html` | Shows the lattice controls directly, including target world selection and chosen transitions. |
| Public GUI | `reports/published/latest/example_a_public_demo/public.html` | Hides the next world until recalculation finishes. The user chooses frequency and severity models only. |

The public GUI intentionally has fewer controls than the admin page. It hides the next world so the user experiences uncertainty, while the run remains reproducible from seed and version.

## Example A Scope

Example A is intentionally small:

- 5 world types
- 3 frequency model families
- 3 severity model families
- 10 yearly steps
- 1 locked retraining regime: `annual_locked`
- 450 reusable yearly checkpoints
- 18,225 reusable yearly transitions

The prototype demonstrates the storage rule used by the current demo: store reusable yearly checkpoints and yearly transitions, not duplicated full multi-year paths.

## Public Start Source

The public demo starts from the public French Motor third-party liability data family:

- `data/raw/freMTPL2freq.csv`
- `data/raw/freMTPL2sev.csv`

The base state is seeded from French motor data at training base year `-1`. Each simulated year is a synthetic layer on top of that start source. The worlds, Markov path, model choices, RMSE replay, benchmarks, and transition graph are product-demo simulation layers, not external market forecasts.

Raw public source data should not be redistributed from this repository. Published outputs must stay clearly marked as simulated or derived.

## Important Terms

| Term | Meaning |
| --- | --- |
| World type | The insurance environment applied to a year. It is hidden in the public GUI until recalculation finishes. |
| Model | The selected frequency and severity model families. They can be the same family or different families. |
| Retraining regime | The training cadence. In Example A it is locked to `annual_locked`. |
| Checkpoint | One yearly state keyed by year, world type, frequency model, severity model, retraining regime, seed, and version. |
| Transition | The edge from one yearly checkpoint to the next yearly checkpoint. |
| Risk metric | In Example A, "risk" means model/pricing error, mainly `pure_premium_rmse`. It is not actual claims cost, capital VaR, or solvency risk. |
| Artifact | CSV/JSON/HTML output used for playback, audit, ranking, and publishing. |

## Current Example A World Type Parameters

The five public world types are defined in `src/example_a_public_demo.py`.

| World Type | World Id | Label | Frequency Stress | Severity Stress | Volatility | Meaning |
| --- | --- | --- | ---: | ---: | ---: | --- |
| World Type 1 | `stable_baseline` | Stable Baseline | 0.16 | 0.16 | 0.08 | Mild drift and low stress. |
| World Type 2 | `good_years` | Good Years | 0.07 | 0.08 | 0.05 | Favorable environment with low claim frequency and severity. |
| World Type 3 | `mobility_suppression` | Mobility Suppression | 0.34 | 0.18 | 0.25 | Claim frequency changes unevenly as driving patterns shift. |
| World Type 4 | `pandemic_recovery_inflation` | Recovery Inflation | 0.32 | 0.45 | 0.22 | Recovery demand plus elevated repair inflation. |
| World Type 5 | `self_drive_revolution` | Self-Drive Revolution | 0.38 | 0.52 | 0.30 | Higher complexity, high severity pressure, and high volatility. |

World Type 5 is riskier than World Type 1 because all three stress inputs are higher.

## Current Example A Model Parameters

The same catalog is used for frequency and severity model choices.

| Model Family | Label | Base Error | Adaptation | Stability | Complexity Skill | Calm Generalization | Overfit Sensitivity | Meaning |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline_tariff` | Baseline Tariff | 0.34 | 0.10 | 0.90 | 0.04 | 0.18 | 0.04 | Stable reference model, slow to adapt. |
| `GLM` | GLM | 0.22 | 0.48 | 0.82 | 0.32 | 0.72 | 0.12 | Stable learner that performs well when good or stable years repeat. |
| `XGBoost` | XGBoost | 0.18 | 0.74 | 0.52 | 0.86 | 0.16 | 0.62 | Aggressive learner that shines in complex worlds but can overfit short calm history. |

If the user chooses "Model A" for both Year 1 and Year 2, the model parameters stay the same. The world parameters can still change because the hidden world path changes.

## Risk Formula

Example A now uses this training-window rule:

- Year 1: one prior-year training slice
- Year 2 onward: rolling 2-year training window

For each base yearly checkpoint:

```text
window_years = 1 if year == 1 else 2
window_factor = window_years / 2

frequency_credit =
  frequency_model.adaptation
  * (0.20 + window_factor * 0.18)

severity_credit =
  severity_model.adaptation
  * (0.18 + window_factor * 0.16)

frequency_rmse =
  frequency_model.base_error
  + world.frequency_stress * 0.32
  + world.volatility * 0.10
  - frequency_credit
  + rolling_window_adjustment
  + deterministic_noise

severity_rmse =
  severity_model.base_error
  + world.severity_stress * 0.34
  + world.volatility * 0.08
  - severity_credit
  + rolling_window_adjustment
  + deterministic_noise

pure_premium_rmse =
  frequency_rmse * 0.48 + severity_rmse * 0.52
```

Lower `pure_premium_rmse` is better. Higher `pure_premium_rmse` means higher pricing/model risk in this prototype. It is an error score for the selected checkpoint, not the claims cost paid in that year.

For Year 2 onward, the transition also applies a rolling-window game adjustment using the source world and target world:

- stable/good source-target pairs reward stability and calm generalization, so GLM can beat XGBoost there
- calm source-target pairs penalize overfit sensitivity, which mainly affects XGBoost
- large world shifts penalize models with weaker complexity skill
- complex target worlds reward complexity skill, which mainly helps XGBoost

That creates the intended game tradeoff: GLM is strong when stable or good years repeat, while XGBoost is strong when the world becomes volatile or nonlinear.

## Worked Example: Year 1 World Type 1, Year 2 World Type 5

Assume:

- Year 1 world is World Type 1: `stable_baseline`
- Year 2 world is World Type 5: `self_drive_revolution`
- The user keeps the same model family for both frequency and severity
- Seed is `20260513`
- Version is `example_a_v1`
- Retraining regime is `annual_locked`

| Same Model Family | Year 1 World Type 1 Pure Premium RMSE | Year 2 World Type 5 Pure Premium RMSE | Risk Change |
| --- | ---: | ---: | ---: |
| `baseline_tariff` | 0.379981 | 0.518058 | +0.138077 |
| `GLM` | 0.169373 | 0.261292 | +0.091919 |
| `XGBoost` | 0.076155 | 0.099561 | +0.023406 |

The stressful World Type 5 move still raises pressure, but XGBoost offsets most of that move because it has the highest complexity skill. GLM is designed to do better in stable/good sequences, not necessarily in sharp high-complexity jumps.

## Gamification Example: Stable Year To Good Year

The rolling 2-year window also creates a game effect when calm years repeat. For a Year 1 `stable_baseline` source moving into a Year 2 `good_years` target:

| Same Model Family | Year 2 Adjusted Pure Premium RMSE | Game Effect |
| --- | ---: | --- |
| `GLM` | 0.078954 | Stable/good rolling window favors simpler models and penalizes overfit. |
| `XGBoost` | 0.102707 | Short calm history creates an overfit penalty. |

This is intentional: GLM can be the stronger choice when the recent two-year training window is simple and stable.

The transition table stores the same comparison as `pure_premium_rmse_delta = source_rmse - target_rmse`.

- `source_rmse` means the `pure_premium_rmse` on the source checkpoint, which is the current yearly state before the transition. In this example, it is the Year 1 World Type 1 checkpoint.
- `target_rmse` means the `pure_premium_rmse` on the target checkpoint, which is the next yearly state after applying the target world type and selected models. In this example, it is the Year 2 World Type 5 checkpoint.

So `target_rmse` is not a separate claims cost number. It is the next year's model/pricing error under the next world type. If `target_rmse` is higher than `source_rmse`, the stored delta is negative and risk got worse. For this example the delta is negative, so the transition is not recommended:

| Same Model Family | Stored Transition Delta | Recommended |
| --- | ---: | --- |
| `baseline_tariff` | -0.138077 | `False` |
| `GLM` | -0.091919 | `False` |
| `XGBoost` | -0.023406 | `False` |

## Example A World Generation Method

The Example A public world path is generated by a seeded Markov-chain style rule. It is not manually picked year by year.

Each world type is a finite state. At a yearly boundary, the next world type is chosen from probabilities conditioned on the current world type. The current implementation uses a seeded autocorrelated path:

```text
Year 1:
  start at World Type 1

Later years:
  draw < 0.58  -> stay in current world type
  draw < 0.82  -> move forward one world type
  draw < 0.92  -> move backward one world type
  otherwise    -> jump forward two world types
```

The method is stochastic in design because the path comes from transition draws. It is cyclic: transitions wrap around the world catalog (e.g., Forward from World 5 leads to World 1). It is reproducible in the demo because the draws are keyed by seed and version.

## Example A Checkpoint And Transition Lattice

Example A stores the finite state graph:

- checkpoints: `10 years x 5 worlds x 3 frequency models x 3 severity models = 450`
- transitions: `9 boundaries x 45 source states x 45 target states = 18,225`
- full paths from one initial state: `756,680,642,578,125`, not materialized

The stored checkpoint key is:

```text
(year, world, frequency_model, severity_model, retraining, seed, version)
```

Each transition references:

- source checkpoint id
- target checkpoint id
- source and target world type
- source and target frequency model
- source and target severity model
- `pure_premium_rmse_delta`
- `recommended`

## Current Example A Artifacts

The Example A public prototype publishes:

- `index.html`
- `public.html`
- `demo_manifest.json`
- `run_summary.json`
- `session_event_log_schema.json`
- `yearly_checkpoints.csv`
- `yearly_transitions.csv`

The renderer script is:

```text
scripts/build_example_a_public_demo_dashboard.py
```

The full artifact and HTML runner is:

```text
pipelines/run_example_a_public_demo.py
```

## Current World-Switching Lab Demo

The current World-Switching Lab demo is a separate 20-year artifact replay. Its scenario file is:

```text
examples/insurance_futures_studio/demo_world_switching_lab_20y.json
```

The scenario uses seed `20260512`, starts in `stable_baseline`, and applies these world switches:

| Year | Target World | Transition Type | Duration | Description |
| ---: | --- | --- | ---: | --- |
| 5 | `mobility_suppression` | `phase_based` | 24 months | Pandemic and work-from-home suppression begins without resetting the portfolio. |
| 10 | `pandemic_recovery_inflation` | `smooth_ramp` | 12 months | Recovery begins while the same portfolio carries forward into persistent inflation. |
| 13 | `autonomous_transition` | `smooth_ramp` | 24 months | Autonomous and assisted-driving adoption gradually reshapes the continuing portfolio. |
| 17 | `severity_inflation` | `abrupt` | 1 month | Repair inflation spikes abruptly while cumulative portfolio history remains intact. |

This demo uses a scenario switch plan, not the Example A hidden public Markov path.

## Current World-Switching Lab World Catalog

The current engine defines these eight world regimes in `src/world_switching_lab.py`:

| World Id | Label | Main Idea |
| --- | --- | --- |
| `stable_baseline` | Stable Baseline | Mild drift, mild inflation, and low randomness. |
| `mobility_suppression` | Mobility Suppression | Pandemic and work-from-home regime with exposure suppression and repair pressure. |
| `pandemic_recovery_inflation` | Pandemic Recovery Inflation | Post-pandemic inflation with elevated repair cost pressure. |
| `autonomous_transition` | Autonomous Transition | Assisted-driving adoption lowers frequency while increasing repair severity. |
| `nonlinear_interaction` | Nonlinear Interaction | Cross-feature interaction effects dominate simple linear trends. |
| `frequency_drift` | Frequency Drift | Persistent structural movement in claim frequency. |
| `severity_inflation` | Severity Inflation | Repair and claim severity inflate faster than historic expectation. |
| `hidden_segment` | Hidden Segment | Latent segment behavior changes measured performance. |

## Current World-Switching Lab Strategies

The current strategy matrix is `config/insurance_futures_studio/default_strategy_matrix.yaml`.

| Strategy Name | Model | Retraining | Window |
| --- | --- | --- | --- |
| `baseline_tariff_never_static_low` | `baseline_tariff` | `never` | expanding |
| `glm_annual_expanding_conservative` | `GLM` | `annual` | expanding |
| `glm_quarterly_rolling5_balanced` | `GLM` | `quarterly` | rolling 5 years |
| `xgboost_annual_expanding_balanced` | `XGBoost` | `annual` | expanding |
| `xgboost_quarterly_rolling5_agile` | `XGBoost` | `quarterly` | rolling 5 years |
| `xgboost_monthly_rolling2_agile` | `XGBoost` | `monthly` | rolling 2 years |
| `xgboost_trigger_rolling3_agile` | `XGBoost` | `trigger_based` | rolling 3 years |

The current World-Switching Lab output bundle includes:

- `run_summary.json`
- `metrics_by_year.csv`
- `metrics_by_period.csv`
- `retraining_events.csv`
- `costs_by_year.csv`
- `winner_by_year.csv`
- `robustness_summary.json`
- `portfolio_state.csv`
- `switch_history.csv`

## Current Repository Paths

| Path | Purpose |
| --- | --- |
| `src/example_a_public_demo.py` | Example A lattice engine. |
| `src/example_a_public_demo_dashboard.py` | Example A admin/public HTML renderer. |
| `pipelines/run_example_a_public_demo.py` | Builds Example A artifacts and HTML. |
| `scripts/build_example_a_public_demo_dashboard.py` | Renders Example A HTML from existing artifacts. |
| `src/world_switching_lab.py` | Current World-Switching Lab simulation engine. |
| `src/world_switching_lab_dashboard.py` | Current World-Switching Lab dashboard renderer. |
| `pipelines/run_world_switching_lab.py` | Runs the current World-Switching Lab scenario bundle. |
| `scripts/build_world_switching_lab_dashboard.py` | Rebuilds the current World-Switching Lab dashboard from artifacts. |

## One-Sentence Explanation

If the user keeps Model A in both years but the hidden Markov-chain world path changes from World Type 1 (`stable_baseline`) to World Type 5 (`self_drive_revolution`), portfolio risk changes because the second year uses World Type 5's higher `frequency_stress`, `severity_stress`, and `volatility` parameters, while the model parameters stay fixed.

## Bottom Line

The current demos are finite, artifact-first simulations over a continuing portfolio.

- Example A uses a seeded Markov-chain style hidden world path.
- The World-Switching Lab 20-year demo uses a fixed scenario switch plan.
- Worlds define regime physics.
- Models define prediction behavior.
- The portfolio does not reset when the world changes.
- The demos store reusable checkpoints, transitions, and published artifacts instead of full duplicated paths.
