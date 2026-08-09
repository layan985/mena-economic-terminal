from __future__ import annotations

import unittest

from menaecon.validation import ValidationError, validate_observation
from tests.helpers import valid_row


class ValidationTests(unittest.TestCase):
    def test_verified_row_passes(self):
        row = validate_observation(valid_row())
        self.assertEqual(row.country, "JOR")
        self.assertEqual(len(row.observation_id), 64)

    def test_release_must_precede_retrieval(self):
        with self.assertRaisesRegex(ValidationError, "release_time cannot be after"):
            validate_observation(
                valid_row(retrieval_timestamp="2026-02-14T09:00:00+03:00")
            )

    def test_verified_row_requires_real_commit(self):
        with self.assertRaisesRegex(ValidationError, "full 40-character Git commit"):
            validate_observation(valid_row(git_commit="UNCOMMITTED"))

    def test_nonfinite_value_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "value must be finite"):
            validate_observation(valid_row(value="NaN"))

    def test_identity_is_tamper_evident(self):
        row = validate_observation(valid_row())
        payload = row.to_dict()
        payload["value"] = 99
        # Value is deliberately not identity: source hash/release lineage is. Changing a
        # value without changing bytes is caught by source reconciliation, not row identity.
        self.assertEqual(validate_observation(payload).observation_id, row.observation_id)
        payload["revision"] = 1
        with self.assertRaisesRegex(ValidationError, "observation_id does not match"):
            validate_observation(payload)


if __name__ == "__main__":
    unittest.main()
