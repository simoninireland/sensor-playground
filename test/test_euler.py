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
from sensorplayground import *


class TestEuler(unittest.TestCase):

    def setUp(self):
        self._playground = SensorPlayground()
        self._estimator = EulerEstimator(self._playground)


    # ---------- Overhearing structure ----------

    def testSingleSensor(self):
        '''Test we can build an estimator for a single sensor.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.5, 0.5])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 0)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 1)


    def testTwoSeparatedSensor(self):
        '''Test we can build an estimator for two non-overlapping sensors.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.25])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.75])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 0)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 2)


    def testTwoOverlappingSensors(self):
        '''Test we can build an estimator for two overlapping sensors.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.25])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.35])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 1)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 1)


    def testThreeOverlappingSensors(self):
        '''Test we can build an estimator for three overlapping sensors.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.25])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.35])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.31])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 1)


    def testFourOverlappingSensors(self):
        '''Test we can build an estimator for four overlapping sensors.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.25])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.35])
        self._playground.addSensor(SimpleSensor(0.1), [0.25, 0.31])
        self._playground.addSensor(SimpleSensor(0.1), [0.3, 0.31])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 3)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 6)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[3], 1)


    def testFourPartiallyOverlappingSensors(self):
        '''Test we can build an estimator for four sensors with more complicated overlaps.'''
        self._playground.addSensor(SimpleSensor(0.05), [0.25, 0.25])
        self._playground.addSensor(SimpleSensor(0.05), [0.25, 0.35])
        self._playground.addSensor(SimpleSensor(0.05), [0.25, 0.3])
        self._playground.addSensor(SimpleSensor(0.06), [0.15, 0.25])

        c = self._estimator.overhearing()
        self.assertEqual(c.maxOrder(), 2)
        self.assertEqual(c.numberOfSimplicesOfOrder()[0], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[1], 4)
        self.assertEqual(c.numberOfSimplicesOfOrder()[2], 1)


    # ---------- Target counting ----------

    def testOneSensorOneTarget(self):
        '''Test we can detect one target in the range of one sensor.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.1), [1.0, 1.0])

        c = self._estimator.estimateFromTargets([[0.05, 0.05]])
        self.assertEqual(c, 1)


    def testOneSensorOneTargetFail(self):
        '''Test we can't detect one target out of range.'''
        self._playground.addSensor(SimpleSensor(0.1), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.1), [1.0, 1.0])

        c = self._estimator.estimateFromTargets([[2.0, 2.0]])
        self.assertEqual(c, 0)


    def testTwoSensorsOneTarget(self):
        '''Test we can detect one target in the range of two sensors.'''
        self._playground.addSensor(SimpleSensor(1.0), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(1.0), [0.0, 1.0])

        c = self._estimator.estimateFromTargets([[0.05, 0.05]])
        self.assertEqual(c, 1)


    def testOneTriangleTwoTargets(self):
        '''Test we can detect two targets in a triangle.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.0])

        c = self._estimator.estimateFromTargets([[0.02, 0.02],
                                                 [0.02, 0.08]])
        self.assertEqual(c, 2)


    def testTwoTrianglesTwoTargets(self):
        '''Test we can detect two targets in two adjacent triangles.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.1])

        c = self._estimator.estimateFromTargets([[0.02, 0.02],
                                                 [0.08, 0.08]])
        self.assertEqual(c, 2)


    def testBowtieOneTarget(self):
        '''Test we can detect one target in a bowtie of two triangles.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.2])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.2])

        c = self._estimator.estimateFromTargets([[0.02, 0.02]])
        self.assertEqual(c, 1)


    def testBowtieTwoTargets(self):
        '''Test we can detect two targets in a bowtie of two triangles.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.2])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.2])

        c = self._estimator.estimateFromTargets([[0.02, 0.02],
                                                 [0.18, 0.18]])
        self.assertEqual(c, 2)


    def testTwoSeparatedTrianglesTwoTargets(self):
        '''Test we can detect two targets in two separated triangles.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.5, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.5, 0.0])

        c = self._estimator.estimateFromTargets([[0.02, 0.02],
                                                 [0.52, 0.05]])
        self.assertEqual(c, 2)


    def testTwoConnectedTrianglesTwoTargets(self):
        '''Test we mis-count two targets in two connected triangles.'''
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.0, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.1, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.0])
        self._playground.addSensor(SimpleSensor(0.15), [0.2, 0.1])
        self._playground.addSensor(SimpleSensor(0.15), [0.3, 0.0])

        c = self._estimator.estimateFromTargets([[0.02, 0.02],
                                                 [0.28, 0.05]])
        self.assertEqual(c, 1)


if __name__ == '__main__':
    unittest.main()
