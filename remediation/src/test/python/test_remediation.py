import sys
import unittest
from io import StringIO

from jsonreme import remediator


class RemediationTests(unittest.TestCase):
    """
    Unit tests for the template engine.
    """
    def setUp(self):
        """
        Set up each test.
        """
        self.stream = StringIO()
        sys.stdout = self.stream

    def tearDown(self):
        """
        Tear down each test.
        """
        sys.stdout = sys.__stdout__

    def test_drift_detection(self):
        remediator.main(["--drift",
                         "-c", "companion.json",
                         "target.json"])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, 'Drift: path(/my_key_1/my_sub_key_1/0), '
                                   'target(xya), companion(xyK)')

    def test_reme(self):
        remediator.main(["-r", "reme.json",
                         "target.json"])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str,
                         "workspace output: OrderedDict(["
                         "('before_my_key_1', \"reme: path /my_key_1 {'my_sub_key_1': ['xya', 'xyb', 'xyc'], 'my_sub_key_2': 'xyz'}\"), "
                         "('after_my_sub_key_1_0', 'reme: path /my_key_1/my_sub_key_1/0 xya'), "
                         "('after_my_sub_key_1_1', 'reme: path /my_key_1/my_sub_key_1/1 xyb'), "
                         "('after_my_sub_key_1_2', 'reme: path /my_key_1/my_sub_key_1/2 xyc'), "
                         "('after_my_sub_key_1_', \"reme: path /my_key_1/my_sub_key_1 ['xya', 'xyb', 'xyc']\"), "
                         "('after_my_key_1', \"reme: path /my_key_1 {'my_sub_key_1': ['xya', 'xyb', 'xyc'], 'my_sub_key_2': 'xyz'}\")])")
