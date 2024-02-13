# Test Euler integrating estimator
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
from simplicial import SimplicialComplex
from sensorplayground import *


class TestEuler(unittest.TestCase):

    def testSingleSensor(self):
        '''Test we can build an estimator for a single sensor.'''
        s = SimpleSensor([0.5, 0.5], 0.1)
        e = EulerEstimator([s])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 0)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 1)


    def testTwoSeparatedSensor(self):
        '''Test we can build an estimator for two non-overlapping sensors.'''
        s1 = SimpleSensor([0.25, 0.25], 0.1)
        s2 = SimpleSensor([0.25, 0.75], 0.1)
        e = EulerEstimator([s1, s2])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 0)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 2)


    def testTwoOverlappingSensors(self):
        '''Test we can build an estimator for two overlapping sensors.'''
        s1 = SimpleSensor([0.25, 0.25], 0.1)
        s2 = SimpleSensor([0.25, 0.35], 0.1)
        e = EulerEstimator([s1, s2])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 1)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 1)


    def testThreeOverlappingSensors(self):
        '''Test we can build an estimator for three overlapping sensors.'''
        s1 = SimpleSensor([0.25, 0.25], 0.1)
        s2 = SimpleSensor([0.25, 0.35], 0.1)
        s3 = SimpleSensor([0.25, 0.3], 0.1)
        e = EulerEstimator([s1, s2, s3])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 1)


    def testFourOverlappingSensors(self):
        '''Test we can build an estimator for four overlapping sensors.'''
        s1 = SimpleSensor([0.25, 0.25], 0.1)
        s2 = SimpleSensor([0.25, 0.35], 0.1)
        s3 = SimpleSensor([0.25, 0.3], 0.1)
        s4 = SimpleSensor([0.3, 0.3], 0.1)
        e = EulerEstimator([s1, s2, s3, s4])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 6)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[3], 1)


    def testFourPartiuallyOverlappingSensors(self):
        '''Test we can build an estimator for four sensors with more complicated overlaps.'''
        s1 = SimpleSensor([0.25, 0.25], 0.05)
        s2 = SimpleSensor([0.25, 0.35], 0.05)
        s3 = SimpleSensor([0.25, 0.3], 0.05)
        s4 = SimpleSensor([0.15, 0.25], 0.06)
        e = EulerEstimator([s1, s2, s3, s4])

        c = e.overhearing()
        self.assertEqual(c.maxOrder(), 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 1)


if __name__ == '__main__':
    unittest.main()
