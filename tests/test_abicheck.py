
import unittest
import os
from binaryaudit import abicheck

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class AbicheckTestSuite(unittest.TestCase):
    def test_is_elf(self):
        assert abicheck.is_elf("/bin/ls")

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

    def test_get_soname_from_xml(self):
        fn = os.path.join(data_dir, "libssl.so.xml")
        with open(fn, "rb") as fd:
            xml = fd.read()
            fd.close()
        soname = abicheck.get_soname_from_xml(xml)
        assert "libssl.so.1.1" == soname

    def test_compare_no_suppress(self):
        ref = os.path.join(data_dir, "libtest1-v0.so")
        cur = os.path.join(data_dir, "libtest1-v1.so")
        result = abicheck.compare(ref, cur)
	assert result is not None

