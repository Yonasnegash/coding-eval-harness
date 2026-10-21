from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import time


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    command: list[str]
    duration_seconds: float


class DockerRunner:
    """Run task tests inside a restricted Docker container."""

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        workspace: Path,
        image: str,
        test_command: str,
    ) -> ExecutionResult:
        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--memory",
            "512m",
            "--cpus",
            "1",
            "--pids-limit",
            "64",
            "-v",
            f"{workspace.resolve()}:/workspace:rw",
            "-w",
            "/workspace",
            image,
            "sh",
            "-lc",
            test_command,
        ]

        started_at = time.monotonic()

        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError:
            return ExecutionResult(
                exit_code=127,
                stdout="",
                stderr="Docker executable was not found.",
                command=command,
                duration_seconds=round(time.monotonic() - started_at, 3),
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                exit_code=124,
                stdout="",
                stderr="Task test execution timed out.",
                command=command,
                duration_seconds=round(time.monotonic() - started_at, 3),
            )

        return ExecutionResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            command=command,
            duration_seconds=round(time.monotonic() - started_at, 3),
        )