from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.example_a_public_demo import (
    DEFAULT_SEED,
    build_demo_manifest,
    build_example_a_artifacts,
    build_yearly_checkpoints,
    build_yearly_transitions,
    generate_public_world_path,
    reconstruct_checkpoint_path,
)
from src.example_a_public_demo_dashboard import build_example_a_dashboard


class ExampleAPublicDemoTests(unittest.TestCase):
    def test_lattice_counts_match_example_a(self) -> None:
        checkpoints = build_yearly_checkpoints(seed=DEFAULT_SEED)
        transitions = build_yearly_transitions(checkpoints=checkpoints, seed=DEFAULT_SEED)
        manifest = build_demo_manifest(checkpoints=checkpoints, transitions=transitions, seed=DEFAULT_SEED)

        self.assertEqual(len(checkpoints), 450)
        self.assertEqual(len(transitions), 18225)
        self.assertEqual(manifest["full_paths_from_one_initial_state"], 756680642578125)
        self.assertEqual(manifest["world_count"], 5)
        self.assertEqual(manifest["years"], 10)
        self.assertEqual(manifest["public_world_path"], generate_public_world_path(seed=DEFAULT_SEED))
        self.assertEqual(manifest["public_world_path"][0], "stable_baseline")
        self.assertGreater(len(set(manifest["public_world_path"])), 1)
        self.assertIn("rolling 2-year window", manifest["training_window_rule"])

        source_glm = next(
            row
            for row in checkpoints
            if row["year"] == 1
            and row["world_id"] == "stable_baseline"
            and row["frequency_model_family"] == "GLM"
            and row["severity_model_family"] == "GLM"
        )
        source_xgb = next(
            row
            for row in checkpoints
            if row["year"] == 1
            and row["world_id"] == "stable_baseline"
            and row["frequency_model_family"] == "XGBoost"
            and row["severity_model_family"] == "XGBoost"
        )
        glm_stable_to_good = next(
            row
            for row in transitions
            if row["from_checkpoint_id"] == source_glm["checkpoint_id"]
            and row["target_world_id"] == "good_years"
            and row["target_frequency_model_family"] == "GLM"
            and row["target_severity_model_family"] == "GLM"
        )
        xgb_stable_to_good = next(
            row
            for row in transitions
            if row["from_checkpoint_id"] == source_xgb["checkpoint_id"]
            and row["target_world_id"] == "good_years"
            and row["target_frequency_model_family"] == "XGBoost"
            and row["target_severity_model_family"] == "XGBoost"
        )
        self.assertLess(float(glm_stable_to_good["target_pure_premium_rmse"]), float(xgb_stable_to_good["target_pure_premium_rmse"]))
        self.assertIn("Stable/good rolling window", glm_stable_to_good["game_effect_summary"])

    def test_transition_references_existing_checkpoints(self) -> None:
        checkpoints = build_yearly_checkpoints(seed=DEFAULT_SEED)
        transitions = build_yearly_transitions(checkpoints=checkpoints, seed=DEFAULT_SEED)
        checkpoint_ids = {row["checkpoint_id"] for row in checkpoints}

        self.assertTrue(transitions)
        for transition in transitions:
            self.assertIn(transition["from_checkpoint_id"], checkpoint_ids)
            self.assertIn(transition["to_checkpoint_id"], checkpoint_ids)
            self.assertEqual(int(transition["target_year"]), int(transition["boundary_year"]) + 1)

    def test_artifacts_and_dashboard_are_created(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = build_example_a_artifacts(temp_dir, seed=DEFAULT_SEED)
            dashboard_path = build_example_a_dashboard(temp_dir)

            for key in (
                "yearly_checkpoints_path",
                "yearly_transitions_path",
                "demo_manifest_path",
                "run_summary_path",
                "session_event_log_schema_path",
            ):
                self.assertTrue(Path(result[key]).exists(), key)
            self.assertTrue(dashboard_path.exists())
            index_path = Path(temp_dir) / "index.html"
            public_path = Path(temp_dir) / "public.html"
            info_path = Path(temp_dir) / "info.html"
            sequence_adjustment_path = Path(temp_dir) / "sequence_adjustment.html"
            self.assertTrue(index_path.exists())
            self.assertTrue(public_path.exists())
            self.assertTrue(info_path.exists())
            self.assertTrue(sequence_adjustment_path.exists())

            with Path(result["yearly_checkpoints_path"]).open("r", newline="", encoding="utf-8") as handle:
                checkpoint_rows = list(csv.DictReader(handle))
                self.assertEqual(len(checkpoint_rows), 450)
                self.assertNotIn("adaptation_cost", checkpoint_rows[0])
                self.assertNotIn("governance_burden", checkpoint_rows[0])
                self.assertNotIn("resilience_score", checkpoint_rows[0])
                self.assertNotIn("cumulative_loss_index", checkpoint_rows[0])
                self.assertNotIn("claim_pressure_index", checkpoint_rows[0])
                self.assertIn("frequency_rmse", checkpoint_rows[0])
                self.assertIn("severity_rmse", checkpoint_rows[0])
                self.assertIn("training_window_years", checkpoint_rows[0])
                self.assertIn("training_window_label", checkpoint_rows[0])
                self.assertEqual(checkpoint_rows[0]["training_window_years"], "1")
                year_two_checkpoint = next(row for row in checkpoint_rows if row["year"] == "2")
                self.assertEqual(year_two_checkpoint["training_window_years"], "2")
            with Path(result["yearly_transitions_path"]).open("r", newline="", encoding="utf-8") as handle:
                transition_rows_for_schema = list(csv.DictReader(handle))
                self.assertEqual(len(transition_rows_for_schema), 18225)
                self.assertIn("target_pure_premium_rmse", transition_rows_for_schema[0])
                self.assertIn("target_training_window_years", transition_rows_for_schema[0])
                self.assertIn("game_effect_summary", transition_rows_for_schema[0])

            summary = json.loads(Path(result["run_summary_path"]).read_text(encoding="utf-8"))
            self.assertEqual(summary["storage_rule"], "Store reusable yearly checkpoints and transitions, not duplicated full paths.")
            self.assertEqual(summary["training_base_year"], -1)
            self.assertEqual(summary["training_base_source"], "French motor data")
            self.assertIn("rolling 2-year window", summary["training_window_rule"])
            self.assertEqual(summary["root_checkpoint_id"], "root_y0_french_motor_public_demo")
            self.assertEqual(summary["source_lineage"]["source_name"], "French Motor third-party liability raw data")
            self.assertEqual(summary["source_lineage"]["root_checkpoint_id"], "root_y0_french_motor_public_demo")
            self.assertEqual(summary["source_lineage"]["source_files"], ["data/raw/freMTPL2freq.csv", "data/raw/freMTPL2sev.csv"])
            self.assertEqual(len(summary["public_checkpoint_path"]), 10)
            self.assertEqual(len(summary["public_transition_path"]), 9)
            with Path(result["yearly_checkpoints_path"]).open("r", newline="", encoding="utf-8") as handle:
                checkpoint_rows = list(csv.DictReader(handle))
            with Path(result["yearly_transitions_path"]).open("r", newline="", encoding="utf-8") as handle:
                transition_rows = list(csv.DictReader(handle))
            replay_path = reconstruct_checkpoint_path(
                initial_checkpoint_id=summary["initial_checkpoint_id"],
                transition_ids=summary["public_transition_path"],
                checkpoints=checkpoint_rows,
                transitions=transition_rows,
            )
            self.assertEqual([row["checkpoint_id"] for row in replay_path], summary["public_checkpoint_path"])
            self.assertEqual([row["world_id"] for row in replay_path], summary["public_world_path"])
            self.assertEqual(int(replay_path[0]["year"]), 1)
            self.assertEqual(int(replay_path[-1]["year"]), 10)
            self.assertIn("Frequency and severity models are chosen separately", summary["target_model_note"])
            dashboard_html = dashboard_path.read_text(encoding="utf-8")
            self.assertIn("Example A Public Demo", dashboard_html)
            self.assertIn("Advance 1 Year", dashboard_html)
            self.assertIn("Target World [W]", dashboard_html)
            self.assertIn("Frequency Model [F]", dashboard_html)
            self.assertIn("Severity Model [S]", dashboard_html)
            self.assertIn("[W] Target world is the insurance environment applied to the next yearly checkpoint.", dashboard_html)
            self.assertIn("Frequency and severity are trained separately", dashboard_html)
            self.assertIn("rolling 2-year window", dashboard_html)
            self.assertIn("Training Window", dashboard_html)
            self.assertIn("Model Info", dashboard_html)
            self.assertIn("World Info", dashboard_html)
            self.assertIn("Root", dashboard_html)
            self.assertIn("Replay", dashboard_html)
            self.assertIn("[W] Target world means the insurance environment you want to simulate next.", dashboard_html)
            self.assertIn("Year 1 uses one prior-year slice", dashboard_html)
            self.assertIn("Root checkpoint: French Motor raw files are", dashboard_html)
            self.assertIn("data/raw/freMTPL2freq.csv", dashboard_html)
            self.assertIn("data/raw/freMTPL2sev.csv", dashboard_html)
            self.assertIn("Open public-friendly GUI", dashboard_html)
            self.assertNotIn("Governance", dashboard_html)
            self.assertNotIn("adaptation_cost", dashboard_html)
            self.assertNotIn("Resilience", dashboard_html)
            self.assertNotIn("Loss Index", dashboard_html)
            self.assertNotIn("Claim Pressure", dashboard_html)
            self.assertIn("Self-Drive Revolution", dashboard_html)
            self.assertIn("Good Years", dashboard_html)
            self.assertIn("exact source is the public French Motor third-party liability raw data files", dashboard_html)
            self.assertIn("data/raw/freMTPL2freq.csv", dashboard_html)
            self.assertIn("data/raw/freMTPL2sev.csv", dashboard_html)
            self.assertIn("synthetic simulation layers designed for product demonstration", dashboard_html)

            public_html = public_path.read_text(encoding="utf-8")
            self.assertIn("Can you manage MTPL risk under uncertainty?", public_html)
            self.assertNotIn("Open admin lattice view", public_html)
            self.assertNotIn('href="admin.html"', public_html)
            self.assertNotIn("Next World [W]", public_html)
            self.assertIn("Frequency Model [F]", public_html)
            self.assertIn("Severity Model [S]", public_html)
            self.assertIn("Advance 1 Year", public_html)
            self.assertIn("Advance 5 Years", public_html)
            self.assertIn("The next insurance world is revealed after each recalculation", public_html)
            self.assertIn("rolling 2-year window", public_html)
            self.assertIn("Training Window", public_html)
            self.assertIn("hidden seeded stochastic scenario path", public_html)
            self.assertIn("What the models mean", public_html)
            self.assertIn("What the worlds mean", public_html)
            self.assertIn("Root checkpoint: French Motor raw files are", public_html)
            self.assertIn("Worlds are alternate insurance regimes", public_html)
            self.assertIn("RMSE Replay", public_html)
            self.assertIn("publicRmseChart", public_html)
            self.assertIn("Time 0: advance to create the first yearly checkpoint", public_html)
            self.assertIn("10-Year Benchmark", public_html)
            self.assertIn("Replay Chain", public_html)
            self.assertIn("pricingExpertBenchmarkDatabase", public_html)
            self.assertIn("pricingExpertYearlyBenchmarkDatabase", public_html)
            self.assertIn("publicWorldPath", public_html)
            self.assertIn("publicWorldForYear", public_html)
            self.assertIn("World revealed:", public_html)
            self.assertIn("worldLabel", public_html)
            self.assertIn("runningPercentileForYear", public_html)
            self.assertIn("Better than", public_html)
            self.assertIn("You did better than", public_html)
            self.assertIn("resultModal", public_html)
            self.assertIn("resultGraphic", public_html)
            self.assertIn("advanceFiveYears", public_html)
            self.assertIn("★★★★★", public_html)
            self.assertIn("😡", public_html)
            self.assertIn("calcStatus", public_html)
            self.assertIn("calcProgressBar", public_html)
            self.assertIn("Recalculating year", public_html)
            self.assertIn("realisticRecalculation", public_html)
            self.assertIn("Connecting to back end simulation service", public_html)
            self.assertNotIn("OpenAI", public_html)
            self.assertNotIn("WebSocket", public_html)
            self.assertIn("15000 + (normalish * 3000)", public_html)
            self.assertIn("displayedProgress = Math.max(displayedProgress, jitter)", public_html)
            self.assertIn("Finalizing year checkpoint", public_html)
            self.assertIn("completeAdvance", public_html)
            self.assertIn("showResultModalForLatestYear", public_html)
            self.assertIn("Year ${latest.year} Complete", public_html)
            self.assertIn("After year ${latest.year}, you did better than", public_html)
            self.assertIn("exact source is the public French Motor third-party liability raw data files", public_html)
            self.assertIn("data/raw/freMTPL2freq.csv", public_html)
            self.assertIn("data/raw/freMTPL2sev.csv", public_html)
            self.assertIn("synthetic simulation layers designed for product demonstration", public_html)

            info_html = info_path.read_text(encoding="utf-8")
            self.assertIn("Training World Transfer", info_html)
            self.assertIn("How The Models Tackle It", info_html)
            self.assertIn("Frequency vs Severity Choices", info_html)
            self.assertIn("sequence_adjustment", info_html)
            self.assertIn("white-space: pre-wrap", info_html)
            self.assertIn("+ sequence_adjustment", info_html)
            self.assertIn("  + calm_overfit_penalty", info_html)
            self.assertIn("  + shock_penalty", info_html)
            self.assertIn("  - stable_window_bonus", info_html)
            self.assertIn("  - complexity_bonus", info_html)
            self.assertIn("Same or similar world", info_html)
            self.assertIn("Different world", info_html)
            self.assertIn("Baseline Tariff", info_html)
            self.assertIn("GLM", info_html)
            self.assertIn("XGBoost", info_html)
            self.assertIn("sequence_adjustment.html", info_html)
            self.assertIn("Open exact sequence adjustment tables", info_html)

            sequence_adjustment_html = sequence_adjustment_path.read_text(encoding="utf-8")
            self.assertIn("Sequence Adjustment Detail", sequence_adjustment_html)
            self.assertIn("Model Inputs", sequence_adjustment_html)
            self.assertIn("Baseline Tariff Sequence Adjustment", sequence_adjustment_html)
            self.assertIn("GLM Sequence Adjustment", sequence_adjustment_html)
            self.assertIn("XGBoost Sequence Adjustment", sequence_adjustment_html)
            self.assertIn("Source World", sequence_adjustment_html)
            self.assertIn("Target World", sequence_adjustment_html)
            self.assertIn("Calm Overfit Penalty", sequence_adjustment_html)
            self.assertIn("Shock Penalty", sequence_adjustment_html)
            self.assertIn("Stable Window Bonus", sequence_adjustment_html)
            self.assertIn("Complexity Bonus", sequence_adjustment_html)
            self.assertIn("Sequence Adjustment", sequence_adjustment_html)
            self.assertIn("Stable Baseline", sequence_adjustment_html)
            self.assertIn("Self-Drive Revolution", sequence_adjustment_html)
            self.assertIn("0.015779", sequence_adjustment_html)
            self.assertIn("-0.021900", sequence_adjustment_html)


if __name__ == "__main__":
    unittest.main()
