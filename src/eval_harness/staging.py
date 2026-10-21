from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

from eval_harness.manifest import Task

class StagingError(RuntimeError):
    """Raised when a submission cannot be safely staged."""

def stage_submission(
    task: Task,
    candidate_source: Path,
    runs_root: Path,
) -> Path:
    """Copy a task workspace and place the candidate source into it."""
    if not candidate_source.is_file():
        raise StagingError(
            f"Candidate source does not exist: {candidate_source}"
        )

    runs_root.mkdir(parents=True, exist_ok=True)

    run_directory = Path(
        tempfile.mkdtemp(
            prefix=f"{task.id}-",
            dir=runs_root,
        )
    )
    staged_workspace = run_directory / "workspace"

    shutil.copytree(task.workspace, staged_workspace)

    destination = (
        staged_workspace / task.submission_target
    ).resolve()

    try:
        destination.relative_to(staged_workspace.resolve())
    except ValueError as error:
        raise StagingError(
            "Submmission target escaped the staged workspace."
        ) from error

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate_source, destination)

    return staged_workspace