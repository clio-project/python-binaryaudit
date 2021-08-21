
import sys
import unittest
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from binaryaudit import conf  # noqa: E402


class ConfTestSuite(unittest.TestCase):
    def test_get_config_dir(self):
        exp = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "conf"))
        ret = conf.get_config_dir()
        assert exp == ret
