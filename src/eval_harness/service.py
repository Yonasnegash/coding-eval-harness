from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Protocol

from eval_harness.manifest import load_submissions, load_tasks
from eval_harness.rubric import score_maintainability
from eval_harness.runner import ExecutionResult
from eval_harness.staging import stage_submission


class TaskRunner(Protocol):
    def execute(
        self,
        workspace: Path,
        image: str,
        test_command: str,
    ) -> ExecutionResult:
        """Run a task's tests and return execution evidence."""


def evaluate(
    tasks_manifest: Path,
    submissions_manifest: Path,
    runner: TaskRunner,
    runs_root: Path,
) -> dict[str, object]:
    """Evaluate every task and return a report-ready result structure."""
    tasks = load_tasks(tasks_manifest)
    submissions = load_submissions(submissions_manifest)
    results: list[dict[str, object]] = []

    for task in tasks:
        if task.id not in submissions:
            results.append(
                {
                    "task_id": task.id,
                    "status": "not_submitted",
                    "score": {
                        "points_awarded": 0,
                        "possible_points": 100,
                    },
                    "evidence": {
                        "reason": "No submission was supplied for this task."
                    },
                }
            )
            continue

        staged_workspace = stage_submission(
            task,
            submissions[task.id],
            runs_root,
        )
        staged_source = staged_workspace / task.submission_target
        source_text = staged_source.read_text(encoding="utf-8")

        execution = runner.execute(
            workspace=staged_workspace,
            image=task.image,
            test_command=task.test_command,
        )
        maintainability = score_maintainability(
            source_text,
            task.maintainability,
        )
        correctness_points = 70 if execution.exit_code == 0 else 0

        results.append(
            {
                "task_id": task.id,
                "status": "passed" if execution.exit_code == 0 else "failed",
                "score": {
                    "points_awarded": (
                        correctness_points
                        + int(maintainability["points_awarded"])
                    ),
                    "possible_points": 100,
                    "correctness": {
                        "points_awarded": correctness_points,
                        "possible_points": 70,
                        "basis": (
                            "All task tests passed."
                            if correctness_points == 70
                            else "Task tests did not pass."
                        ),
                    },
                    "maintainability": maintainability,
                },
                "evidence": {
                    "source_sha256": sha256(
                        source_text.encode("utf-8")
                    ).hexdigest(),
                    "container_image": task.image,
                    "test_command": task.test_command,
                    "docker_command": execution.command,
                    "exit_code": execution.exit_code,
                    "duration_seconds": execution.duration_seconds,
                    "stdout": execution.stdout[-4000:],
                    "stderr": execution.stderr[-4000:],
                },
            }
        )

    points_awarded = sum(
        int(result["score"]["points_awarded"])
        for result in results
    )
    possible_points = sum(
        int(result["score"]["possible_points"])
        for result in results
    )

    return {
        "summary": {
            "tasks_evaluated": len(results),
            "points_awarded": points_awarded,
            "possible_points": possible_points,
        },
        "results": results,
    }