import unittest
from src.main import run

class TestMain(unittest.TestCase):
    def test_run(self):
        # Just checks if function executes without error
        try:
            run()
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
