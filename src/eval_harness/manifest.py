from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


class ManifestError(ValueError):
    """Raised when a task manifest has an invalid structure."""


@dataclass(frozen=True)
class Task:
    id: str
    workspace: Path
    submission_target: str
    image: str
    test_command: str
    maintainability: dict[str, object]


def load_tasks(manifest_path: Path) -> list[Task]:
    """Load and validate task records from a JSONL manifest."""
    tasks: list[Task] = []
    seen_ids: set[str] = set()

    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip():
            continue

        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise ManifestError(
                f"Line {line_number}: invalid JSON."
            ) from error

        if not isinstance(record, dict):
            raise ManifestError(
                f"Line {line_number}: each task must be a JSON object."
            )

        required_fields = {
            "id",
            "workspace",
            "submission_target",
            "image",
            "test_command",
        }
        missing_fields = required_fields - record.keys()
        if missing_fields:
            raise ManifestError(
                f"Line {line_number}: missing fields {sorted(missing_fields)}."
            )

        task_id = str(record["id"])
        if not task_id:
            raise ManifestError(
                f"Line {line_number}: task id cannot be empty."
            )

        if task_id in seen_ids:
            raise ManifestError(f"Duplicate task id: {task_id}.")
        seen_ids.add(task_id)

        workspace = (
            manifest_path.parent / str(record["workspace"])
        ).resolve()
        if not workspace.is_dir():
            raise ManifestError(
                f"Task {task_id}: workspace does not exist: {workspace}"
            )

        submission_target = Path(str(record["submission_target"]))
        if submission_target.is_absolute() or ".." in submission_target.parts:
            raise ManifestError(
                f"Task {task_id}: submission_target must stay inside the workspace."
            )

        maintainability = record.get("maintainability", {})
        if not isinstance(maintainability, dict):
            raise ManifestError(
                f"Task {task_id}: maintainability must be a JSON object."
            )

        tasks.append(
            Task(
                id=task_id,
                workspace=workspace,
                submission_target=str(submission_target),
                image=str(record["image"]),
                test_command=str(record["test_command"]),
                maintainability=maintainability,
            )
        )

    return tasks