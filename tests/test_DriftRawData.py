from unittest import TestCase

from lib.drifts.DriftRawData import DriftRawData


class TestDriftRawData(TestCase):
    def test__remove_outlier(self):
        lst = [1,2,150]
        result = DriftRawData._has_outlier_stderr(lst)
        self.assertEqual(result, "MAX_OUTLIER")

    def test__remove_no_outlier(self):
        lst = [1,2,3]
        result = DriftRawData._has_outlier_stderr(lst)
        self.assertEqual(result, "OK")