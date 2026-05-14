from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_example_a_dashboard_data(artifact_dir: str | Path) -> dict[str, Any]:
    root = Path(artifact_dir)
    return {
        "manifest": _load_json(root / "demo_manifest.json"),
        "checkpoints": _load_csv(root / "yearly_checkpoints.csv"),
        "transitions": _load_csv(root / "yearly_transitions.csv"),
    }


def build_example_a_dashboard_html(data: dict[str, Any]) -> str:
    embedded = json.dumps(data)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Example A Public Demo</title>
  <style>
    :root {{
      --ink: #18212b;
      --muted: #64707d;
      --paper: #f5f0e8;
      --panel: #fffaf1;
      --line: rgba(24, 33, 43, 0.14);
      --teal: #0f766e;
      --blue: #1d4ed8;
      --amber: #b45309;
      --red: #be123c;
      --green: #4d7c0f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    .shell {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 40px; }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      gap: 18px;
      align-items: stretch;
      min-height: 320px;
    }}
    .hero-main {{
      padding: 32px;
      border: 1px solid var(--line);
      background:
        linear-gradient(rgba(255, 250, 241, 0.86), rgba(255, 250, 241, 0.86)),
        repeating-linear-gradient(90deg, rgba(15, 118, 110, 0.12) 0 1px, transparent 1px 72px),
        repeating-linear-gradient(0deg, rgba(180, 83, 9, 0.10) 0 1px, transparent 1px 58px);
      border-radius: 8px;
    }}
    h1 {{
      margin: 0;
      max-width: 780px;
      font-family: Georgia, 'Times New Roman', serif;
      font-size: clamp(42px, 6vw, 78px);
      line-height: 0.96;
      letter-spacing: 0;
    }}
    .subtitle {{ margin: 18px 0 0; max-width: 680px; color: var(--muted); font-size: 18px; line-height: 1.5; }}
    .panel {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 18px; }}
    .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .summary-card {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: rgba(255, 255, 255, 0.44); }}
    .label {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0; }}
    .value {{ margin-top: 6px; font-size: 26px; font-weight: 700; }}
    .sub {{ margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.35; }}
    .section {{ margin-top: 22px; }}
    .section-head {{ display: flex; justify-content: space-between; gap: 16px; align-items: end; margin-bottom: 10px; }}
    h2 {{ margin: 0; font-family: Georgia, 'Times New Roman', serif; font-size: 28px; letter-spacing: 0; }}
    .controls {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .step-note {{ margin-top: 12px; color: var(--muted); font-size: 13px; line-height: 1.45; }}
    select, button {{
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: white;
      color: var(--ink);
      font: inherit;
      padding: 8px 10px;
    }}
    button {{ cursor: pointer; font-weight: 700; }}
    button.primary {{ background: var(--teal); color: white; border-color: var(--teal); }}
    button:disabled {{ opacity: 0.45; cursor: default; }}
    .rail {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
    .year-card {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: white; min-height: 150px; }}
    .year-card.active {{ border-color: var(--teal); box-shadow: inset 0 0 0 2px rgba(15, 118, 110, 0.18); }}
    .pill {{ display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 8px; font-size: 12px; font-weight: 700; background: rgba(15, 118, 110, 0.10); color: var(--teal); }}
    .pill.warn {{ background: rgba(180, 83, 9, 0.12); color: var(--amber); }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .chart-wrap {{ min-height: 300px; }}
    svg {{ width: 100%; height: auto; display: block; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0; }}
    .table-wrap {{ overflow-x: auto; }}
    .model-info-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .world-info-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .view-link {{ display: inline-flex; margin-top: 16px; color: var(--teal); font-weight: 700; text-decoration: none; }}
    .source-note {{ margin-top: 24px; border-top: 1px solid var(--line); padding-top: 14px; color: var(--muted); font-size: 12px; line-height: 1.5; }}
    @media (max-width: 840px) {{
      .hero, .controls, .metric-grid, .rail {{ grid-template-columns: 1fr; }}
      .summary-grid {{ grid-template-columns: 1fr 1fr; }}
      h1 {{ font-size: 44px; }}
    }}
    @media (max-width: 520px) {{
      .summary-grid {{ grid-template-columns: 1fr; }}
      .hero-main {{ padding: 22px; }}
      h1 {{ font-size: 36px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-main">
        <div class="label">World-Switching Lab</div>
        <h1>Example A Public Demo</h1>
        <p class="subtitle">A finite yearly lattice for five insurance worlds, separate frequency and severity model choices, ten decisions, and one locked retraining regime.</p>
        <div style="display: flex; gap: 24px;">
          <a class="view-link" href="public.html">Open public-friendly GUI</a>
          <a class="view-link" href="info.html">Understand assumptions behind &rarr;</a>
        </div>
      </div>
      <div class="panel summary-grid" id="summaryGrid"></div>
    </section>

    <section class="section panel">
      <div class="section-head">
        <h2>Control Room</h2>
        <span class="pill" id="statusPill"></span>
      </div>
      <div class="controls">
        <div>
          <div class="label">Target World [W]</div>
          <select id="worldSelect"></select>
        </div>
        <div>
          <div class="label">Frequency Model [F]</div>
          <select id="frequencyModelSelect"></select>
        </div>
        <div>
          <div class="label">Severity Model [S]</div>
          <select id="severityModelSelect"></select>
        </div>
        <div>
          <div class="label">Step</div>
          <button class="primary" id="advanceButton">Advance 1 Year</button>
        </div>
        <div>
          <div class="label">Session</div>
          <button id="resetButton">Reset</button>
        </div>
      </div>
      <p class="step-note">[W] Target world is the insurance environment applied to the next yearly checkpoint. [F] and [S] models are retrained using a rolling 2-year window through the prior year. Root checkpoint: French Motor raw files are `data/raw/freMTPL2freq.csv` and `data/raw/freMTPL2sev.csv`.</p>
    </section>

    <section class="section">
      <div class="section-head"><h2>Yearly Path</h2></div>
      <div class="rail" id="yearRail"></div>
    </section>

    <section class="section">
      <div class="metric-grid" id="metricGrid"></div>
    </section>

    <section class="section panel">
      <div class="section-head"><h2>RMSE Replay</h2></div>
      <div class="chart-wrap"><svg id="chart" viewBox="0 0 960 300"></svg></div>
    </section>

    <section class="section panel">
      <div class="section-head"><h2>Chosen Transitions</h2></div>
      <div class="table-wrap"><table id="transitionTable"></table></div>
    </section>

    <section class="section panel">
      <div class="section-head"><h2>Model Info</h2></div>
      <p class="step-note">[F] and [S] are chosen separately. Frequency and severity are trained separately on the rolling 2-year window after Year 1; pure premium RMSE combines both errors.</p>
      <div class="model-info-grid" id="modelInfoGrid"></div>
    </section>

    <section class="section panel">
      <div class="section-head"><h2>World Info</h2></div>
      <p class="step-note">[W] Target world means the insurance environment you want to simulate next. It changes the frequency and severity conditions for the next yearly checkpoint.</p>
      <div class="world-info-grid" id="worldInfoGrid"></div>
    </section>

    <footer class="source-note">
      Source note: exact source is the public French Motor third-party liability raw data files `data/raw/freMTPL2freq.csv` and `data/raw/freMTPL2sev.csv`, then simulated on top as a finite insurance futures lattice. The worlds, model choices, yearly paths, RMSE replay, benchmark totals, and transition graph are synthetic simulation layers designed for product demonstration, not external market forecasts.
    </footer>
  </main>

  <script>
    const data = {embedded};
    const manifest = data.manifest;
    const checkpoints = data.checkpoints.map((row) => ({{
      ...row,
      year: Number(row.year),
      training_window_years: Number(row.training_window_years),
      training_data_start_year: Number(row.training_data_start_year),
      training_data_end_year: Number(row.training_data_end_year),
      frequency_rmse: Number(row.frequency_rmse),
      severity_rmse: Number(row.severity_rmse),
      pure_premium_rmse: Number(row.pure_premium_rmse),
      net_strategic_value: Number(row.net_strategic_value),
    }}));
    const transitions = data.transitions.map((row) => ({{
      ...row,
      boundary_year: Number(row.boundary_year),
      target_year: Number(row.target_year),
      pure_premium_rmse_delta: Number(row.pure_premium_rmse_delta),
      target_training_window_years: Number(row.target_training_window_years),
      target_training_data_start_year: Number(row.target_training_data_start_year),
      target_training_data_end_year: Number(row.target_training_data_end_year),
      target_frequency_rmse: Number(row.target_frequency_rmse),
      target_severity_rmse: Number(row.target_severity_rmse),
      target_pure_premium_rmse: Number(row.target_pure_premium_rmse),
      target_net_strategic_value: Number(row.target_net_strategic_value),
      recommended: row.recommended === "True" || row.recommended === true,
    }}));
    const checkpointById = new Map(checkpoints.map((row) => [row.checkpoint_id, row]));
    const initialCheckpoint = checkpointById.get(manifest.initial_checkpoint_id);
    const worlds = manifest.world_catalog;
    const models = manifest.model_catalog;
    const state = {{
      currentCheckpointId: null,
      firstCheckpointId: null,
      chosenTransitions: [],
    }};

    function title(value) {{
      return String(value || "").replaceAll("_", " ").replace(/\\b\\w/g, (letter) => letter.toUpperCase());
    }}

    function number(value, digits = 1) {{
      return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : "-";
    }}

    function checkpointFromTransition(row) {{
      const base = checkpointById.get(row.to_checkpoint_id);
      if (!base) {{
        return null;
      }}
      return {{
        ...base,
        training_window_years: row.target_training_window_years || base.training_window_years,
        training_window_label: row.target_training_window_label || base.training_window_label,
        training_data_start_year: Number.isFinite(row.target_training_data_start_year) ? row.target_training_data_start_year : base.training_data_start_year,
        training_data_end_year: Number.isFinite(row.target_training_data_end_year) ? row.target_training_data_end_year : base.training_data_end_year,
        frequency_rmse: Number.isFinite(row.target_frequency_rmse) ? row.target_frequency_rmse : base.frequency_rmse,
        severity_rmse: Number.isFinite(row.target_severity_rmse) ? row.target_severity_rmse : base.severity_rmse,
        pure_premium_rmse: Number.isFinite(row.target_pure_premium_rmse) ? row.target_pure_premium_rmse : base.pure_premium_rmse,
        net_strategic_value: Number.isFinite(row.target_net_strategic_value) ? row.target_net_strategic_value : base.net_strategic_value,
        game_effect_summary: row.game_effect_summary || base.game_effect_summary,
      }};
    }}

    function currentCheckpoint() {{
      if (!state.currentCheckpointId) {{
        return null;
      }}
      const latestTransition = state.chosenTransitions[state.chosenTransitions.length - 1];
      if (latestTransition && latestTransition.to_checkpoint_id === state.currentCheckpointId) {{
        return checkpointFromTransition(latestTransition);
      }}
      return checkpointById.get(state.currentCheckpointId);
    }}

    function selectedYearOneCheckpoint(targetWorld, targetFrequencyModel, targetSeverityModel) {{
      return checkpoints.find((row) =>
        row.year === 1 &&
        row.world_id === targetWorld &&
        row.frequency_model_family === targetFrequencyModel &&
        row.severity_model_family === targetSeverityModel
      ) || null;
    }}

    function transitionFor(targetWorld, targetFrequencyModel, targetSeverityModel) {{
      const current = currentCheckpoint();
      if (!current) {{
        return null;
      }}
      return transitions.find((row) =>
        row.from_checkpoint_id === current.checkpoint_id &&
        row.target_world_id === targetWorld &&
        row.target_frequency_model_family === targetFrequencyModel &&
        row.target_severity_model_family === targetSeverityModel
      );
    }}

    function populateControls() {{
      const current = currentCheckpoint() || initialCheckpoint;
      const worldSelect = document.getElementById("worldSelect");
      const frequencyModelSelect = document.getElementById("frequencyModelSelect");
      const severityModelSelect = document.getElementById("severityModelSelect");
      const atLimit = Boolean(currentCheckpoint() && current.year >= manifest.years);
      const busy = state.recalculating;
      worldSelect.innerHTML = worlds.map((world) => `<option value="${{world.world_id}}">${{world.label}}</option>`).join("");
      frequencyModelSelect.innerHTML = models.map((model) => `<option value="${{model.model_family}}">${{model.label}}</option>`).join("");
      severityModelSelect.innerHTML = models.map((model) => `<option value="${{model.model_family}}">${{model.label}}</option>`).join("");
      worldSelect.value = current.world_id;
      frequencyModelSelect.value = current.frequency_model_family;
      severityModelSelect.value = current.severity_model_family;
      document.getElementById("advanceButton").disabled = atLimit || busy;
      const advanceFiveButton = document.getElementById("advanceFiveButton");
      if (advanceFiveButton) {{
        advanceFiveButton.disabled = atLimit || busy;
      }}
    }}

    function renderSummary() {{
      const current = currentCheckpoint();
      const replayCheckpointCount = manifest.public_checkpoint_path?.length || 0;
      const replayTransitionCount = manifest.public_transition_path?.length || 0;
      const cards = [
        ["Checkpoints", manifest.checkpoint_count, `${{manifest.years}} years x 5 worlds x 3 x 3`],
        ["Transitions", manifest.transition_count, `${{Math.max(0, manifest.years - 1)}} boundaries x 45 x 45`],
        ["Full Paths", manifest.full_paths_from_one_initial_state, "not materialized"],
        ["Replay", `${{replayCheckpointCount}} / ${{replayTransitionCount}}`, "checkpoint ids / transition ids"],
        ["Retraining", title(manifest.retraining_regime), "locked"],
        ["Root", title(manifest.source_lineage?.root_checkpoint_label || "French Motor Root"), (manifest.source_lineage?.source_files || []).join(" + ")],
      ];
      document.getElementById("summaryGrid").innerHTML = cards.map(([label, value, sub]) => `
        <div class="summary-card"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
      `).join("");
      document.getElementById("statusPill").textContent = current ? `Year ${{current.year}} / ${{manifest.years}}` : `Time 0 / ${{manifest.years}} years`;
    }}

    function pathCheckpoints() {{
      if (!currentCheckpoint()) {{
        return [];
      }}
      const first = checkpointById.get(state.firstCheckpointId || state.currentCheckpointId);
      return [first, ...state.chosenTransitions.map((item) => checkpointFromTransition(item))].filter(Boolean);
    }}

    function renderRail() {{
      const path = pathCheckpoints();
      document.getElementById("yearRail").innerHTML = Array.from({{ length: manifest.years }}, (_, index) => {{
        const year = index + 1;
        const row = path.find((item) => item.year === year);
        const active = currentCheckpoint()?.year === year ? " active" : "";
        return `<div class="year-card${{active}}">
          <div class="label">Year ${{year}}</div>
          <div class="value">${{row ? title(row.world_id) : "Unrealised"}}</div>
          <div class="sub">${{row ? "F: " + title(row.frequency_model_family) + " | S: " + title(row.severity_model_family) : "No transition chosen"}}</div>
          ${{row ? `<span class="pill${{row.pure_premium_rmse > 0.25 ? " warn" : ""}}">RMSE ${{number(row.pure_premium_rmse, 3)}}</span>` : ""}}
        </div>`;
      }}).join("");
    }}

    function renderMetrics() {{
      const current = currentCheckpoint();
      if (!current) {{
        const metrics = [
          ["Time", "0", "No simulated year has elapsed"],
          ["World", title(initialCheckpoint?.world_id), "Initial target for the first yearly checkpoint"],
          ["Frequency Model", title(initialCheckpoint?.frequency_model_family), "Initial target for year 1"],
          ["Severity Model", title(initialCheckpoint?.severity_model_family), "Initial target for year 1"],
          ["Training Window", "1 year", "Year 1 uses one prior-year slice"],
          ["Pure Premium RMSE", "-", "Available after the first advance"],
          ["Frequency RMSE", "-", "Available after the first advance"],
          ["Severity RMSE", "-", "Available after the first advance"],
        ];
        document.getElementById("metricGrid").innerHTML = metrics.map(([label, value, sub]) => `
          <div class="panel"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
        `).join("");
        return;
      }}
      const metrics = [
        ["World", title(current.world_id), current.world_narrative],
        ["Frequency Model", title(current.frequency_model_family), current.frequency_model_narrative],
        ["Severity Model", title(current.severity_model_family), current.severity_model_narrative],
        ["Training Window", current.training_window_label || "-", current.game_effect_summary || "Rolling window effect"],
        ["Pure Premium RMSE", number(current.pure_premium_rmse, 3), "lower is better"],
        ["Frequency RMSE", number(current.frequency_rmse, 3), "claim count model error"],
        ["Severity RMSE", number(current.severity_rmse, 3), "claim size model error"],
      ];
      document.getElementById("metricGrid").innerHTML = metrics.map(([label, value, sub]) => `
        <div class="panel"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
      `).join("");
    }}

    function drawChart() {{
      const rows = pathCheckpoints();
      const width = 960;
      const height = 300;
      const pad = {{ left: 46, right: 18, top: 18, bottom: 34 }};
      const values = rows.map((row) => row.pure_premium_rmse);
      if (!rows.length) {{
        document.getElementById("chart").innerHTML = `<text x="50%" y="50%" text-anchor="middle" fill="#64707d">Time 0: advance to create the first yearly checkpoint</text>`;
        return;
      }}
      const minY = Math.min(0, ...values);
      const maxY = Math.max(0.6, ...values);
      const x = (year) => pad.left + ((year - 1) / Math.max(1, manifest.years - 1)) * (width - pad.left - pad.right);
      const y = (value) => pad.top + ((maxY - value) / Math.max(1, maxY - minY)) * (height - pad.top - pad.bottom);
      const path = rows.map((row, index) => `${{index === 0 ? "M" : "L"}} ${{x(row.year)}} ${{y(row.pure_premium_rmse)}}`).join(" ");
      const points = rows.map((row) => `<circle cx="${{x(row.year)}}" cy="${{y(row.pure_premium_rmse)}}" r="5" fill="#0f766e"></circle>`).join("");
      const labels = Array.from({{ length: manifest.years }}, (_, index) => {{
        const year = index + 1;
        return `<text x="${{x(year)}}" y="${{height - 10}}" text-anchor="middle" fill="#64707d" font-size="12">Y${{year}}</text>`;
      }}).join("");
      document.getElementById("chart").innerHTML = `
        <rect width="${{width}}" height="${{height}}" fill="transparent"></rect>
        <line x1="${{pad.left}}" y1="${{height - pad.bottom}}" x2="${{width - pad.right}}" y2="${{height - pad.bottom}}" stroke="rgba(24,33,43,0.2)"></line>
        <line x1="${{pad.left}}" y1="${{pad.top}}" x2="${{pad.left}}" y2="${{height - pad.bottom}}" stroke="rgba(24,33,43,0.2)"></line>
        ${{labels}}
        <path d="${{path}}" fill="none" stroke="#0f766e" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
        ${{points}}
      `;
    }}

    function renderTransitions() {{
      const rows = state.chosenTransitions;
      const body = rows.length ? rows.map((row) => `
        <tr>
          <td>${{row.boundary_year}}</td>
          <td>${{title(row.source_world_id)}} -> ${{title(row.target_world_id)}}</td>
          <td>F: ${{title(row.source_frequency_model_family)}} -> ${{title(row.target_frequency_model_family)}}<br>S: ${{title(row.source_severity_model_family)}} -> ${{title(row.target_severity_model_family)}}</td>
          <td>${{number(row.pure_premium_rmse_delta, 3)}}</td>
        </tr>
      `).join("") : `<tr><td colspan="4">No transitions selected.</td></tr>`;
      document.getElementById("transitionTable").innerHTML = `
        <thead><tr><th>Boundary</th><th>World</th><th>Models</th><th>RMSE Improvement</th></tr></thead>
        <tbody>${{body}}</tbody>
      `;
    }}

    function renderModelInfo() {{
      document.getElementById("modelInfoGrid").innerHTML = models.map((model) => `
        <div class="summary-card">
          <div class="label">${{model.label}}</div>
          <div class="value">${{title(model.model_family)}}</div>
          <div class="sub">${{model.model_info}}</div>
        </div>
      `).join("");
    }}

    function renderWorldInfo() {{
      document.getElementById("worldInfoGrid").innerHTML = worlds.map((world) => `
        <div class="summary-card">
          <div class="label">${{world.label}}</div>
          <div class="value">${{title(world.world_id)}}</div>
          <div class="sub">${{world.narrative}}</div>
        </div>
      `).join("");
    }}

    function renderAll() {{
      populateControls();
      renderSummary();
      renderRail();
      renderMetrics();
      drawChart();
      renderTransitions();
      renderModelInfo();
      renderWorldInfo();
    }}

    function advanceYear() {{
      const targetWorld = document.getElementById("worldSelect").value;
      const targetFrequencyModel = document.getElementById("frequencyModelSelect").value;
      const targetSeverityModel = document.getElementById("severityModelSelect").value;
      if (!currentCheckpoint()) {{
        const firstCheckpoint = selectedYearOneCheckpoint(targetWorld, targetFrequencyModel, targetSeverityModel);
        if (!firstCheckpoint) {{
          return;
        }}
        state.currentCheckpointId = firstCheckpoint.checkpoint_id;
        state.firstCheckpointId = firstCheckpoint.checkpoint_id;
        renderAll();
        return;
      }}
      const transition = transitionFor(targetWorld, targetFrequencyModel, targetSeverityModel);
      if (!transition) {{
        return;
      }}
      state.chosenTransitions.push(transition);
      state.currentCheckpointId = transition.to_checkpoint_id;
      renderAll();
    }}

    function reset() {{
      state.currentCheckpointId = null;
      state.firstCheckpointId = null;
      state.chosenTransitions = [];
      renderAll();
    }}

    document.getElementById("advanceButton").addEventListener("click", advanceYear);
    document.getElementById("resetButton").addEventListener("click", reset);
    renderAll();
  </script>
</body>
</html>
"""


def build_example_a_public_html(data: dict[str, Any]) -> str:
    embedded = json.dumps(data)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>World-Switching Lab Public GUI</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #5f6f7a;
      --paper: #f7f3ec;
      --panel: #fffdf8;
      --line: rgba(23, 32, 42, 0.14);
      --teal: #0f766e;
      --blue: #2563eb;
      --amber: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--paper); color: var(--ink); }}
    .shell {{ max-width: 1040px; margin: 0 auto; padding: 24px 16px 42px; }}
    .hero {{
      min-height: 280px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 28px;
      background:
        linear-gradient(rgba(255,253,248,0.88), rgba(255,253,248,0.88)),
        repeating-linear-gradient(120deg, rgba(15,118,110,0.11) 0 2px, transparent 2px 86px);
    }}
    h1 {{ margin: 0; max-width: 760px; font-family: Georgia, 'Times New Roman', serif; font-size: clamp(32px, 5vw, 48px); line-height: 1.1; letter-spacing: -0.02em; }}
    .lede {{ max-width: 720px; margin: 16px 0 0; color: var(--muted); font-size: 16px; line-height: 1.6; }}
    .hero {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 40px; padding: 40px 0; border-bottom: 1px solid var(--line); margin-bottom: 30px; }}
    .hero-text {{ flex: 1; }}
    .forecast-box {{ width: 220px; background: white; border: 1px solid var(--line); border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }}
    .forecast-box .label {{ font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; display: block; }}
    .pie-wrap {{ position: relative; width: 120px; height: 120px; margin: 0 auto 12px; }}
    .pie-legend {{ display: grid; grid-template-columns: 1fr; gap: 4px; text-align: left; margin-top: 8px; }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--muted); }}
    .legend-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
    .top-link {{ display: inline-flex; margin-top: 16px; color: var(--teal); font-weight: 700; text-decoration: none; font-size: 14px; }}
    .section {{ margin-top: 18px; }}
    .panel {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 18px; }}
    .choices {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .field label {{ display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; margin-bottom: 6px; }}
    select, button {{ width: 100%; min-height: 46px; border: 1px solid var(--line); border-radius: 7px; padding: 9px 10px; font: inherit; background: white; color: var(--ink); }}
    button {{ cursor: pointer; font-weight: 700; }}
    button.primary {{ background: var(--teal); color: white; border-color: var(--teal); }}
    button:disabled {{ opacity: 0.45; cursor: default; }}
    .actions {{ display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: 12px; margin-top: 14px; }}
    .advance-group {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .calc-status {{ display: none; margin-top: 12px; border: 1px solid var(--line); border-radius: 8px; background: white; padding: 12px; }}
    .calc-status.active {{ display: block; }}
    .calc-bar {{ height: 8px; border-radius: 999px; background: rgba(23,32,42,0.10); overflow: hidden; }}
    .calc-bar span {{ display: block; height: 100%; width: 0%; border-radius: inherit; background: var(--teal); transition: width 180ms ease; }}
    .story {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }}
    .card {{ border: 1px solid var(--line); border-radius: 8px; background: white; padding: 16px; }}
    .label {{ color: var(--muted); font-size: 11px; text-transform: uppercase; }}
    .value {{ margin-top: 6px; font-size: 28px; font-weight: 700; }}
    .sub {{ margin-top: 6px; color: var(--muted); font-size: 13px; line-height: 1.4; }}
    .path {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
    .year {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: white; min-height: 120px; }}
    .year.active {{ border-color: var(--teal); box-shadow: inset 0 0 0 2px rgba(15,118,110,0.16); }}
    .benchmark {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .chart-wrap {{ min-height: 280px; overflow-x: auto; }}
    .chart-wrap svg {{ width: 100%; min-width: 640px; height: auto; display: block; }}
    .modal-backdrop {{ position: fixed; inset: 0; display: none; align-items: center; justify-content: center; padding: 20px; background: rgba(23,32,42,0.42); z-index: 20; }}
    .modal-backdrop.open {{ display: flex; }}
    .modal {{ max-width: 460px; width: 100%; border-radius: 8px; border: 1px solid var(--line); background: var(--panel); padding: 22px; box-shadow: 0 24px 80px rgba(23,32,42,0.22); }}
    .modal h2 {{ margin: 0; font-size: 28px; }}
    .result-graphic {{ margin-top: 12px; font-size: 40px; line-height: 1.1; letter-spacing: 0; }}
    .result-graphic.red {{ color: #be123c; }}
    .result-graphic.gold {{ color: #b45309; }}
    .modal .value {{ font-size: 42px; color: var(--teal); }}
    .note {{ margin-top: 12px; color: var(--muted); font-size: 13px; line-height: 1.45; }}
    .source-note {{ margin-top: 24px; border-top: 1px solid var(--line); padding-top: 14px; color: var(--muted); font-size: 12px; line-height: 1.5; }}
    .model-grid, .world-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .highlight-tag {{ background: var(--teal); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 8px; letter-spacing: 0.5px; vertical-align: middle; }}
    @media (max-width: 760px) {{ .choices, .story, .actions, .path, .benchmark, .model-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-text">
        <h1>Can you manage MTPL risk under uncertainty?</h1>
        <p class="lede">Choose frequency and severity model types, then advance one year. The next insurance world is revealed after each recalculation across ten yearly decisions.</p>
        <a class="top-link" href="info.html">Understand assumptions behind &rarr;</a>
      </div>
      <div class="forecast-box">
        <span class="label">Next World Probability</span>
        <div class="pie-wrap" id="forecastPie"></div>
        <div class="pie-legend" id="forecastLegend"></div>
      </div>
    </section>

    <section class="section panel">
      <div class="choices">
        <div class="field">
          <label for="frequencyModelSelect">Frequency Model [F] <span class="highlight-tag">Choose Model</span></label>
          <select id="frequencyModelSelect"></select>
        </div>
        <div class="field">
          <label for="severityModelSelect">Severity Model [S] <span class="highlight-tag">Choose Model</span></label>
          <select id="severityModelSelect"></select>
        </div>
      </div>
      <div class="actions">
        <div class="advance-group">
          <button class="primary" id="advanceButton">Advance 1 Year</button>
          <button class="primary" id="advanceFiveButton">Advance 5 Years</button>
        </div>
        <button id="resetButton">Start Over</button>
      </div>
      <div class="calc-status" id="calcStatus" aria-live="polite">
        <div class="calc-bar"><span id="calcProgressBar"></span></div>
        <p class="note" id="calcStatusText">Recalculating frequency, severity, pure premium, and yearly transition path...</p>
      </div>
      <p class="note">The next world follows a hidden seeded stochastic scenario path and is revealed after each year completes. [F] and [S] models are retrained using a rolling 2-year window through the prior year. Root checkpoint: French Motor raw files are `data/raw/freMTPL2freq.csv` and `data/raw/freMTPL2sev.csv`.</p>
    </section>

    <section class="section story" id="storyCards"></section>

    <section class="section">
      <div class="path" id="pathGrid"></div>
    </section>

    <section class="section panel">
      <h2>RMSE Replay</h2>
      <div class="chart-wrap"><svg id="publicRmseChart" viewBox="0 0 960 280"></svg></div>
    </section>

    <section class="section panel">
      <h2>10-Year Benchmark</h2>
      <div class="benchmark" id="benchmarkCards"></div>
    </section>

    <section class="section panel">
      <h2>What the models mean</h2>
      <p class="note">Frequency and severity are trained separately for the selected target model. Year 1 uses one prior-year slice; Year 2 onward uses a rolling 2-year window, which rewards GLM in stable/good sequences and lets XGBoost shine in complex regimes.</p>
      <div class="model-grid" id="modelGrid"></div>
    </section>

    <section class="section panel">
      <h2>What the worlds mean</h2>
      <p class="note">Worlds are alternate insurance regimes. The public scenario hides the next world until the yearly recalculation completes.</p>
      <div class="world-grid" id="worldGrid"></div>
    </section>

    <footer class="source-note">
      Source note: exact source is the public French Motor third-party liability raw data files `data/raw/freMTPL2freq.csv` and `data/raw/freMTPL2sev.csv`, then simulated on top as a finite insurance futures lattice. The worlds, model choices, yearly paths, RMSE replay, benchmark totals, and transition graph are synthetic simulation layers designed for product demonstration, not external market forecasts.
    </footer>
  </main>

  <div class="modal-backdrop" id="resultModal" role="dialog" aria-modal="true" aria-labelledby="resultTitle">
    <div class="modal">
      <h2 id="resultTitle">Run Complete</h2>
      <div class="result-graphic" id="resultGraphic" aria-label="Result rating"></div>
      <div class="value" id="resultPercentile"></div>
      <p class="note" id="resultCopy"></p>
      <button class="primary" id="closeResultButton">Close</button>
    </div>
  </div>

  <script>
    const data = {embedded};
    const manifest = data.manifest;
    const checkpoints = data.checkpoints.map((row) => ({{
      ...row,
      year: Number(row.year),
      training_window_years: Number(row.training_window_years),
      training_data_start_year: Number(row.training_data_start_year),
      training_data_end_year: Number(row.training_data_end_year),
      frequency_rmse: Number(row.frequency_rmse),
      severity_rmse: Number(row.severity_rmse),
      pure_premium_rmse: Number(row.pure_premium_rmse),
      net_strategic_value: Number(row.net_strategic_value),
    }}));
    const transitions = data.transitions.map((row) => ({{
      ...row,
      boundary_year: Number(row.boundary_year),
      target_year: Number(row.target_year),
      pure_premium_rmse_delta: Number(row.pure_premium_rmse_delta),
      target_training_window_years: Number(row.target_training_window_years),
      target_training_data_start_year: Number(row.target_training_data_start_year),
      target_training_data_end_year: Number(row.target_training_data_end_year),
      target_frequency_rmse: Number(row.target_frequency_rmse),
      target_severity_rmse: Number(row.target_severity_rmse),
      target_pure_premium_rmse: Number(row.target_pure_premium_rmse),
      target_net_strategic_value: Number(row.target_net_strategic_value),
    }}));
    const checkpointById = new Map(checkpoints.map((row) => [row.checkpoint_id, row]));
    const initialCheckpoint = checkpointById.get(manifest.initial_checkpoint_id);
    const worlds = manifest.world_catalog;
    const models = manifest.model_catalog;
    const publicWorldPath = manifest.public_world_path || Array.from({{ length: manifest.years }}, () => initialCheckpoint?.world_id || "stable_baseline");
    const pricingExpertBenchmarkDatabase = Object.freeze([
      0.502, 0.518, 0.521, 0.523, 0.526, 0.527, 0.535, 0.544, 0.557, 0.579,
      0.582, 0.588, 0.59, 0.602, 0.603, 0.615, 0.619, 0.621, 0.623, 0.626,
      0.63, 0.639, 0.642, 0.645, 0.646, 0.66, 0.665, 0.687, 0.695, 0.7,
      0.707, 0.729, 0.74, 0.745, 0.746, 0.747, 0.747, 0.755, 0.768, 0.78,
      0.783, 0.789, 0.795, 0.8, 0.802, 0.81, 0.816, 0.826, 0.83, 0.851,
      0.853, 0.853, 0.857, 0.863, 0.877, 0.878, 0.885, 0.905, 0.906, 0.912,
      0.927, 0.927, 0.935, 0.946, 0.987, 1.003, 1.003, 1.017, 1.02, 1.03,
      1.042, 1.081, 1.089, 1.09, 1.094, 1.107, 1.112, 1.118, 1.126, 1.137,
      1.159, 1.165, 1.174, 1.181, 1.182, 1.183, 1.183, 1.192, 1.197, 1.201,
      1.226, 1.238, 1.247, 1.263, 1.263, 1.282, 1.294, 1.307, 1.363, 1.405
    ]);
    const pricingExpertYearlyBenchmarkDatabase = Object.freeze(
      Array.from({{ length: manifest.years }}, (_, index) =>
        pricingExpertBenchmarkDatabase.map((value) => Number((value * ((index + 1) / manifest.years)).toFixed(3)))
      )
    );
    const state = {{
      currentCheckpointId: null,
      firstCheckpointId: null,
      chosenTransitions: [],
      selectedFrequencyModel: initialCheckpoint?.frequency_model_family || models[0]?.model_family || "",
      selectedSeverityModel: initialCheckpoint?.severity_model_family || models[0]?.model_family || "",
      pendingWorld: null,
      pendingFrequencyModel: null,
      pendingSeverityModel: null,
      lastShownResultYear: 0,
      recalculating: false,
      recalculationTimer: null
    }};

    function title(value) {{
      return String(value || "").replaceAll("_", " ").replace(/\\b\\w/g, (letter) => letter.toUpperCase());
    }}
    function number(value, digits = 1) {{
      return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : "-";
    }}
    function checkpointFromTransition(row) {{
      const base = checkpointById.get(row.to_checkpoint_id);
      if (!base) return null;
      return {{
        ...base,
        training_window_years: row.target_training_window_years || base.training_window_years,
        training_window_label: row.target_training_window_label || base.training_window_label,
        training_data_start_year: Number.isFinite(row.target_training_data_start_year) ? row.target_training_data_start_year : base.training_data_start_year,
        training_data_end_year: Number.isFinite(row.target_training_data_end_year) ? row.target_training_data_end_year : base.training_data_end_year,
        frequency_rmse: Number.isFinite(row.target_frequency_rmse) ? row.target_frequency_rmse : base.frequency_rmse,
        severity_rmse: Number.isFinite(row.target_severity_rmse) ? row.target_severity_rmse : base.severity_rmse,
        pure_premium_rmse: Number.isFinite(row.target_pure_premium_rmse) ? row.target_pure_premium_rmse : base.pure_premium_rmse,
        net_strategic_value: Number.isFinite(row.target_net_strategic_value) ? row.target_net_strategic_value : base.net_strategic_value,
        game_effect_summary: row.game_effect_summary || base.game_effect_summary,
      }};
    }}
    function currentCheckpoint() {{
      if (!state.currentCheckpointId) return null;
      const latestTransition = state.chosenTransitions[state.chosenTransitions.length - 1];
      if (latestTransition && latestTransition.to_checkpoint_id === state.currentCheckpointId) {{
        return checkpointFromTransition(latestTransition);
      }}
      return checkpointById.get(state.currentCheckpointId);
    }}
    function publicWorldForYear(year) {{
      return publicWorldPath[Math.max(0, Math.min(publicWorldPath.length - 1, year - 1))] || initialCheckpoint?.world_id || "stable_baseline";
    }}
    function worldLabel(worldId) {{
      return worlds.find((world) => world.world_id === worldId)?.label || title(worldId);
    }}
    function modelLabel(modelId) {{
      return models.find((model) => model.model_family === modelId)?.label || title(modelId);
    }}
    function modelNarrative(modelId) {{
      return models.find((model) => model.model_family === modelId)?.narrative || "Selected for the current recalculation";
    }}
    function worldNarrative(worldId) {{
      return worlds.find((world) => world.world_id === worldId)?.narrative || "Revealed for the current recalculation";
    }}
    function totalRmse() {{
      return pathCheckpoints().reduce((total, row) => total + Number(row.pure_premium_rmse || 0), 0);
    }}
    function percentileAgainst(total, database) {{
      if (!database.length) return 0;
      const betterThan = database.filter((expertTotal) => total < expertTotal).length;
      return Math.round((betterThan / database.length) * 100);
    }}
    function runningRmseUntil(year) {{
      return pathCheckpoints()
        .filter((row) => row.year <= year)
        .reduce((total, row) => total + Number(row.pure_premium_rmse || 0), 0);
    }}
    function runningPercentileForYear(year) {{
      const database = pricingExpertYearlyBenchmarkDatabase[Math.max(0, Math.min(pricingExpertYearlyBenchmarkDatabase.length - 1, year - 1))] || [];
      return percentileAgainst(runningRmseUntil(year), database);
    }}
    function completedRunPercentile() {{
      const rows = pathCheckpoints();
      if (rows.length < manifest.years) return null;
      return percentileAgainst(totalRmse(), pricingExpertBenchmarkDatabase);
    }}
    function resultGraphic(percentile) {{
      if (percentile >= 90) return {{ text: "★★★★★", tone: "gold", label: "Five stars" }};
      if (percentile >= 75) return {{ text: "★★★★", tone: "gold", label: "Four stars" }};
      if (percentile >= 50) return {{ text: "☺", tone: "", label: "Smiley face" }};
      if (percentile >= 30) return {{ text: "😐", tone: "", label: "Neutral smiley" }};
      if (percentile >= 20) return {{ text: "★", tone: "gold", label: "One star" }};
      if (percentile >= 10) return {{ text: "😓", tone: "", label: "Sad sweaty smiley" }};
      return {{ text: "😡", tone: "red", label: "Red face smiley" }};
    }}
    function selectedYearOneCheckpoint(targetWorld, targetFrequencyModel, targetSeverityModel) {{
      return checkpoints.find((row) =>
        row.year === 1 &&
        row.world_id === targetWorld &&
        row.frequency_model_family === targetFrequencyModel &&
        row.severity_model_family === targetSeverityModel
      ) || null;
    }}
    function pathCheckpoints() {{
      if (!currentCheckpoint()) return [];
      const first = checkpointById.get(state.firstCheckpointId || state.currentCheckpointId);
      return [first, ...state.chosenTransitions.map((item) => checkpointFromTransition(item))].filter(Boolean);
    }}
    function transitionFor(targetWorld, targetFrequencyModel, targetSeverityModel) {{
      const current = currentCheckpoint();
      if (!current) return null;
      return transitions.find((row) =>
        row.from_checkpoint_id === current.checkpoint_id &&
        row.target_world_id === targetWorld &&
        row.target_frequency_model_family === targetFrequencyModel &&
        row.target_severity_model_family === targetSeverityModel
      );
    }}
    function setModelOptions(select, selectedModel) {{
      if (select.options.length !== models.length) {{
        select.innerHTML = models.map((model) => `<option value="${{model.model_family}}">${{model.label}}</option>`).join("");
      }}
      select.value = selectedModel;
    }}
    function populateControls() {{
      const current = currentCheckpoint() || initialCheckpoint;
      const frequencyModelSelect = document.getElementById("frequencyModelSelect");
      const severityModelSelect = document.getElementById("severityModelSelect");
      const displayFrequencyModel = state.recalculating
        ? (state.pendingFrequencyModel || state.selectedFrequencyModel || current.frequency_model_family)
        : (state.selectedFrequencyModel || current.frequency_model_family);
      const displaySeverityModel = state.recalculating
        ? (state.pendingSeverityModel || state.selectedSeverityModel || current.severity_model_family)
        : (state.selectedSeverityModel || current.severity_model_family);
      setModelOptions(frequencyModelSelect, displayFrequencyModel);
      setModelOptions(severityModelSelect, displaySeverityModel);
      document.getElementById("advanceButton").disabled = state.recalculating || Boolean(currentCheckpoint() && current.year >= manifest.years);
      document.getElementById("resetButton").disabled = state.recalculating;
      frequencyModelSelect.disabled = state.recalculating;
      severityModelSelect.disabled = state.recalculating;
    }}
    function setRecalculationStatus(active, targetYear = null, progress = 0, message = null, targetWorld = null) {{
      state.recalculating = active;
      const status = document.getElementById("calcStatus");
      status.classList.toggle("active", active);
      document.getElementById("calcProgressBar").style.width = `${{Math.max(0, Math.min(100, progress))}}%`;
      const worldPrefix = active && targetWorld ? `World revealed: ${{worldLabel(targetWorld)}}. ` : "";
      document.getElementById("calcStatusText").textContent = active
        ? (worldPrefix + (message || `Recalculating year ${{targetYear}}: fitting frequency, severity, pure premium, and transition path...`))
        : "Recalculating frequency, severity, pure premium, and yearly transition path...";
      populateControls();
      renderStory();
    }}
    function realisticRecalculation(targetYear, targetWorld, onDone) {{
      const normalish = (Math.random() + Math.random() + Math.random() + Math.random() - 2) / 2;
      const totalMs = Math.round(15000 + (normalish * 3000));
      const stages = [
        [0.08, "Connecting to back end simulation service..."],
        [0.23, "Loading rolling training window..."],
        [0.41, "Refitting frequency model on rolling exposure window..."],
        [0.58, "Refitting severity model and inflation carry-through..."],
        [0.74, "Repricing pure premium by target world..."],
        [0.89, "Scoring yearly transition path and benchmark impact..."],
        [1.00, "Finalizing year checkpoint..."],
      ];
      const startedAt = Date.now();
      let displayedProgress = 0;
      function tick() {{
        const elapsed = Date.now() - startedAt;
        const rawProgress = Math.min(100, Math.round((elapsed / totalMs) * 100));
        const jitter = rawProgress < 96 ? Math.max(0, Math.min(96, rawProgress + Math.round(Math.random() * 3))) : rawProgress;
        displayedProgress = Math.max(displayedProgress, jitter);
        const stage = stages.find((item) => elapsed / totalMs <= item[0]) || stages[stages.length - 1];
        setRecalculationStatus(true, targetYear, displayedProgress, `Year ${{targetYear}}: ${{stage[1]}}`, targetWorld);
        if (elapsed >= totalMs) {{
          setRecalculationStatus(true, targetYear, 100, `Year ${{targetYear}}: Finalizing year checkpoint...`, targetWorld);
          window.setTimeout(onDone, 180);
          return;
        }}
        state.recalculationTimer = window.setTimeout(tick, 120 + Math.round(Math.random() * 120));
      }}
      tick();
    }}
    function renderStory() {{
      const current = currentCheckpoint();
      if (!current) {{
        const pending = state.recalculating && state.pendingFrequencyModel && state.pendingSeverityModel;
        const cards = [
          ["Time", "0", "No simulated year has elapsed"],
          ["World", pending ? worldLabel(state.pendingWorld) : "Hidden", pending ? "Revealed for the current recalculation" : "Revealed after the first yearly recalculation"],
          ["Frequency Model", pending ? modelLabel(state.pendingFrequencyModel) : title(initialCheckpoint?.frequency_model_family), pending ? modelNarrative(state.pendingFrequencyModel) : "Initial target for year 1"],
          ["Severity Model", pending ? modelLabel(state.pendingSeverityModel) : title(initialCheckpoint?.severity_model_family), pending ? modelNarrative(state.pendingSeverityModel) : "Initial target for year 1"],
          ["Training Window", "1 year", pending ? "Rolling-window effect is scored after recalculation" : "Year 1 uses one prior-year slice"],
          ["Pure Premium RMSE", "-", "Available after the first advance"],
          ["Frequency RMSE", "-", "Available after the first advance"],
          ["Severity RMSE", "-", "Available after the first advance"],
        ];
        document.getElementById("storyCards").innerHTML = cards.map(([label, value, sub]) => `
          <div class="card"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
        `).join("");
        return;
      }}
      if (state.recalculating && state.pendingFrequencyModel && state.pendingSeverityModel) {{
        const targetYear = current.year + 1;
        const cards = [
          ["Year", `${{targetYear}} of ${{manifest.years}}`, "Recalculation in progress"],
          ["World", worldLabel(state.pendingWorld), worldNarrative(state.pendingWorld)],
          ["Frequency Model", modelLabel(state.pendingFrequencyModel), modelNarrative(state.pendingFrequencyModel)],
          ["Severity Model", modelLabel(state.pendingSeverityModel), modelNarrative(state.pendingSeverityModel)],
          ["Training Window", targetYear === 1 ? "1 year" : "2 years", targetYear === 1 ? "Initial prior-year slice" : "Rolling 2-year window"],
          ["Pure Premium RMSE", "-", "Finalizing current run"],
          ["Frequency RMSE", "-", "Finalizing current run"],
          ["Severity RMSE", "-", "Finalizing current run"],
        ];
        document.getElementById("storyCards").innerHTML = cards.map(([label, value, sub]) => `
          <div class="card"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
        `).join("");
        return;
      }}
      const cards = [
        ["Year", `${{current.year}} of ${{manifest.years}}`, "Current checkpoint"],
        ["World", title(current.world_id), current.world_narrative],
        ["Frequency Model", title(current.frequency_model_family), current.frequency_model_narrative],
        ["Severity Model", title(current.severity_model_family), current.severity_model_narrative],
        ["Training Window", current.training_window_label || "-", current.game_effect_summary || "Rolling window effect"],
        ["Pure Premium RMSE", number(current.pure_premium_rmse, 3), "Lower is better"],
        ["Frequency RMSE", number(current.frequency_rmse, 3), "Claim count model error"],
        ["Severity RMSE", number(current.severity_rmse, 3), "Claim size model error"],
      ];
      document.getElementById("storyCards").innerHTML = cards.map(([label, value, sub]) => `
        <div class="card"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
      `).join("");
    }}
    function renderPath() {{
      const rows = pathCheckpoints();
      document.getElementById("pathGrid").innerHTML = Array.from({{ length: manifest.years }}, (_, index) => {{
        const year = index + 1;
        const row = rows.find((item) => item.year === year);
        const active = currentCheckpoint()?.year === year ? " active" : "";
        const percentile = row ? runningPercentileForYear(year) : null;
        return `<div class="year${{active}}"><div class="label">Year ${{year}}</div><div class="value">${{row ? title(row.world_id) : "Unrealised"}}</div><div class="sub">${{row ? "F: " + title(row.frequency_model_family) + " | S: " + title(row.severity_model_family) + " | RMSE " + number(row.pure_premium_rmse, 3) + " | Better than " + percentile + "% of experts" : "Choose as you advance"}}</div></div>`;
      }}).join("");
    }}
    function drawChart() {{
      const rows = pathCheckpoints();
      const svg = document.getElementById("publicRmseChart");
      const width = 960;
      const height = 280;
      const pad = {{ left: 46, right: 18, top: 18, bottom: 34 }};
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
      if (!rows.length) {{
        svg.innerHTML = `<text x="50%" y="50%" text-anchor="middle" fill="#5f6f7a">Time 0: advance to create the first yearly checkpoint</text>`;
        return;
      }}
      const values = rows.map((row) => row.pure_premium_rmse);
      const minY = Math.min(0, ...values);
      const maxY = Math.max(0.6, ...values);
      const x = (year) => pad.left + ((year - 1) / Math.max(1, manifest.years - 1)) * (width - pad.left - pad.right);
      const y = (value) => pad.top + ((maxY - value) / Math.max(1, maxY - minY)) * (height - pad.top - pad.bottom);
      const path = rows.map((row, index) => `${{index === 0 ? "M" : "L"}} ${{x(row.year)}} ${{y(row.pure_premium_rmse)}}`).join(" ");
      const points = rows.map((row) => `<circle cx="${{x(row.year)}}" cy="${{y(row.pure_premium_rmse)}}" r="5" fill="#0f766e"></circle>`).join("");
      const labels = Array.from({{ length: manifest.years }}, (_, index) => {{
        const year = index + 1;
        return `<text x="${{x(year)}}" y="${{height - 10}}" text-anchor="middle" fill="#5f6f7a" font-size="12">Y${{year}}</text>`;
      }}).join("");
      const valueLabels = rows.map((row) => `
        <text x="${{x(row.year)}}" y="${{y(row.pure_premium_rmse) - 12}}" text-anchor="middle" fill="#0f766e" font-size="11" font-weight="700">${{number(row.pure_premium_rmse, 3)}}</text>
      `).join("");
      svg.innerHTML = `
        <rect width="${{width}}" height="${{height}}" fill="transparent"></rect>
        <line x1="${{pad.left}}" y1="${{height - pad.bottom}}" x2="${{width - pad.right}}" y2="${{height - pad.bottom}}" stroke="rgba(23,32,42,0.2)"></line>
        <line x1="${{pad.left}}" y1="${{pad.top}}" x2="${{pad.left}}" y2="${{height - pad.bottom}}" stroke="rgba(23,32,42,0.2)"></line>
        ${{labels}}
        <path d="${{path}}" fill="none" stroke="#0f766e" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
        ${{points}}
        ${{valueLabels}}
      `;
    }}
    function renderBenchmark() {{
      const rows = pathCheckpoints();
      const total = totalRmse();
      const latest = rows[rows.length - 1] || null;
      const percentile = latest ? runningPercentileForYear(latest.year) : null;
      const replayCheckpointCount = manifest.public_checkpoint_path?.length || 0;
      const replayTransitionCount = manifest.public_transition_path?.length || 0;
      const cards = [
        ["10-Year RMSE Total", rows.length ? number(total, 3) : "-", `${{rows.length}} of ${{manifest.years}} years completed`],
        ["Benchmark Database", pricingExpertBenchmarkDatabase.length, "Simulated expert scenarios"],
        ["Replay Chain", `${{replayCheckpointCount}} / ${{replayTransitionCount}}`, "checkpoint ids / transition ids"],
        ["Current Rank", percentile === null ? "-" : `Better than ${{percentile}}%`, rows.length ? `After year ${{latest.year}}` : "Lower total RMSE ranks higher"],
      ];
      document.getElementById("benchmarkCards").innerHTML = cards.map(([label, value, sub]) => `
        <div class="card"><div class="label">${{label}}</div><div class="value">${{value}}</div><div class="sub">${{sub}}</div></div>
      `).join("");
    }}
    function showResultModalForLatestYear() {{
      const rows = pathCheckpoints();
      const latest = rows[rows.length - 1] || null;
      if (!latest || latest.year <= state.lastShownResultYear) return;
      state.lastShownResultYear = latest.year;
      const percentile = latest.year >= manifest.years ? completedRunPercentile() : runningPercentileForYear(latest.year);
      if (percentile === null) return;
      const graphic = resultGraphic(percentile);
      const graphicNode = document.getElementById("resultGraphic");
      graphicNode.textContent = graphic.text;
      graphicNode.className = `result-graphic ${{graphic.tone}}`;
      graphicNode.setAttribute("aria-label", graphic.label);
      document.getElementById("resultPercentile").textContent = `${{percentile}}%`;
      document.getElementById("resultTitle").textContent = latest.year >= manifest.years ? "Run Complete" : `Year ${{latest.year}} Complete`;
      document.getElementById("resultCopy").textContent = latest.year >= manifest.years
        ? `World revealed: ${{title(latest.world_id)}}. You did better than ${{percentile}}% of pricing experts. Your 10-year RMSE total was ${{number(totalRmse(), 3)}}.`
        : `World revealed: ${{title(latest.world_id)}}. After year ${{latest.year}}, you did better than ${{percentile}}% of pricing experts. Your running RMSE total is ${{number(runningRmseUntil(latest.year), 3)}}.`;
      document.getElementById("resultModal").classList.add("open");
    }}
    function closeResultModal() {{
      document.getElementById("resultModal").classList.remove("open");
    }}
    function updateForecast() {{
      const current = currentCheckpoint();
      const currentWorld = current?.world_id || "stable_baseline";
      const currentIndex = worlds.findIndex(w => w.world_id === currentWorld);
      
      const stay = 0.58;
      const forward1 = 0.24;
      const back1 = 0.10;
      const forward2 = 0.08;
      
      // Map probabilities to world indices
      const outcomes = [
        {{ index: currentIndex, value: stay, label: worlds[currentIndex].label, color: "#0f766e" }},
        {{ index: (currentIndex + 1) % worlds.length, value: forward1, label: worlds[(currentIndex + 1) % worlds.length].label, color: "#1d4ed8" }},
        {{ index: (currentIndex - 1 + worlds.length) % worlds.length, value: back1, label: worlds[(currentIndex - 1 + worlds.length) % worlds.length].label, color: "#be123c" }},
        {{ index: (currentIndex + 2) % worlds.length, value: forward2, label: worlds[(currentIndex + 2) % worlds.length].label, color: "#b45309" }}
      ];
      
      // Group by world index
      const grouped = {{}};
      outcomes.forEach(o => {{
        if (!grouped[o.index]) {{
          grouped[o.index] = {{ value: 0, label: worlds[o.index].label, color: o.color }};
        }}
        grouped[o.index].value += o.value;
      }});
      
      const slices = Object.values(grouped).filter(s => s.value > 0);
      
      let cumulativePercent = 0;
      const getCoordinatesForPercent = (percent) => {{
        const x = Math.cos(2 * Math.PI * percent);
        const y = Math.sin(2 * Math.PI * percent);
        return [x, y];
      }};
      
      let svgContent = `<svg viewBox="-1 -1 2 2" style="transform: rotate(-90deg); border-radius: 50%; background: #f1f5f9;">`;
      slices.forEach(slice => {{
        const [startX, startY] = getCoordinatesForPercent(cumulativePercent);
        cumulativePercent += slice.value;
        const [endX, endY] = getCoordinatesForPercent(cumulativePercent);
        const largeArcFlag = slice.value > 0.5 ? 1 : 0;
        const pathData = `M ${{startX}} ${{startY}} A 1 1 0 ${{largeArcFlag}} 1 ${{endX}} ${{endY}} L 0 0`;
        svgContent += `<path d="${{pathData}}" fill="${{slice.color}}" />`;
      }});
      svgContent += `</svg>`;
      
      document.getElementById("forecastPie").innerHTML = svgContent;
      document.getElementById("forecastLegend").innerHTML = slices.map(s => `
        <div class="legend-item">
          <div class="legend-dot" style="background: ${{s.color}}"></div>
          <span>${{s.label}}: ${{Math.round(s.value * 100)}}%</span>
        </div>
      `).join("");
    }}
    function renderModels() {{
      document.getElementById("modelGrid").innerHTML = models.map((model) => `
        <div class="card"><div class="label">${{model.label}}</div><div class="value">${{title(model.model_family)}}</div><div class="sub">${{model.model_info}}</div></div>
      `).join("");
    }}
    function renderWorlds() {{
      document.getElementById("worldGrid").innerHTML = worlds.map((world) => `
        <div class="card"><div class="label">${{world.label}}</div><div class="value">${{title(world.world_id)}}</div><div class="sub">${{world.narrative}}</div></div>
      `).join("");
    }}
    function renderAll() {{ populateControls(); renderStory(); renderPath(); drawChart(); renderBenchmark(); renderModels(); renderWorlds(); updateForecast(); }}
    function advanceStep(showResult = true, onDone = null) {{
      if (state.recalculating) return;
      const targetFrequencyModel = document.getElementById("frequencyModelSelect").value;
      const targetSeverityModel = document.getElementById("severityModelSelect").value;
      const targetYear = currentCheckpoint() ? currentCheckpoint().year + 1 : 1;
      if (targetYear > manifest.years) {{
        return;
      }}
      const targetWorld = publicWorldForYear(targetYear);
      state.selectedFrequencyModel = targetFrequencyModel;
      state.selectedSeverityModel = targetSeverityModel;
      state.pendingWorld = targetWorld;
      state.pendingFrequencyModel = targetFrequencyModel;
      state.pendingSeverityModel = targetSeverityModel;
      setRecalculationStatus(true, targetYear, 0, null, targetWorld);
      realisticRecalculation(targetYear, targetWorld, () => {{
        completeAdvance(targetWorld, targetFrequencyModel, targetSeverityModel, showResult);
        state.pendingWorld = null;
        state.pendingFrequencyModel = null;
        state.pendingSeverityModel = null;
        setRecalculationStatus(false);
        if (typeof onDone === "function") {{
          onDone();
        }}
      }});
    }}
    function advance() {{
      advanceStep(true);
    }}
    function advanceFiveYears() {{
      const stepsRemaining = Math.max(0, manifest.years - (currentCheckpoint()?.year || 0));
      const stepsToRun = Math.min(5, stepsRemaining);
      if (!stepsToRun) {{
        return;
      }}
      const runStep = (remaining) => {{
        advanceStep(remaining === 1, () => {{
          if (remaining > 1) {{
            runStep(remaining - 1);
          }}
        }});
      }};
      runStep(stepsToRun);
    }}
    function completeAdvance(targetWorld, targetFrequencyModel, targetSeverityModel, showResult = true) {{
      if (!currentCheckpoint()) {{
        const firstCheckpoint = selectedYearOneCheckpoint(
          targetWorld,
          targetFrequencyModel,
          targetSeverityModel
        );
        if (!firstCheckpoint) return;
        state.currentCheckpointId = firstCheckpoint.checkpoint_id;
        state.firstCheckpointId = firstCheckpoint.checkpoint_id;
        renderAll();
        if (showResult) {{
          showResultModalForLatestYear();
        }}
        return;
      }}
      const transition = transitionFor(
        targetWorld,
        targetFrequencyModel,
        targetSeverityModel
      );
      if (!transition) return;
      state.chosenTransitions.push(transition);
      state.currentCheckpointId = transition.to_checkpoint_id;
      renderAll();
      if (showResult) {{
        showResultModalForLatestYear();
      }}
    }}
    function reset() {{
      state.currentCheckpointId = null;
      state.firstCheckpointId = null;
      state.chosenTransitions = [];
      state.selectedFrequencyModel = initialCheckpoint?.frequency_model_family || models[0]?.model_family || "";
      state.selectedSeverityModel = initialCheckpoint?.severity_model_family || models[0]?.model_family || "";
      state.pendingWorld = null;
      state.pendingFrequencyModel = null;
      state.pendingSeverityModel = null;
      state.lastShownResultYear = 0;
      if (state.recalculationTimer) {{
        window.clearTimeout(state.recalculationTimer);
        state.recalculationTimer = null;
      }}
      closeResultModal();
      renderAll();
    }}
    document.getElementById("advanceButton").addEventListener("click", advance);
    document.getElementById("advanceFiveButton").addEventListener("click", advanceFiveYears);
    document.getElementById("resetButton").addEventListener("click", reset);
    document.getElementById("frequencyModelSelect").addEventListener("change", (event) => {{ state.selectedFrequencyModel = event.target.value; }});
    document.getElementById("severityModelSelect").addEventListener("change", (event) => {{ state.selectedSeverityModel = event.target.value; }});
    document.getElementById("closeResultButton").addEventListener("click", closeResultModal);
    renderAll();
  </script>
</body>
</html>
"""



def build_example_a_info_html(data: dict[str, Any]) -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Example A | Simulation & Risk Design</title>
  <style>
    :root {
      --ink: #18212b;
      --muted: #64707d;
      --paper: #f5f0e8;
      --panel: #fffaf1;
      --line: rgba(24, 33, 43, 0.14);
      --teal: #0f766e;
      --blue: #1d4ed8;
      --amber: #b45309;
      --red: #be123c;
      --green: #4d7c0f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, system-ui, -apple-system, sans-serif;
      background: var(--paper);
      color: var(--ink);
      line-height: 1.6;
    }
    .shell { max-width: 1000px; margin: 0 auto; padding: 40px 20px 80px; }
    header { margin-bottom: 40px; }
    h1 { font-family: Georgia, serif; font-size: 48px; margin: 0 0 10px; line-height: 1.1; }
    .subtitle { font-size: 20px; color: var(--muted); max-width: 700px; }
    .nav-links { margin-top: 20px; display: flex; gap: 20px; font-weight: 700; }
    .nav-links a { color: var(--teal); text-decoration: none; }
    .section { margin-top: 60px; }
    h2 { font-family: Georgia, serif; font-size: 32px; border-bottom: 1px solid var(--line); padding-bottom: 10px; margin-bottom: 30px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 24px; }
    .card h3 { margin-top: 0; color: var(--teal); }
    .matrix-wrap { overflow-x: auto; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px; text-align: center; border: 1px solid var(--line); }
    th { background: rgba(15, 118, 110, 0.05); color: var(--muted); font-size: 11px; text-transform: uppercase; }
    .highlight { background: rgba(15, 118, 110, 0.1); font-weight: 700; color: var(--teal); }
    .formula { font-family: 'Courier New', Courier, monospace; background: #1e293b; color: #f8fafc; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; margin: 20px 0; }
    .graphic-box { height: 200px; background: white; border: 1px solid var(--line); border-radius: 8px; margin-top: 15px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
    .world-bubble { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; border: 2px solid var(--teal); background: white; z-index: 2; }
    .arrow { position: absolute; height: 2px; background: var(--teal); opacity: 0.3; }
    .hint-box { background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 100%); color: white; padding: 30px; border-radius: 12px; margin-top: 40px; box-shadow: 0 10px 25px rgba(15, 118, 110, 0.2); }
    .hint-box h3 { margin-top: 0; color: white; }
    .tag { display: inline-block; padding: 4px 10px; border-radius: 999px; background: rgba(255,255,255,0.2); font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <h1>Simulation & Risk Design</h1>
      <p class="subtitle">An intuitive guide to the physics, gamification, and world-switching mechanics of Example A.</p>
      <div class="nav-links">
        <a href="public.html">&larr; Back to Public GUI</a>
      </div>
    </header>

    <section class="section">
      <h2>The Five Worlds</h2>
      <p>The simulation operates across five distinct insurance "regimes," each with its own physical parameters for claim frequency, severity, and volatility.</p>
      <div class="grid">
        <div class="card">
          <h3>W1: Stable Baseline</h3>
          <p>Mild drift and low stress. The "ideal" state where models perform predictably.</p>
          <div style="font-size: 12px; color: var(--muted);">Freq: 0.16 | Sev: 0.16 | Vol: 0.08</div>
        </div>
        <div class="card">
          <h3>W2: Good Years</h3>
          <p>Favorable environment with low claim frequency and severity. Simpler models thrive here.</p>
          <div style="font-size: 12px; color: var(--muted);">Freq: 0.07 | Sev: 0.08 | Vol: 0.05</div>
        </div>
        <div class="card">
          <h3>W3: Mobility Suppression</h3>
          <p>Shift in driving patterns (e.g., pandemic). High frequency stress with uneven patterns.</p>
          <div style="font-size: 12px; color: var(--muted);">Freq: 0.34 | Sev: 0.18 | Vol: 0.25</div>
        </div>
        <div class="card">
          <h3>W4: Recovery Inflation</h3>
          <p>Post-suppression demand plus elevated repair inflation. Severe pressure on pricing.</p>
          <div style="font-size: 12px; color: var(--muted);">Freq: 0.32 | Sev: 0.45 | Vol: 0.22</div>
        </div>
        <div class="card">
          <h3>W5: Self-Drive Revolution</h3>
          <p>High complexity and volatility. Only aggressive learners can keep up with the rapid shifts.</p>
          <div style="font-size: 12px; color: var(--muted);">Freq: 0.38 | Sev: 0.52 | Vol: 0.30</div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>World Transition Matrix</h2>
      <p>How the simulation moves between worlds. It follows a seeded Markov-chain rule where the next world is conditioned on the current state.</p>
      <div class="matrix-wrap">
        <table>
          <thead>
            <tr>
              <th>From / To</th>
              <th>Stay</th>
              <th>Forward 1</th>
              <th>Forward 2</th>
              <th>Backward 1</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>Probability</th>
              <td class="highlight">58%</td>
              <td>24%</td>
              <td>8%</td>
              <td>10%</td>
            </tr>
            <tr>
              <td colspan="5" style="font-size: 12px; color: var(--muted); padding: 20px;">
                <em>Note: Transitions are cyclic and loop back. For example, if at World 5, a "Forward 1" draw loops back to World 1. Likewise, a "Backward 1" from World 1 loops to World 5.</em>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>Risk Physics: The RMSE Formula</h2>
      <p>Performance is measured by <strong>Pure Premium RMSE</strong>. This is not the total claims cost, but rather the <em>pricing error</em> of your selected model combination.</p>
      <div class="formula">
frequency_rmse = base_error + (world.frequency_stress * 0.32) + (world.volatility * 0.10) - frequency_credit

severity_rmse = base_error + (world.severity_stress * 0.34) + (world.volatility * 0.08) - severity_credit

pure_premium_rmse = (frequency_rmse * 0.48) + (severity_rmse * 0.52)
      </div>
      <p>Lower RMSE is better. The "credit" depends on model adaptation and the size of the training window.</p>
    </section>

    <section class="section">
      <h2>Gamification: The 2-Year Window</h2>
      <p>The simulation uses a <strong>Rolling 2-Year Training Window</strong> (from Year 2 onwards). This creates a strategic trade-off:</p>
      <div class="grid">
        <div class="card">
          <h3>Stable/Good Repeats</h3>
          <p>Rewards <strong>Stability</strong> and <strong>Generalization</strong>. Simple models like GLM often outperform XGBoost here because they don't overfit the short history.</p>
        </div>
        <div class="card">
          <h3>World Shifts / Jumps</h3>
          <p>Rewards <strong>Complexity Skill</strong> and <strong>Adaptation</strong>. This is where XGBoost shines, as it can capture non-linear patterns that simpler models miss.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="hint-box">
        <div class="tag">Coming Soon</div>
        <h3>Dynamic Expectation Strategy</h3>
        <p>We are working on a new analytical solution: an observation-based dynamic strategy that aims for <strong>maximum expectation</strong> (RMSE minimizing).</p>
        <p style="opacity: 0.9; font-size: 15px;">This strategy will use historical world observations to dynamically adjust frequency and severity weights in real-time. Stay tuned for the next update.</p>
      </div>
    </section>

    <footer style="margin-top: 80px; padding-top: 20px; border-top: 1px solid var(--line); font-size: 12px; color: var(--muted);">
      Source: French Motor Third-Party Liability Simulation Lattice. For demonstration purposes only.
    </footer>
  </div>
</body>
</html>
"""


def build_example_a_dashboard(artifact_dir: str | Path, output_dir: str | Path | None = None) -> Path:
    artifact_path = Path(artifact_dir)
    target_dir = Path(output_dir) if output_dir is not None else artifact_path
    target_dir.mkdir(parents=True, exist_ok=True)
    data = load_example_a_dashboard_data(artifact_path)
    html = build_example_a_dashboard_html(data)
    output_path = target_dir / "admin.html"
    output_path.write_text(html, encoding="utf-8")
    public_html = build_example_a_public_html(data)
    (target_dir / "index.html").write_text(public_html, encoding="utf-8")
    info_html = build_example_a_info_html(data)
    (target_dir / "info.html").write_text(info_html, encoding="utf-8")
    return output_path
