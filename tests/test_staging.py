import tempfile
from pathlib import Path
import unittest

from eval_harness.manifest import Task
from eval_harness.staging import stage_submission


class SubmissionStagingTests(unittest.TestCase):
    def test_copies_workspace_and_stages_candidate_source(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            workspace = root / "task-template"
            workspace.mkdir()
            (workspace / "test_solution.py").write_text(
                "from solution import add\n",
                encoding="utf-8",
            )

            candidate_source = root / "candidate.py"
            candidate_source.write_text(
                "def add(values):\n    return sum(values)\n",
                encoding="utf-8",
            )

            task = Task(
                id="sum-list",
                workspace=workspace,
                submission_target="solution.py",
                image="python:3.12-alpine",
                test_command="python -m unittest discover -v",
                maintainability={},
            )

            staged_workspace = stage_submission(
                task,
                candidate_source,
                root / "evaluation-runs",
            )

            self.assertTrue(
                (staged_workspace / "test_solution.py").is_file()
            )
            self.assertEqual(
                (staged_workspace / "solution.py").read_text(
                    encoding="utf-8"
                ),
                candidate_source.read_text(encoding="utf-8"),
            )
            self.assertFalse((workspace / "solution.py").exists())


if __name__ == "__main__":
    unittest.main()