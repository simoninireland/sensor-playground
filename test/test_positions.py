# Test positions
#
# Copyright (C) 2024 Simon Dobson
#
# This file is part of target-counting, an experiment in
# target counting and higher-order sensor data analytics
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/gpl.html>.

import unittest
from sensorplayground import *


class TestPositions(unittest.TestCase):

    # ---------- Bounding boxes ----------

    def testEmptyBox(self):
        '''Test functions behave as expected on an empty bounding box.'''
        bb = BoundingBox([], [])
        self.assertTrue(bb.contains([]))


    def testDimensions(self):
        '''Test we can detect correct and mis-mtched dimensions.'''

        # matching
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([0.0, 0.0, 1.0], [1.0, 1.0, 5.0])

        # mis-matching
        with self.assertRaises(ValueError):
            b3 = BoundingBox([0.0, 0.0], [1.0])
        with self.assertRaises(ValueError):
            b4 = BoundingBox([0.0], [1.0, 1.0])
        with self.assertRaises(ValueError):
            b5 = BoundingBox([0.0, 0.0], [1.0, 1.0, 0.0])

        # zero depth
        b5 = BoundingBox([0.0, 0.0, 0.0], [1.0, 1.0, 0.0])
        self.assertTrue(b5.contains([0.9, 0.9, 0.0]))

    def testCorners(self):
        '''Test corners come out (smallest, largest).'''

        # right way round
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        (bl, tr) = b1.corners()
        for d in range(2):
            self.assertTrue(bl[d] < tr[d])

        # wrong way round
        b1 = BoundingBox([1.0, 1.0], [0.0, 0.0])
        (bl, tr) = b1.corners()
        for d in range(2):
            self.assertTrue(bl[d] < tr[d])


    def testOrdering(self):
        '''Test the bounding box is set correctly regardless of how the corners are arranged.'''

        # obvious set-up
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        self.assertTrue(b1.contains([0.1, 0.1]))
        self.assertFalse(b1.contains([1.1, 1.1]))

        # reversed
        b2 = BoundingBox([1.0, 1.0], [0.0, 0.0])
        self.assertTrue(b2.contains([0.1, 0.1]))
        self.assertFalse(b2.contains([1.1, 1.1]))

        # mixed
        b3 = BoundingBox([1.0, 0.0], [0.0, 1.0])
        self.assertTrue(b3.contains([0.1, 0.1]))
        self.assertFalse(b3.contains([1.1, 1.1]))


    def testContains(self):
        '''Test point containment.'''
        bb = BoundingBox([0.0, 0.0], [1.0, 1.0])

        # within
        self.assertTrue([0.1, 0.1] in bb)
        self.assertTrue([0.5, 0.5] in bb)

        # on the boundary
        self.assertFalse(bb.contains([0.0, 0.5]))
        self.assertFalse(bb.contains([0.5, 0.0]))
        self.assertFalse(bb.contains([0.0, 0.0]))


    def testPoint(self):
        '''Test we can create bounding boxes that are single points.'''
        b1 = BoundingBox([0.0, 0.0])
        self.assertEqual(b1.corners(), ([0.0, 0.0], [0.0, 0.0]))
        self.assertTrue(b1.contains([0.0, 0.0]))

        b2 = BoundingBox([0.0, 0.0], [0.0, 0.0])
        self.assertEqual(b1.corners(), ([0.0, 0.0], [0.0, 0.0]))
        self.assertTrue(b1.contains([0.0, 0.0]))


    def testUnion(self):
        '''Test unioning of bounding boxes.'''

        # same box twice
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        bu = b1.union(b2)
        self.assertCountEqual(b1.corners(), bu.corners())

        # extending box
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([0.5, 0.5], [1.5, 1.5])
        bu = b1.union(b2)
        self.assertCountEqual(bu.corners(), ([0.0, 0.0], [1.5, 1.5]))

        # non-intersecting boxes
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([1.5, 1.5], [2.5, 2.5])
        bu = b1.union(b2)
        self.assertCountEqual(bu.corners(), ([0.0, 0.0], [2.5, 2.5]))

        # boxes with reversed corners
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([1.5, 2.5], [2.5, 1.5])
        bu = b1.union(b2)
        self.assertCountEqual(bu.corners(), ([0.0, 0.0], [2.5, 2.5]))

        # mismatched dimensions
        b1 = BoundingBox([0.0, 0.0], [1.0, 1.0])
        b2 = BoundingBox([1.5, 1.5, 0.0], [2.5, 2.5, 1.5])
        with self.assertRaises(ValueError):
            bu = b1.union(b2)


class TestTrajectories(unittest.TestCase):

    def testBasic(self):
        '''Test the basics.'''
        j = Trajectory([0.0, 0.0], 0.0,
                       [1.0, 1.0], 1.0)

        self.assertEqual(j.interval(), (0.0, 1.0))
        self.assertEqual(j.endpoints(), ([0.0, 0.0], [1.0, 1.0]))
        self.assertTrue(j.isWithinInterval(0.5))
        with self.assertRaises(ValueError):
            j.isWithinInterval(1.5, fatal=True)
        self.assertEqual(j.boundingBox().corners(),
                         ([0.0, 0.0], [1.0, 1.0]))


    def testPosition(self):
        '''Test we linearly interpolate the position correctly.'''
        j = Trajectory([0.0, 0.0], 0.0,
                       [1.0, 1.0], 1.0)
        self.assertEqual(j.positionAt(0.5), [0.5, 0.5])


    def testEnterExit(self):
        '''Test the simple enter-exit scenario.'''
        j = Trajectory([0.0, 0.5], 0.0,
                       [1.0, 0.5], 1.0)
        bb = BoundingBox([0.25, 0.25], [0.75, 0.75])
        ee = j.entersLeavesAt(bb)
        print(ee)
        self.assertTrue(True)
