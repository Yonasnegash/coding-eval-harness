import json
from pathlib import Path
import tempfile
import unittest

from eval_harness.report import write_report


class ReportWriterTests(unittest.TestCase):
    def test_writes_formatted_json_report(self):
        report = {
            "schema_version": "1.0",
            "summary": {
                "tasks_evaluated": 1,
                "points_awarded": 100,
                "possible_points": 100,
            },
            "results": [
                {
                    "task_id": "sum-list",
                    "status": "passed",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = (
                Path(temporary_directory)
                / "outputs"
                / "report.json"
            )

            write_report(report, destination)

            persisted = json.loads(
                destination.read_text(encoding="utf-8")
            )

            self.assertEqual(persisted, report)
            self.assertTrue(
                destination.read_text(encoding="utf-8").endswith("\n")
            )


if __name__ == "__main__":
    unittest.main()