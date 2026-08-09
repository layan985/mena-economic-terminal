from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from menaecon.cli import main


class CliTests(unittest.TestCase):
    def test_demo_initialization_and_query(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "demo.db"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(["init", "--database", str(database), "--with-fixtures"]), 0
                )
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(
                    [
                        "get", "unemployment", "--country", "JOR", "--vintage",
                        "2026-06-01", "--database", str(database), "--include-fixtures",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn('"value": 21.4', output.getvalue())
            self.assertNotIn('"value": 21.1', output.getvalue())


if __name__ == "__main__":
    unittest.main()
