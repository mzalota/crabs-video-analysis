from unittest import TestCase

from lib.common import Point, Box


class TestBox(TestCase):
    def test_box_from_string(self):
        #setup
        box = Box(Point(3, 5), Point(7, 11))

        #exercise
        asSring = str(box)
        reBox = Box.from_string(asSring)

        #assert
        self.assertEqual(reBox.topLeft.x, 3)
        self.assertEqual(reBox.topLeft.y, 5)
        self.assertEqual(reBox.bottomRight.x, 7)
        self.assertEqual(reBox.bottomRight.y, 11)
