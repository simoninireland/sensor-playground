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


class TestScenarios(unittest.TestCase):

    def setUp(self):
        self._playground = SensorPlayground()


    def testStaticSingleTarget(self):
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
        self._playground.postEvent(sPlace, 0.5, s.sample)

        # run the simulation
        self._playground.run()
