from __future__ import annotations

import argparse
from pathlib import Path

from eval_harness.report import write_report
from eval_harness.runner import DockerRunner
from eval_harness.service import evaluate


def main() -> int:
    """Run a coding evaluation from command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate coding submissions in constrained Docker containers."
        )
    )
    parser.add_argument(
        "--tasks",
        type=Path,
        required=True,
        help="Path to the task JSONL manifest.",
    )
    parser.add_argument(
        "--submissions",
        type=Path,
        required=True,
        help="Path to the submission JSONL manifest.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Destination for the JSON audit report.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path(".evaluation-runs"),
        help="Directory for isolated evaluation workspaces.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Maximum test runtime per task in seconds.",
    )

    arguments = parser.parse_args()

    report = evaluate(
        arguments.tasks,
        arguments.submissions,
        DockerRunner(timeout_seconds=arguments.timeout),
        arguments.runs_root,
    )
    write_report(report, arguments.report)

    print(f"Wrote audit report to {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())