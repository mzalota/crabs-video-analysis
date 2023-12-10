from unittest import TestCase

from lib.drifts.DriftRawData import DriftRawData


class TestDriftRawData(TestCase):
    def test__remove_outlier(self):
        lst = [1,2,150]
        result = DriftRawData._remove_outlier2(lst)
        self.assertTrue(result)

    def test__remove_no_outlier(self):
        lst = [1,2,3]
        result = DriftRawData._remove_outlier2(lst)
        self.assertFalse(result)