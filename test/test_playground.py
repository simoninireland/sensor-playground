# Test playground and simulation
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


class DummyAgent(Agent):

    def __init__(self):
        super().__init__()
        self.eventTime = None


    def setUp(self, pg):
        super().setUp(pg)
        self.playground().postEvent(self, 1.0, self.setterEvent)


    def setterEvent(self, t):
        self.eventTime = t


class TestPlayground(unittest.TestCase):

    def setUp(self):
        self._playground = SensorPlayground(d=2)


    # ---------- Agent management ----------

    def testAgents(self):
        '''Test we can add and remove agents.'''
        a = Agent()
        b = Agent()

        self._playground.addAgent(a)
        self._playground.addAgent(b)
        self.assertEqual(set(self._playground.agents()), set([a, b]))

        self._playground.removeAgent(a)
        self.assertEqual(set(self._playground.agents()), set([b]))


    def testGetAgent(self):
        '''Test we can retrieve an agent by id.'''
        a = Agent()
        b = Agent()
        self._playground.addAgent(a)
        self._playground.addAgent(b)

        self.assertEqual(self._playground.getAgent(a.id()), a)
        self.assertEqual(self._playground.getAgent(b.id()), b)
        with self.assertRaises(KeyError):
            self._playground.getAgent('hello')


    def testGetAgentDict(self):
        '''Test we can retrieve agents using the dict interface.'''
        a = Agent()
        b = Agent()
        self._playground.addAgent(a)
        self._playground.addAgent(b)

        self.assertEqual(self._playground[a.id()], a)
        self.assertEqual(self._playground[b.id()], b)
        with self.assertRaises(KeyError):
            self._playground['hello']


    def testContains(self):
        '''Test the conmtains interface for testing for agents.'''
        a = Agent()
        b = Agent()
        self._playground.addAgent(a)
        self._playground.addAgent(b)

        self.assertIn(a.id(), self._playground)
        self.assertIn(b.id(), self._playground)
        self.assertNotIn('hello', self._playground)


    def testPostedEventAtSetup(self):
        '''Test that the agent posts an event when added.'''
        self.assertFalse(self._playground.hasEvents())
        a = DummyAgent()
        self._playground.addAgent(a)
        self.assertTrue(self._playground.hasEvents())


    def testRemoveAgent(self):
        '''Test we remove an agent and all its associated events.'''
        a = DummyAgent()
        b = DummyAgent()
        c = DummyAgent()
        self._playground.addAgent(a)
        self._playground.addAgent(b)
        self._playground.addAgent(c)

        # remove agent by id
        self._playground.removeAgent(a.id())
        self.assertEqual(set(self._playground.agents()), set([b, c]))

        # remove agent by object
        self._playground.removeAgent(c)
        self.assertEqual(set(self._playground.agents()), set([b]))

        # check agents have been removed
        with self.assertRaises(KeyError):
            self._playground.getAgent(a.id())
        with self.assertRaises(KeyError):
            self._playground.getAgent(c.id())
        self.assertEqual(self._playground.getAgent(b.id()), b)

        # check events have been erased as well
        nev = self._playground.run()
        self.assertEqual(nev, 1)
        self.assertIsNone(a.eventTime)
        self.assertIsNotNone(b.eventTime)


    # ---------- Simulation ----------

    def testPostTimes(self):
        '''Test we can only post events into the future.'''
        a = DummyAgent()
        self._playground.addAgent(a)

        self._playground.setSimulationTime(10.0)
        self._playground.postEvent(a, 15.0, a.setterEvent)
        with self.assertRaises(ValueError):
            self._playground.postEvent(a, 0.5, a.setterEvent)


    def testRun(self):
        '''Test we run all events posted by default by agents.'''
        a = DummyAgent()
        b = DummyAgent()
        self._playground.addAgent(a)
        self._playground.addAgent(b)

        nev = self._playground.run()
        self.assertEqual(nev, 2)
        self.assertIsNotNone(a.eventTime)
        self.assertIsNotNone(b.eventTime)
