from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from eval_harness.cli import main
from eval_harness.runner import DockerRunner


class CommandLineTests(unittest.TestCase):
    @patch("eval_harness.cli.write_report")
    @patch("eval_harness.cli.evaluate")
    def test_runs_evaluation_and_writes_report(
        self,
        evaluate_mock,
        write_report_mock,
    ):
        evaluate_mock.return_value = {
            "summary": {
                "tasks_evaluated": 1,
                "points_awarded": 100,
                "possible_points": 100,
            },
            "results": [],
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            tasks = root / "tasks.jsonl"
            submissions = root / "submissions.jsonl"
            report = root / "report.json"
            runs_root = root / "runs"

            with patch.object(
                sys,
                "argv",
                [
                    "eval-harness",
                    "--tasks",
                    str(tasks),
                    "--submissions",
                    str(submissions),
                    "--report",
                    str(report),
                    "--runs-root",
                    str(runs_root),
                ],
            ):
                exit_code = main()

        self.assertEqual(exit_code, 0)

        arguments = evaluate_mock.call_args.args
        self.assertEqual(arguments[0], tasks)
        self.assertEqual(arguments[1], submissions)
        self.assertIsInstance(arguments[2], DockerRunner)
        self.assertEqual(arguments[3], runs_root)

        write_report_mock.assert_called_once_with(
            evaluate_mock.return_value,
            report,
        )


if __name__ == "__main__":
    unittest.main()