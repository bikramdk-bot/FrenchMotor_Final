from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_SEED = 20260513
DEFAULT_VERSION = "example_a_v1"
DEFAULT_RETRAINING = "annual_locked"
DEFAULT_YEARS = 10
FRENCH_MOTOR_SOURCE_FILES = ("data/raw/freMTPL2freq.csv", "data/raw/freMTPL2sev.csv")
TRAINING_BASE_NOTE = "Base year -1 uses French motor data; Year 1 trains on one prior-year slice, then Year 2 onward uses a rolling 2-year window."


@dataclass(frozen=True)
class DemoWorld:
    world_id: str
    label: str
    frequency_stress: float
    severity_stress: float
    volatility: float
    narrative: str


@dataclass(frozen=True)
class DemoModel:
    model_family: str
    label: str
    base_error: float
    adaptation: float
    stability: float
    complexity_skill: float
    calm_generalization: float
    overfit_sensitivity: float
    narrative: str
    model_info: str


WORLD_CATALOG: tuple[DemoWorld, ...] = (
    DemoWorld(
        world_id="stable_baseline",
        label="Stable Baseline",
        frequency_stress=0.16,
        severity_stress=0.16,
        volatility=0.08,
        narrative="Mild drift and low stress keep the portfolio close to historic behavior.",
    ),
    DemoWorld(
        world_id="good_years",
        label="Good Years",
        frequency_stress=0.07,
        severity_stress=0.08,
        volatility=0.05,
        narrative="Frequency and severity are both low, creating a favorable underwriting environment.",
    ),
    DemoWorld(
        world_id="mobility_suppression",
        label="Mobility Suppression",
        frequency_stress=0.34,
        severity_stress=0.18,
        volatility=0.25,
        narrative="Frequency changes unevenly as driving patterns shift, while severity pressure stays moderate.",
    ),
    DemoWorld(
        world_id="pandemic_recovery_inflation",
        label="Recovery Inflation",
        frequency_stress=0.32,
        severity_stress=0.45,
        volatility=0.22,
        narrative="Recovery demand returns while repair inflation and claim severity remain elevated.",
    ),
    DemoWorld(
        world_id="self_drive_revolution",
        label="Self-Drive Revolution",
        frequency_stress=0.38,
        severity_stress=0.52,
        volatility=0.30,
        narrative="Frequency changes unevenly as automated driving adoption spreads, while higher repair complexity lifts severity.",
    ),
)


MODEL_CATALOG: tuple[DemoModel, ...] = (
    DemoModel(
        model_family="baseline_tariff",
        label="Baseline Tariff",
        base_error=0.34,
        adaptation=0.10,
        stability=0.90,
        complexity_skill=0.04,
        calm_generalization=0.18,
        overfit_sensitivity=0.04,
        narrative="Stable reference model that is slow to adapt when the world changes.",
        model_info="A fixed tariff benchmark. It uses pre-set rating relativities and updates slowly, so it is useful as a stable baseline rather than an adaptive learner.",
    ),
    DemoModel(
        model_family="GLM",
        label="GLM",
        base_error=0.22,
        adaptation=0.48,
        stability=0.82,
        complexity_skill=0.32,
        calm_generalization=0.72,
        overfit_sensitivity=0.12,
        narrative="Stable learner that performs well when good or stable years repeat in the rolling window.",
        model_info="A generalized linear model. It learns transparent frequency and severity relationships from the rolling 2-year window, generalizes well in stable/good years, and is less prone to overfitting short calm history.",
    ),
    DemoModel(
        model_family="XGBoost",
        label="XGBoost",
        base_error=0.18,
        adaptation=0.74,
        stability=0.52,
        complexity_skill=0.86,
        calm_generalization=0.16,
        overfit_sensitivity=0.62,
        narrative="Aggressive learner that shines in volatile or complex worlds but can overfit short calm history.",
        model_info="A gradient-boosted tree model. It captures nonlinear frequency and severity patterns in complex worlds, but the short rolling 2-year window can overfit when stable or good years repeat.",
    ),
)

PUBLIC_WORLD_ORDER: tuple[str, ...] = (
    "stable_baseline",
    "good_years",
    "mobility_suppression",
    "pandemic_recovery_inflation",
    "self_drive_revolution",
)


def _world_lookup() -> dict[str, DemoWorld]:
    return {world.world_id: world for world in WORLD_CATALOG}


def _model_lookup() -> dict[str, DemoModel]:
    return {model.model_family: model for model in MODEL_CATALOG}


def _source_lineage() -> dict[str, Any]:
    return {
        "source_name": "French Motor third-party liability raw data",
        "source_files": list(FRENCH_MOTOR_SOURCE_FILES),
        "root_year": 0,
        "root_checkpoint_id": "root_y0_french_motor_public_demo",
        "root_checkpoint_label": "French Motor Root",
        "root_checkpoint_note": "Observed French Motor calibration layer used as the reproducibility root for the public demo.",
    }


def _stable_noise(seed: int, *parts: Any, amplitude: float = 0.01) -> float:
    text = "|".join([str(seed), *[str(part) for part in parts]])
    value = 0
    for character in text:
        value = (value * 131 + ord(character)) % 1_000_003
    normalized = (value / 1_000_003.0) * 2.0 - 1.0
    return normalized * amplitude


def _stable_unit(seed: int, *parts: Any) -> float:
    return (_stable_noise(seed, *parts, amplitude=0.5) + 0.5)


def _training_window_years(year: int) -> int:
    return 1 if year <= 1 else 2


def _training_window_bounds(year: int) -> tuple[int, int]:
    end_year = year - 1
    window_years = _training_window_years(year)
    return end_year - window_years + 1, end_year


def _training_window_label(year: int) -> str:
    return "1-year initial window" if _training_window_years(year) == 1 else "rolling 2-year window"


def _world_complexity(world: DemoWorld) -> float:
    return (world.frequency_stress * 0.34) + (world.severity_stress * 0.42) + (world.volatility * 0.24)


def _is_calm_world(world: DemoWorld) -> bool:
    return world.world_id in {"stable_baseline", "good_years"}


def _sequence_adjustment(source_world: DemoWorld | None, target_world: DemoWorld, model: DemoModel, target_year: int) -> float:
    if source_world is None or target_year <= 1:
        return 0.0

    source_complexity = _world_complexity(source_world)
    target_complexity = _world_complexity(target_world)
    stress_shift = abs(source_world.frequency_stress - target_world.frequency_stress)
    stress_shift += abs(source_world.severity_stress - target_world.severity_stress)
    stress_shift += abs(source_world.volatility - target_world.volatility)

    same_world = source_world.world_id == target_world.world_id
    calm_pair = _is_calm_world(source_world) and _is_calm_world(target_world)
    average_complexity = (source_complexity + target_complexity) / 2.0

    stable_window_bonus = 0.0
    if calm_pair:
        stable_window_bonus = (model.stability * 0.025) + (model.calm_generalization * 0.050)
    elif same_world:
        stable_window_bonus = model.stability * 0.018

    calm_overfit_penalty = 0.0
    if calm_pair:
        calm_overfit_penalty = model.overfit_sensitivity * 0.240
    elif average_complexity < 0.18:
        calm_overfit_penalty = model.overfit_sensitivity * (0.18 - average_complexity) * 0.22

    shock_penalty = stress_shift * (1.0 - model.complexity_skill) * 0.045
    complexity_bonus = max(0.0, target_complexity - 0.20) * model.complexity_skill * 0.10

    return calm_overfit_penalty + shock_penalty - stable_window_bonus - complexity_bonus


def _score_rmse(
    *,
    year: int,
    world: DemoWorld,
    frequency_model: DemoModel,
    severity_model: DemoModel,
    seed: int,
    version: str,
    source_world: DemoWorld | None = None,
) -> dict[str, Any]:
    window_years = _training_window_years(year)
    start_year, end_year = _training_window_bounds(year)
    window_factor = window_years / 2.0
    frequency_credit = frequency_model.adaptation * (0.20 + (window_factor * 0.18))
    severity_credit = severity_model.adaptation * (0.18 + (window_factor * 0.16))
    frequency_noise = _stable_noise(seed, year, world.world_id, frequency_model.model_family, "frequency", version, amplitude=0.008)
    severity_noise = _stable_noise(seed, year, world.world_id, severity_model.model_family, "severity", version, amplitude=0.008)
    frequency_adjustment = _sequence_adjustment(source_world, world, frequency_model, year)
    severity_adjustment = _sequence_adjustment(source_world, world, severity_model, year)
    frequency_rmse = max(
        0.02,
        frequency_model.base_error
        + (world.frequency_stress * 0.32)
        + (world.volatility * 0.10)
        - frequency_credit
        + frequency_adjustment
        + frequency_noise,
    )
    severity_rmse = max(
        0.02,
        severity_model.base_error
        + (world.severity_stress * 0.34)
        + (world.volatility * 0.08)
        - severity_credit
        + severity_adjustment
        + severity_noise,
    )
    rmse = (frequency_rmse * 0.48) + (severity_rmse * 0.52)
    net_value = 100.0 - (rmse * 100.0)
    if source_world is None or year <= 1:
        game_effect_summary = "Initial 1-year training window."
    elif _is_calm_world(source_world) and _is_calm_world(world):
        game_effect_summary = "Stable/good rolling window favors simpler models and penalizes overfit."
    elif source_world.world_id == world.world_id:
        game_effect_summary = "Repeated world gives stable learners a small consistency benefit."
    else:
        game_effect_summary = "World shift rewards adaptive models but penalizes poor generalization."
    return {
        "training_window_years": window_years,
        "training_window_label": _training_window_label(year),
        "training_data_start_year": start_year,
        "training_data_end_year": end_year,
        "frequency_rmse": round(frequency_rmse, 6),
        "severity_rmse": round(severity_rmse, 6),
        "pure_premium_rmse": round(rmse, 6),
        "net_strategic_value": round(net_value, 6),
        "game_effect_summary": game_effect_summary,
    }


def generate_public_world_path(years: int = DEFAULT_YEARS, seed: int = DEFAULT_SEED) -> list[str]:
    path: list[str] = []
    index = 0
    for year in range(1, years + 1):
        if year == 1:
            index = 0
        else:
            draw = _stable_unit(seed, "public_world_path", year, path[-1])
            if draw < 0.58:
                index = index
            elif draw < 0.82:
                index = (index + 1) % len(PUBLIC_WORLD_ORDER)
            elif draw < 0.92:
                index = (index - 1) % len(PUBLIC_WORLD_ORDER)
            else:
                index = (index + 2) % len(PUBLIC_WORLD_ORDER)
        path.append(PUBLIC_WORLD_ORDER[index])
    return path


def checkpoint_id(
    year: int,
    world_id: str,
    frequency_model_family: str,
    severity_model_family: str,
    seed: int,
    version: str = DEFAULT_VERSION,
) -> str:
    return f"chk_y{year}_{world_id}_freq_{frequency_model_family}_sev_{severity_model_family}_{DEFAULT_RETRAINING}_s{seed}_{version}"


def transition_id(
    year: int,
    source_world_id: str,
    source_frequency_model_family: str,
    source_severity_model_family: str,
    target_world_id: str,
    target_frequency_model_family: str,
    target_severity_model_family: str,
    seed: int,
    version: str = DEFAULT_VERSION,
) -> str:
    return (
        f"tr_y{year}_"
        f"{source_world_id}_freq_{source_frequency_model_family}_sev_{source_severity_model_family}_to_"
        f"{target_world_id}_freq_{target_frequency_model_family}_sev_{target_severity_model_family}_s{seed}_{version}"
    )


def build_yearly_checkpoints(
    *,
    years: int = DEFAULT_YEARS,
    seed: int = DEFAULT_SEED,
    version: str = DEFAULT_VERSION,
) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for year in range(1, years + 1):
        for world in WORLD_CATALOG:
            for frequency_model in MODEL_CATALOG:
                for severity_model in MODEL_CATALOG:
                    score = _score_rmse(
                        year=year,
                        world=world,
                        frequency_model=frequency_model,
                        severity_model=severity_model,
                        seed=seed,
                        version=version,
                    )
                    checkpoints.append(
                        {
                            "checkpoint_id": checkpoint_id(
                                year,
                                world.world_id,
                                frequency_model.model_family,
                                severity_model.model_family,
                                seed,
                                version,
                            ),
                            "year": year,
                            "world_id": world.world_id,
                            "world_label": world.label,
                            "frequency_model_family": frequency_model.model_family,
                            "frequency_model_label": frequency_model.label,
                            "severity_model_family": severity_model.model_family,
                            "severity_model_label": severity_model.label,
                            "retraining_regime": DEFAULT_RETRAINING,
                            "seed": seed,
                            "version": version,
                            "training_window_years": score["training_window_years"],
                            "training_window_label": score["training_window_label"],
                            "training_data_start_year": score["training_data_start_year"],
                            "training_data_end_year": score["training_data_end_year"],
                            "frequency_rmse": score["frequency_rmse"],
                            "severity_rmse": score["severity_rmse"],
                            "pure_premium_rmse": score["pure_premium_rmse"],
                            "net_strategic_value": score["net_strategic_value"],
                            "game_effect_summary": score["game_effect_summary"],
                            "world_narrative": world.narrative,
                            "frequency_model_narrative": frequency_model.narrative,
                            "severity_model_narrative": severity_model.narrative,
                        }
                    )
    return checkpoints


def build_yearly_transitions(
    *,
    checkpoints: list[dict[str, Any]],
    years: int = DEFAULT_YEARS,
    seed: int = DEFAULT_SEED,
    version: str = DEFAULT_VERSION,
) -> list[dict[str, Any]]:
    by_key = {
        (int(row["year"]), str(row["world_id"]), str(row["frequency_model_family"]), str(row["severity_model_family"])): row
        for row in checkpoints
    }
    transitions: list[dict[str, Any]] = []
    for year in range(1, years):
        for source_world in WORLD_CATALOG:
            for source_frequency_model in MODEL_CATALOG:
                for source_severity_model in MODEL_CATALOG:
                    source = by_key[(year, source_world.world_id, source_frequency_model.model_family, source_severity_model.model_family)]
                    for target_world in WORLD_CATALOG:
                        for target_frequency_model in MODEL_CATALOG:
                            for target_severity_model in MODEL_CATALOG:
                                target = by_key[(year + 1, target_world.world_id, target_frequency_model.model_family, target_severity_model.model_family)]
                                world_switch = source_world.world_id != target_world.world_id
                                frequency_model_switch = source_frequency_model.model_family != target_frequency_model.model_family
                                severity_model_switch = source_severity_model.model_family != target_severity_model.model_family
                                target_score = _score_rmse(
                                    year=year + 1,
                                    world=target_world,
                                    frequency_model=target_frequency_model,
                                    severity_model=target_severity_model,
                                    seed=seed,
                                    version=version,
                                    source_world=source_world,
                                )
                                value_delta = float(source["pure_premium_rmse"]) - float(target_score["pure_premium_rmse"])
                                transitions.append(
                                    {
                                        "transition_id": transition_id(
                                            year,
                                            source_world.world_id,
                                            source_frequency_model.model_family,
                                            source_severity_model.model_family,
                                            target_world.world_id,
                                            target_frequency_model.model_family,
                                            target_severity_model.model_family,
                                            seed,
                                            version,
                                        ),
                                        "from_checkpoint_id": source["checkpoint_id"],
                                        "to_checkpoint_id": target["checkpoint_id"],
                                        "boundary_year": year,
                                        "target_year": year + 1,
                                        "source_world_id": source_world.world_id,
                                        "target_world_id": target_world.world_id,
                                        "source_frequency_model_family": source_frequency_model.model_family,
                                        "target_frequency_model_family": target_frequency_model.model_family,
                                        "source_severity_model_family": source_severity_model.model_family,
                                        "target_severity_model_family": target_severity_model.model_family,
                                        "world_action": "switch" if world_switch else "stay",
                                        "frequency_model_action": "switch" if frequency_model_switch else "stay",
                                        "severity_model_action": "switch" if severity_model_switch else "stay",
                                        "pure_premium_rmse_delta": round(value_delta, 6),
                                        "target_training_window_years": target_score["training_window_years"],
                                        "target_training_window_label": target_score["training_window_label"],
                                        "target_training_data_start_year": target_score["training_data_start_year"],
                                        "target_training_data_end_year": target_score["training_data_end_year"],
                                        "target_frequency_rmse": target_score["frequency_rmse"],
                                        "target_severity_rmse": target_score["severity_rmse"],
                                        "target_pure_premium_rmse": target_score["pure_premium_rmse"],
                                        "target_net_strategic_value": target_score["net_strategic_value"],
                                        "game_effect_summary": target_score["game_effect_summary"],
                                        "recommended": bool(value_delta >= 0),
                                    }
                                )
    return transitions


def _checkpoint_index(checkpoints: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["checkpoint_id"]): row for row in checkpoints}


def _transition_index(transitions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["transition_id"]): row for row in transitions}


def reconstruct_checkpoint_path(
    *,
    initial_checkpoint_id: str,
    transition_ids: list[str],
    checkpoints: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    checkpoint_by_id = _checkpoint_index(checkpoints)
    transition_by_id = _transition_index(transitions)
    if initial_checkpoint_id not in checkpoint_by_id:
        raise KeyError(f"Unknown initial checkpoint id: {initial_checkpoint_id}")

    path = [checkpoint_by_id[initial_checkpoint_id]]
    current_checkpoint_id = initial_checkpoint_id
    for transition_id_value in transition_ids:
        if transition_id_value not in transition_by_id:
            raise KeyError(f"Unknown transition id: {transition_id_value}")
        transition = transition_by_id[transition_id_value]
        if transition["from_checkpoint_id"] != current_checkpoint_id:
            raise ValueError(
                "Transition chain is not contiguous: "
                f"{transition_id_value} starts at {transition['from_checkpoint_id']} "
                f"but the current checkpoint is {current_checkpoint_id}."
            )
        current_checkpoint_id = str(transition["to_checkpoint_id"])
        path.append(checkpoint_by_id[current_checkpoint_id])
    return path


def build_public_graph_replay(
    *,
    checkpoints: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    public_world_path: list[str],
    initial_checkpoint_id: str,
) -> dict[str, list[str]]:
    checkpoint_by_id = _checkpoint_index(checkpoints)
    if initial_checkpoint_id not in checkpoint_by_id:
        raise KeyError(f"Unknown initial checkpoint id: {initial_checkpoint_id}")

    current_checkpoint = checkpoint_by_id[initial_checkpoint_id]
    checkpoint_ids = [str(current_checkpoint["checkpoint_id"])]
    transition_ids: list[str] = []

    for target_year, target_world in enumerate(public_world_path[1:], start=2):
        transition = next(
            row
            for row in transitions
            if str(row["from_checkpoint_id"]) == str(current_checkpoint["checkpoint_id"])
            and int(row["target_year"]) == target_year
            and str(row["target_world_id"]) == target_world
            and str(row["target_frequency_model_family"]) == str(current_checkpoint["frequency_model_family"])
            and str(row["target_severity_model_family"]) == str(current_checkpoint["severity_model_family"])
        )
        transition_ids.append(str(transition["transition_id"]))
        current_checkpoint = checkpoint_by_id[str(transition["to_checkpoint_id"])]
        checkpoint_ids.append(str(current_checkpoint["checkpoint_id"]))

    return {
        "checkpoint_ids": checkpoint_ids,
        "transition_ids": transition_ids,
    }


def build_demo_manifest(
    *,
    checkpoints: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    years: int = DEFAULT_YEARS,
    seed: int = DEFAULT_SEED,
    version: str = DEFAULT_VERSION,
) -> dict[str, Any]:
    source_lineage = _source_lineage()
    public_world_path = generate_public_world_path(years=years, seed=seed)
    public_graph_replay = build_public_graph_replay(
        checkpoints=checkpoints,
        transitions=transitions,
        public_world_path=public_world_path,
        initial_checkpoint_id=checkpoint_id(1, "stable_baseline", "baseline_tariff", "baseline_tariff", seed, version),
    )
    return {
        "demo_name": "Example A: Small Public Demo",
        "description": "Finite 5-world x 3-frequency-model x 3-severity-model x 10-year lattice with one locked retraining regime.",
        "years": years,
        "seed": seed,
        "version": version,
        "retraining_regime": DEFAULT_RETRAINING,
        "training_base_year": -1,
        "training_base_source": "French motor data",
        "training_window_rule": "Year 1 uses a 1-year initial training window; Year 2 onward uses a rolling 2-year window through the prior year.",
        "source_lineage": source_lineage,
        "target_model_note": "Frequency and severity models are chosen separately; pure premium RMSE combines frequency RMSE and severity RMSE.",
        "step_note": TRAINING_BASE_NOTE,
        "world_count": len(WORLD_CATALOG),
        "frequency_model_count": len(MODEL_CATALOG),
        "severity_model_count": len(MODEL_CATALOG),
        "checkpoint_count": len(checkpoints),
        "transition_count": len(transitions),
        "full_paths_from_one_initial_state": (len(WORLD_CATALOG) * len(MODEL_CATALOG) * len(MODEL_CATALOG)) ** (years - 1),
        "storage_rule": "Store reusable yearly checkpoints and transitions, not duplicated full paths.",
        "world_catalog": [asdict(world) for world in WORLD_CATALOG],
        "model_catalog": [asdict(model) for model in MODEL_CATALOG],
        "public_world_path": public_world_path,
        "public_world_path_rule": "Seeded stochastic autocorrelated scenario: worlds tend to persist and often move along a natural order, but can stay longer, move early, or step back.",
        "public_checkpoint_path": public_graph_replay["checkpoint_ids"],
        "public_transition_path": public_graph_replay["transition_ids"],
        "public_checkpoint_path_rule": "Walk the graph along the seeded public world path while keeping the current frequency and severity model families fixed between yearly boundaries.",
        "initial_checkpoint_id": checkpoint_id(1, "stable_baseline", "baseline_tariff", "baseline_tariff", seed, version),
        "root_checkpoint_id": source_lineage["root_checkpoint_id"],
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_example_a_artifacts(
    output_dir: str | Path,
    *,
    years: int = DEFAULT_YEARS,
    seed: int = DEFAULT_SEED,
    version: str = DEFAULT_VERSION,
) -> dict[str, str]:
    if years != DEFAULT_YEARS:
        raise ValueError("Example A is intentionally fixed at 10 yearly steps.")
    output_path = Path(output_dir)
    checkpoints = build_yearly_checkpoints(years=years, seed=seed, version=version)
    transitions = build_yearly_transitions(checkpoints=checkpoints, years=years, seed=seed, version=version)
    manifest = build_demo_manifest(checkpoints=checkpoints, transitions=transitions, years=years, seed=seed, version=version)
    event_log_schema = {
        "event_types": ["session_start", "year_boundary_choice", "playback_step", "session_complete"],
        "session_start": ["session_id", "initial_checkpoint_id", "retraining_regime", "seed", "version"],
        "year_boundary_choice": ["session_id", "boundary_year", "transition_id", "from_checkpoint_id", "to_checkpoint_id"],
        "playback_step": ["session_id", "current_checkpoint_id"],
        "session_complete": ["session_id", "final_checkpoint_id", "chosen_transition_ids"],
    }
    source_lineage = manifest["source_lineage"]

    checkpoint_path = output_path / "yearly_checkpoints.csv"
    transition_path = output_path / "yearly_transitions.csv"
    manifest_path = output_path / "demo_manifest.json"
    summary_path = output_path / "run_summary.json"
    event_log_schema_path = output_path / "session_event_log_schema.json"

    write_csv(checkpoints, checkpoint_path)
    write_csv(transitions, transition_path)
    write_json(manifest, manifest_path)
    write_json(
        {
            **manifest,
            "artifact_label": "example_a_lattice",
            "source_lineage": source_lineage,
            "public_root_checkpoint_id": source_lineage["root_checkpoint_id"],
        },
        summary_path,
    )
    write_json(event_log_schema, event_log_schema_path)

    return {
        "output_dir": str(output_path),
        "yearly_checkpoints_path": str(checkpoint_path),
        "yearly_transitions_path": str(transition_path),
        "demo_manifest_path": str(manifest_path),
        "run_summary_path": str(summary_path),
        "session_event_log_schema_path": str(event_log_schema_path),
    }
