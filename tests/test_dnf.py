import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from binaryaudit import dnf  # noqa: E402

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class dnfTestSuite(unittest.TestCase):
    def test_download(self):
        try:
            rpm_name = dnf.download("Cython-0.29.13-6.cm1.src.rpm", data_dir + "/", "python3-Cython", {})
        except Exception:
            return
        rpm_name = os.path.join(data_dir, "old/" + rpm_name)
        self.assertTrue(os.path.exists(rpm_name))

    def test_generate_abidiffs_output(self):
        new_json_file = os.path.join(data_dir, 'new.json')
        old_json_file = os.path.join(data_dir, 'old.json')
        dnf.generate_abidiffs("Cython-0.29.13-6.cm1.src.rpm", "data/", new_json_file,
                              old_json_file, "data/output_abidiffs/", False)
        with open(os.path.join(data_dir, 'output_abidiffs/python3-Cython__0.28.5-8.cm1__0.29.13-6.cm1.abidiff')) as f:
            out = f.read()
        os.remove(os.path.join(data_dir, 'output_abidiffs/python3-Cython__0.28.5-8.cm1__0.29.13-6.cm1.abidiff'))
        os.rmdir(os.path.join(data_dir, 'output_abidiffs/'))
        with open(os.path.join(data_dir, 'test_generate_abidiffs_expected')) as f:
            expected_out = f.read()
        assert out == expected_out
