import unittest

from solution import add

class AddTests(unittest.TestCase):
    def tests_add_integer_values(self):
        self.assertEqual(add([3, 4, 5]), 12)

    def test_handles_an_empty_list(self):
        self.assertEqual(add([]), 0)

if __name__ == "__main__":
    unittest.main()