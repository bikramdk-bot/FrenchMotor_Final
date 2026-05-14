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


DEFAULT_PUBLISHED_DIR = PROJECT_ROOT / "reports" / "published" / "latest" / "example_a_public_demo"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the Example A published admin index.html and public.html pages.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=str,
        default=str(DEFAULT_PUBLISHED_DIR),
        help="Directory containing demo_manifest.json, yearly_checkpoints.csv, and yearly_transitions.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="HTML output directory. Defaults to the artifact directory.",
    )
    parser.add_argument(
        "--regenerate-artifacts",
        action="store_true",
        help="Regenerate the Example A CSV/JSON lattice artifacts before rendering HTML.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--version", type=str, default=DEFAULT_VERSION)
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    output_dir = Path(args.output_dir) if args.output_dir else artifact_dir

    artifact_result = None
    if args.regenerate_artifacts:
        artifact_result = build_example_a_artifacts(artifact_dir, seed=args.seed, version=args.version)

    index_path = build_example_a_dashboard(artifact_dir, output_dir)
    public_path = output_dir / "index.html"

    print(
        json.dumps(
            {
                "artifact_dir": str(artifact_dir),
                "output_dir": str(output_dir),
                "admin_html_path": str(index_path),
                "index_html_path": str(public_path),
                "regenerated_artifacts": bool(args.regenerate_artifacts),
                "artifact_result": artifact_result,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
