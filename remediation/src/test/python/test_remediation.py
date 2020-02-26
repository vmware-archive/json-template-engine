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
        pass

    def tearDown(self):
        """
        Tear down each test.
        """
        sys.stdout = sys.__stdout__
        pass

    def test_drift_detection(self):
        remediator.main(["-d",
                         "-c", "companion.json",
                         "target.json"])
        json_str = self.stream.getvalue().strip()
        self.assertEqual(json_str, 'Drift: path(/my_key_1/my_sub_key_1/0), '
                                   'target(xya), companion(xyK)')
