import copy
import json
import subprocess
import sys
import shutil
import uuid
from contextlib import contextmanager
import unittest
from datetime import date
from pathlib import Path

from tracker import load_case, report

ROOT = Path(__file__).parent


@contextmanager
def temporary_case_directory():
    directory = ROOT / (".test-" + uuid.uuid4().hex)
    directory.mkdir()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.case = load_case(ROOT / "example.json")

    def test_due_today_is_not_overdue(self):
        result = report(self.case, date(2026, 10, 23))
        self.assertIn("[PENDING] searches", result)
        self.assertNotIn("[OVERDUE]", result)

    def test_overdue_and_next_action(self):
        result = report(self.case, date(2026, 10, 26))
        self.assertIn("[OVERDUE] searches", result)
        self.assertIn("Progress: 1/4", result)
        self.assertIn("Next action: Follow up with Solicitor", result)

    def test_completed_tasks_are_not_flagged(self):
        for task in self.case["tasks"]:
            task["status"] = "complete"
        result = report(self.case, date(2026, 11, 1))
        self.assertIn("All tracked milestones are complete", result)
        self.assertNotIn("[OVERDUE]", result)

    def test_duplicate_ids_rejected(self):
        case = copy.deepcopy(self.case)
        case["tasks"][1]["id"] = case["tasks"][0]["id"]
        with temporary_case_directory() as directory:
            path = Path(directory) / "case.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique"):
                load_case(path)

    def test_cli_persists_completion_and_rejects_unknown_id(self):
        with temporary_case_directory() as directory:
            path = Path(directory) / "case.json"
            path.write_text(json.dumps(self.case), encoding="utf-8")
            command = [sys.executable, str(ROOT / "tracker.py"), str(path)]
            result = subprocess.run(command + ["--complete", "searches"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(load_case(path)["tasks"][1]["status"], "complete")
            before = path.read_bytes()
            result = subprocess.run(command + ["--complete", "unknown"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
