import json
import tempfile
from pathlib import Path
import unittest

from eval_harness.manifest import ManifestError, load_tasks


class TaskManifestTests(unittest.TestCase):
    def write_tasks(self, root: Path, rows: list[dict]) -> Path:
        tasks_dir = root / "tasks"
        tasks_dir.mkdir()
        manifest = tasks_dir / "tasks.jsonl"
        manifest.write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )
        return manifest

    def valid_task(self) -> dict:
        return {
            "id": "sum-list",
            "workspace": "../workspaces/sum-list",
            "submission_target": "solution.py",
            "image": "python:3.12-alpine",
            "test_command": "python -m unittest discover -v",
        }

    def test_loads_a_valid_task(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "workspaces" / "sum-list").mkdir(parents=True)
            manifest = self.write_tasks(root, [self.valid_task()])

            task = load_tasks(manifest)[0]

        self.assertEqual(task.id, "sum-list")
        self.assertEqual(task.image, "python:3.12-alpine")
        self.assertEqual(task.submission_target, "solution.py")

    def test_rejects_duplicate_task_ids(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "workspaces" / "sum-list").mkdir(parents=True)
            task = self.valid_task()
            manifest = self.write_tasks(root, [task, task])

            with self.assertRaises(ManifestError):
                load_tasks(manifest)


if __name__ == "__main__":
    unittest.main()