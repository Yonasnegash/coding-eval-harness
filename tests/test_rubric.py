import unittest

from eval_harness.rubric import score_maintainability


class MaintainabilityRubricTests(unittest.TestCase):
    def test_awards_full_score_for_clear_python_source(self):
        source = '''
def add(values):
    """Return the sum of integer values."""
    return sum(values)
'''

        result = score_maintainability(
            source,
            {"max_line_length": 100},
        )

        self.assertEqual(result["points_awarded"], 30)
        self.assertEqual(result["possible_points"], 30)
        self.assertTrue(
            all(check["passed"] for check in result["checks"])
        )


if __name__ == "__main__":
    unittest.main()