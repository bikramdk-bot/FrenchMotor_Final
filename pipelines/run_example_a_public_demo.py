from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.example_a_public_demo import DEFAULT_SEED, DEFAULT_VERSION, build_example_a_artifacts
from src.example_a_public_demo_dashboard import build_example_a_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Example A small public demo lattice artifacts.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "reports" / "published" / "latest" / "example_a_public_demo"),
    )
    args = parser.parse_args()

    result = build_example_a_artifacts(args.output_dir, seed=args.seed, version=args.version)
    dashboard_path = build_example_a_dashboard(args.output_dir, args.output_dir)
    payload = {
        **result,
        "dashboard_path": str(dashboard_path),
        "artifact_label": "example_a_lattice",
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

