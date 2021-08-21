import unittest
from binaryaudit import util


class UtilTestSuite(unittest.TestCase):
    def test_no_sn(self):
        sn = ""
        fn = "/some/path/to/myexe"
        adir = "/hello/buildhistory/packages/cortexa57-poky-linux/somepkg/binaryaudit/abixml"
        expected = "/hello/buildhistory/packages/cortexa57-poky-linux/somepkg/binaryaudit/abixml/myexe.xml"
        result = util.create_path_to_xml(sn, adir, fn)

        assert expected == result

    def test_sn_1(self):
        sn = "libcrypto.so.1.1"
        fn = ""
        adir = "/path/buildhistory/packages/cortexa57-poky-linux/openssl/binaryaudit/abixml"
        expected = "/path/buildhistory/packages/cortexa57-poky-linux/openssl/binaryaudit/abixml/libcrypto.so.xml"
        result = util.create_path_to_xml(sn, adir, fn)

        assert expected == result

    def test_sn_2(self):
        fn = "doesn't matter"
        sn = "libcurl.so.4"
        adir = "/there/buildhistory/packages/cortexa57-poky-linux/curl/binaryaudit/abixml"
        expected = "/there/buildhistory/packages/cortexa57-poky-linux/curl/binaryaudit/abixml/libcurl.so.xml"
        result = util.create_path_to_xml(sn, adir, fn)

        assert expected == result

    def test_build_diff_filename(self):
        name = "rpm-libs"
        ver_old = "4.14.2-10.cm1"
        ver_new = "4.14.2-13.cm1"
        exp = "rpm-libs__4.14.2-10.cm1__4.14.2-13.cm1.abidiff"
        ret = util.build_diff_filename(name, ver_old, ver_new)
        assert exp == ret
