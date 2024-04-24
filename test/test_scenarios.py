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


class Target(MobileAgent):
    '''An agent that's distinct from an agent with a sensor.'''
    pass


class Tweeter(Target):
    '''A target that "tweets" and triggers sensors for which it is in
    view.'''

    def tweet(self, t):
        '''Cause an observable tweet.

        :param t: the simulation time (ignored)'''
        print('tweet')
        possibleSensors = self.playground().allSensorsObserving(self, cls=Acoustic)
        print(possibleSensors)
        for s in possibleSensors:
            s.triggeredBy(self)


class Acoustic(SimpleTargetCountSensor):
    '''A triggerable sensor that counts tweets.'''

    def __init__(self, a = None, r = 1.0, id = None):
        super().__init__(a, r, id)
        self._tweets = 0


    def triggeredBy(self, a):
        '''Increment the count.

        :param a: the target that triggered the sensor'''
        self._tweets += 1


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

        # add sensing events for t=0.0, 0.5, 0.70, 1.0
        # (0.70 is chosen so both targets are in view)
        for t in [0.0, 0.5, 0.70, 1.0]:
            self._playground.postEvent(s, t, s.sample)

        # run the simulation
        self._playground.run()

        # check detection
        self.assertCountEqual(s._trace, [(0.0, 0), (0.5, 1), (0.70, 2), (1.0, 1)])


    def testStaticTargetsDistinct(self):
        '''Test a target counting scenario with non-overlapping fields of view.'''

        # sensors with overlap
        sPlace1 = Agent()
        sPlace2 = Agent()
        sPlace3 = Agent()
        for p in [sPlace1, sPlace2, sPlace3]:
            self._playground.addAgent(p)
        s1 = SimpleTargetCountSensor(sPlace1, r=1.0, cls=Target)
        s2 = SimpleTargetCountSensor(sPlace2, r=1.0, cls=Target)
        s3 = SimpleTargetCountSensor(sPlace3, r=1.0, cls=Target)
        sPlace1.setPosition([0.0, 0.0])
        sPlace2.setPosition([-2.25, 0.0])
        sPlace3.setPosition([2.25, 0.0])

        # targets in the views of s1 and s3
        m1 = Target()
        self._playground.addAgent(m1)
        m1.setPosition([0.6, 0.1])
        m2 = Target()
        self._playground.addAgent(m2)
        m2.setPosition([1.5, 0.1])

        # sample at all three sensors
        for s in [s1, s2, s3]:
            self._playground.postEvent(s, 1.0, s.sample)

        # run the simulation
        self._playground.run()

        # check the counts
        self.assertEqual(s1.numberOfTargets(), 1)
        self.assertEqual(s2.numberOfTargets(), 0)
        self.assertEqual(s3.numberOfTargets(), 1)


    def testStaticTargetsOverlapping(self):
        '''Test a target counting scenario with overlapping fields of view.'''

        # sensors with overlap
        sPlace1 = Agent()
        sPlace2 = Agent()
        sPlace3 = Agent()
        for p in [sPlace1, sPlace2, sPlace3]:
            self._playground.addAgent(p)
        s1 = SimpleTargetCountSensor(sPlace1, r=1.0, cls=Target)
        s2 = SimpleTargetCountSensor(sPlace2, r=1.0, cls=Target)
        s3 = SimpleTargetCountSensor(sPlace3, r=1.0, cls=Target)
        sPlace1.setPosition([0.0, 0.0])
        sPlace2.setPosition([-0.25, 0.0])
        sPlace3.setPosition([1.25, 0.0])

        # targets in the overlap and in view of s3 only
        m1 = Target()
        self._playground.addAgent(m1)
        m1.setPosition([0.6, 0.1])
        m2 = Target()
        self._playground.addAgent(m2)
        m2.setPosition([1.5, 0.1])

        # sample at all three sensors
        for s in [s1, s2, s3]:
            self._playground.postEvent(s, 1.0, s.sample)

        # run the simulation
        self._playground.run()

        # check the counts
        self.assertEqual(s1.numberOfTargets(), 1)
        self.assertEqual(s2.numberOfTargets(), 1)
        self.assertEqual(s3.numberOfTargets(), 2)


    # ---------- Triggered sensors ----------

    def testHearSingleTweet(self):
        '''Test we can hear a single tweet.'''

        # sensor
        sPlace = Agent()
        self._playground.addAgent(sPlace)
        s = Acoustic(sPlace, r=1.0)
        sPlace.setPosition([0.0,0.0])

        # target that tweets
        t = Tweeter()
        self._playground.addAgent(t)
        t.setPosition([0.5, 0.5])

        # set a tweet event
        self._playground.postEvent(t, 1.0, t.tweet)

        # run the simulation
        self._playground.run()

        # check the counts
        self.assertEqual(s._tweets, 1)
