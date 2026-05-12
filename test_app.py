import unittest
from app import greet

class TestGreet(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Amy"), "Hello, Alice!")

if __name__ == "__main__":
    unittest.main()
