import json
from pathlib import Path
import tempfile
import unittest

from eval_harness.runner import ExecutionResult
from eval_harness.service import evaluate


class PassingRunner:
    def execute(self, workspace, image, test_command):
        self.workspace = workspace
        return ExecutionResult(
            exit_code=0,
            stdout="2 tests passed",
            stderr="",
            command=["docker", "run", image],
            duration_seconds=0.15,
        )
    

class FailingRunner:
    def execute(self, workspace, image, test_command):
        self.workspace = workspace
        return ExecutionResult(
            exit_code=1,
            stdout="test_adds_values ... FAIL",
            stderr="AssertionError: expected 6, got 0",
            command=["docker", "run", image],
            duration_seconds=0.20,
        )


class EvaluationServiceTests(unittest.TestCase):
    @staticmethod
    def create_evaluation_manifests(root: Path) -> tuple[Path, Path]:
        tasks_dir = root / "tasks"
        tasks_dir.mkdir()

        workspace = root / "workspaces" / "sum-list"
        workspace.mkdir(parents=True)
        (workspace / "test_solution.py").write_text(
            "from solution import add\n",
            encoding="utf-8",
        )

        submissions_dir = root / "submissions"
        submissions_dir.mkdir()
        candidate = submissions_dir / "candidate.py"
        candidate.write_text(
            'def add(values):\n'
            '    """Return the sum of integer values."""\n'
            '    return sum(values)\n',
            encoding="utf-8",
        )

        tasks_manifest = tasks_dir / "tasks.jsonl"
        tasks_manifest.write_text(
            json.dumps(
                {
                    "id": "sum-list",
                    "workspace": "../workspaces/sum-list",
                    "submission_target": "solution.py",
                    "image": "python:3.12-alpine",
                    "test_command": "python -m unittest discover -v",
                    "maintainability": {"max_line_length": 100},
                }
            )
            + "\n",
            encoding="utf-8",
        )

        submissions_manifest = submissions_dir / "submissions.jsonl"
        submissions_manifest.write_text(
            json.dumps(
                {
                    "task_id": "sum-list",
                    "source_path": "candidate.py",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        return tasks_manifest, submissions_manifest

    def test_evaluates_staged_submission_and_returns_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            tasks_manifest, submissions_manifest = self.create_evaluation_manifests(root)

            runner = PassingRunner()
            report = evaluate(
                tasks_manifest,
                submissions_manifest,
                runner,
                root / "evaluation-runs",
            )

            result = report["results"][0]

            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["score"]["points_awarded"], 100)
            self.assertEqual(result["score"]["correctness"]["points_awarded"], 70)
            self.assertEqual(result["evidence"]["exit_code"], 0)
            self.assertTrue((runner.workspace / "solution.py").is_file())

    def test_records_failed_tests_with_auditable_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            tasks_manifest, submissions_manifest = self.create_evaluation_manifests(root)

            runner = FailingRunner()
            report = evaluate(
                tasks_manifest,
                submissions_manifest,
                runner,
                root / "evaluation-runs",
            )

            result = report["results"][0]

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["score"]["correctness"]["points_awarded"], 0)
            self.assertEqual(result["score"]["points_awarded"], 30)
            self.assertEqual(result["evidence"]["exit_code"], 1)
            self.assertIn("FAIL", result["evidence"]["stdout"])
            self.assertIn("AssertionError", result["evidence"]["stderr"])

    def test_reports_missing_submission_without_running_tests(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            tasks_manifest, submissions_manifest = (
                self.create_evaluation_manifests(root)
            )
            submissions_manifest.write_text("", encoding="utf-8")

            runner = PassingRunner()
            report = evaluate(
                tasks_manifest,
                submissions_manifest,
                runner,
                root / "evaluation-runs",
            )

            result = report["results"][0]

            self.assertEqual(result["status"], "not_submitted")
            self.assertEqual(result["score"]["points_awarded"], 0)
            self.assertEqual(result["score"]["possible_points"], 100)
            self.assertEqual(
                result["evidence"]["reason"],
                "No submission was supplied for this task.",
            )
            self.assertFalse(hasattr(runner, "workspace"))


if __name__ == "__main__":
    unittest.main()