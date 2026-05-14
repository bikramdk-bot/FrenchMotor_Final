# Future Plans

This file is for ideas that are not part of the current published demos.

## Competitor Mode

Introduce simulated competitors into the public game so the player is not only trying to minimize RMSE, but also competing against market actors with different objectives.

## Competitor Types

| Competitor | Strategy Style | Objective |
| --- | --- | --- |
| Conservative Tariff | Slow price movement, low model risk, low operating cost. | Preserve margin and avoid bad surprises. |
| Stable GLM | Uses transparent GLM pricing and avoids overreacting to short noisy history. | Win stable and good-year markets. |
| Aggressive XGBoost | Reacts quickly to nonlinear stress and volatile worlds. | Win complex regimes before slower competitors adapt. |
| Discount Growth | Prices aggressively below technical premium. | Gain market share, even with margin risk. |
| Profit Defender | Raises prices quickly when severity or volatility rises. | Protect underwriting margin. |

## Competitor Objectives

Each competitor can optimize a different score:

- lowest pure premium RMSE
- highest underwriting margin
- highest market share
- best retention
- lowest volatility
- lowest retraining and governance cost
- best combined strategic score

## Game Effects

Competitors can create additional gameplay pressure:

- price pressure when a competitor undercuts the player
- retention loss when the player is too expensive
- margin loss when the player is too cheap
- market-share shifts after each yearly recalculation
- competitor adaptation lag after world changes
- competitor overreaction during short volatile periods

## Suggested State

Add competitor state per year:

```text
competitor_id
competitor_strategy
target_world
price_index
technical_premium_index
market_share
retention_rate
margin_index
model_error
adaptation_lag
objective_score
```

## Suggested Player Score

The public game score can combine:

```text
player_score =
  prediction_score
  + margin_score
  + retention_score
  + market_share_score
  - volatility_penalty
  - retraining_cost_penalty
```

## First Implementation Slice

Start with three competitors:

- Conservative Tariff
- Stable GLM
- Aggressive XGBoost

Then add one market-share panel to `public.html`:

- player market share
- best competitor
- yearly share change
- margin warning

Keep competitor mode synthetic and deterministic from seed/version, the same way the current world path is reproducible.
