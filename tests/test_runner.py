from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from eval_harness.runner import DockerRunner


class DockerRunnerTests(unittest.TestCase):
    @patch("eval_harness.runner.subprocess.run")
    def test_runs_tests_with_network_and_resource_limits(self, run_mock):
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="2 tests passed",
            stderr="",
        )

        runner = DockerRunner(timeout_seconds=30)
        result = runner.execute(
            workspace=Path("sample-workspace"),
            image="python:3.12-alpine",
            test_command="python -m unittest discover -v",
        )

        command = run_mock.call_args.args[0]

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "2 tests passed")
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop", command)
        self.assertIn("ALL", command)
        self.assertIn("--memory", command)
        self.assertIn("512m", command)
        self.assertEqual(
            command[-3:],
            ["sh", "-lc", "python -m unittest discover -v"],
        )


if __name__ == "__main__":
    unittest.main()