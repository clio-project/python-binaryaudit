
import unittest
from binaryaudit import abicheck


class AbicheckTestSuite(unittest.TestCase):
    def test_is_elf(self):
        assert abicheck.is_elf("/usr/bin/ls")

    def test_get_bits(self):
        code = 8 | 4
        a = abicheck.diff_get_bits(code)
        assert len(a) == 2
        assert "CHANGE" in a
        assert "INCOMPATIBLE_CHANGE" in a

        code = 1 | 2
        a = abicheck.diff_get_bits(code)
        assert len(a) == 2
        assert "ERROR" in a
        assert "USAGE_ERROR" in a

        code = 0
        a = abicheck.diff_get_bits(code)
        assert len(a) == 1
        assert "OK" in a
