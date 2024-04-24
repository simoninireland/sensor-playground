# Test different sensing scenarios
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

from re import split
import unittest
from sensorplayground import *


class TargetCountingTraceSensor(SimpleTargetCountSensor):
    '''A target counter that records a trace.'''

    def __init__(self, a = None, r = 1.0, id = None):
        super().__init__(a, r, id)
        self._trace = []


    def sample(self, t):
        super().sample(t)
        self._trace.append((t, self.numberOfTargets()))


class TestScenarios(unittest.TestCase):

    def setUp(self):
        self._playground = SensorPlayground()


    # ---------- Sampling target counting sensors ----------

    def testStaticSensorSingleMovingTarget(self):
        '''Test a single target against a single static sensor.'''

        # static sensor with radius 1 field of view
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        sPlace.setPosition([1.0, 1.0])
        s = SimpleTargetCountSensor(sPlace, r=1.0)

        # target that moves through the sensor field at t=0.5
        m = MobileAgent()
        self._playground.addAgent(m)
        m.setPosition([0.0, 1.5])
        m.moveTo([2.0, 1.5], dt=1.0)

        # add a sensing event for t=0.5
        self._playground.postEvent(s, 0.5, s.sample)

        # run the simulation
        self._playground.run()

        # check detection
        self.assertEqual(s.numberOfTargets(), 1)


    def testStaticSensorSingleStaticTargetMissed(self):
        '''Test a single target against a single static sensor that never sees it.'''

        # static sensor with radius 1 field of view
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        sPlace.setPosition([1.0, 1.0])
        s = SimpleTargetCountSensor(sPlace, r=1.0)

        # target that stays out of field of view
        m = Agent()
        self._playground.addAgent(m)
        m.setPosition([0.0, 1.5])

        # add a sensing event for t=0.5
        self._playground.postEvent(s, 0.5, s.sample)

        # run the simulation
        self._playground.run()

        # check no detection occurred
        self.assertEqual(s.numberOfTargets(), 0)


    def testStaticSensorSingleStaticTargetSeen(self):
        '''Test a single target against a single static sensor that sees it.'''

        # static sensor with radius 1 field of view
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        sPlace.setPosition([1.0, 1.0])
        s = SimpleTargetCountSensor(sPlace, r=1.0)

        # target that stays out of field of view
        m = Agent()
        self._playground.addAgent(m)
        m.setPosition([0.1, 1.0])

        # add a sensing event for t=0.5
        self._playground.postEvent(s, 0.5, s.sample)

        # run the simulation
        self._playground.run()

        # check detection occurred
        self.assertEqual(s.numberOfTargets(), 1)


    def testStaticSensorSingleMovingTargetOverTime(self):
        '''Test a single target against a single static sensor, checking the trace.'''

        # static sensor with radius 1 field of view
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        sPlace.setPosition([1.0, 1.0])
        s = TargetCountingTraceSensor(sPlace, r=1.0)

        # target that moves through the sensor field at t=0.5
        m = MobileAgent()
        self._playground.addAgent(m)
        m.setPosition([0.0, 1.5])
        m.moveTo([2.0, 1.5], dt=1.0)

        # add sensing events for t=0.0, 0.5, 1.0
        for t in [0.0, 0.5, 1.0]:
            self._playground.postEvent(s, t, s.sample)

        # run the simulation
        self._playground.run()

        # check detection
        self.assertCountEqual(s._trace, [(0.0, 0), (0.5, 1), (1.0, 0)])


    def testStaticSensorTwoMovingTargetsOverTime(self):
        '''Test two targets against a single static sensor, checking the trace.'''

        # static sensor with radius 1 field of view
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        sPlace.setPosition([1.0, 1.0])
        s = TargetCountingTraceSensor(sPlace, r=1.0)

        # target that moves through the sensor field and is visible at t=0.5
        m = MobileAgent()
        self._playground.addAgent(m)
        m.setPosition([0.0, 1.5])
        m.moveTo([2.0, 1.5], dt=1.0)

        # target that stops in the sensor field at time t=0.75
        m = MobileAgent()
        self._playground.addAgent(m)
        m.setPosition([-0.65, 1.0])
        m.moveTo([0.1, 1.0], dt=0.75)

        # add sensing events for t=0.0, 0.5, 0.75, 1.0
        for t in [0.0, 0.5, 0.70, 1.0]:
            self._playground.postEvent(s, t, s.sample)

        # run the simulation
        self._playground.run()

        # check detection
        self.assertCountEqual(s._trace, [(0.0, 0), (0.5, 1), (0.70, 2), (1.0, 1)])
