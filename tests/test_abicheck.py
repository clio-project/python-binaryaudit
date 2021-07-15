
import unittest
from binaryaudit import abicheck


class AbicheckTestSuite(unittest.TestCase):
    def test_is_elf(self):
        assert abicheck.is_elf("/usr/bin/ls")
