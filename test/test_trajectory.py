# Test trajectories
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


class TestTrajectory(unittest.TestCase):

    def testDimension(self):
        '''Test we detect mismatched dimensions.'''

        # matched
        _ = Trajectory([1, 2, 3], 0.0, [1, 2, 6], 1.0)
        _ = Trajectory([1, 2], 0.0, [2, 6], 1.0)

        # unmatched with exception
        with self.assertRaises(ValueError):
            _ = Trajectory([1, 2, 3], 0.0, [1, 2], 1.0)


    def testTimes(self):
        '''Test we detect wrongly-ordered times.'''
        with self.assertRaises(ValueError):
            _ = Trajectory([1, 2, 3], 1.0, [1, 2], 0.0)


    def testWithinInterval(self):
        '''Test we can check for positions in intervals (and not).'''
        t = Trajectory([1, 2, 3], 0.0, [1, 3, 6], 1.0)

        self.assertTrue(t.isWithinInterval(0.5))
        self.assertTrue(t.isWithinInterval(0.0))
        self.assertTrue(t.isWithinInterval(1.0))

        self.assertFalse(t.isWithinInterval(1.1))
        with self.assertRaises(ValueError):
            t.isWithinInterval(1.1, fatal=True)


    def testBoundingBox(self):
        '''Test we get the bounding box sense correct.'''

        # correct order
        t = Trajectory([0, 0, 0], 0.0, [1, 1, 1], 1.0)
        (bl, tr) = t.boundingBox()
        self.assertCountEqual(bl, [0, 0, 0])
        self.assertCountEqual(tr, [1, 1, 1])

        # reversed
        t = Trajectory([1, 1, 1], 0.0, [0, 0, 0], 1.0)
        (bl, tr) = t.boundingBox()
        self.assertCountEqual(bl, [0, 0, 0])
        self.assertCountEqual(tr, [1, 1, 1])

        # mixed
        t = Trajectory([0, 0, 1], 0.0, [1, 1, 0], 1.0)
        (bl, tr) = t.boundingBox()
        self.assertCountEqual(bl, [0, 0, 0])
        self.assertCountEqual(tr, [1, 1, 1])


    def testWithinBoundingBox(self):
        '''Test we can check points within bounding boxes (and not).'''
        t = Trajectory([0, 0, 0], 0.0, [1, 1, 1], 1.0)

        self.assertTrue(t.isWithinBoundingBox([0.5, 0.5, 0.5]))
        self.assertTrue(t.isWithinBoundingBox([1, 1, 1]))
        self.assertTrue(t.isWithinBoundingBox([0, 0, 0]))
        self.assertTrue(t.isWithinBoundingBox([1, 0.5, 1]))

        self.assertFalse(t.isWithinBoundingBox([1, 1.5, 1]))
        with self.assertRaises(ValueError):
            t.isWithinBoundingBox([1, 1.5, 1], fatal=True)


    def testPosition(self):
        '''Test position interpolation.'''
        t = Trajectory([0, 0, 0], 0.0, [2, 1, 1], 1.0)

        # at start and end
        self.assertCountEqual(t.position(0.0), [0.0, 0.0, 0.0])
        self.assertCountEqual(t.position(1.0), [2.0, 1.0, 1.0])
        self.assertCountEqual(t.position(0.8), [1.6, 0.8, 0.8])

        # within
        self.assertCountEqual(t.position(0.5), [1.0, 0.5, 0.5])

        # outside
        with self.assertRaises(ValueError):
            t.position(1.1)

        # test endpoints are within bounding box
        self.assertTrue(t.isWithinBoundingBox(t.position(0.0)))
        self.assertTrue(t.isWithinBoundingBox(t.position(1.0)))

        # within with a reversed direction
        t = Trajectory([1, 1, 1], 0.0, [0, 0, 0], 1.0)
        self.assertCountEqual(t.position(0.5), [0.5, 0.5, 0.5])
