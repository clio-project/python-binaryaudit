import unittest
from binaryaudit import buildname as bn


class BuildnameTestSuite(unittest.TestCase):
    def test_no_sn(self):
        sn = ""
        fn = "/some/path/to/myexe"
        adir = "/hello/buildhistory/packages/cortexa57-poky-linux/somepkg/binaryaudit/abixml"
        expected = "/hello/buildhistory/packages/cortexa57-poky-linux/somepkg/binaryaudit/abixml/myexe.xml"
        result = bn.build_name(sn, adir, fn)

        assert expected == result

    def test_sn_1(self):
        sn = "libcrypto.so.1.1"
        fn = ""
        adir = "/path/buildhistory/packages/cortexa57-poky-linux/openssl/binaryaudit/abixml"
        expected = "/path/buildhistory/packages/cortexa57-poky-linux/openssl/binaryaudit/abixml/libcrypto.so.xml"
        result = bn.build_name(sn, adir, fn)

        assert expected == result

    def test_sn_2(self):
        fn = "doesn't matter"
        sn = "libcurl.so.4"
        adir = "/there/buildhistory/packages/cortexa57-poky-linux/curl/binaryaudit/abixml"
        expected = "/there/buildhistory/packages/cortexa57-poky-linux/curl/binaryaudit/abixml/libcurl.so.xml"
        result = bn.build_name(sn, adir, fn)

        assert expected == result