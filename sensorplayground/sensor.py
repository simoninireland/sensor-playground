# Sensors
#
# Copyright (C) 2024 Simon Dobson
#
# This file is part of sensor-playground, an experimental framework for
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

import numpy
from numpy.linalg import norm
from typing import List, Union, Any, Iterable, cast
from sensorplayground import Position, distanceBetween, BoundingBox, Agent, TargetCount


class Sensor:
    '''A sensor attached to an agent.

    :param a: the agent to which the sensor is attached
    :param id: (optional) sensor id (defaults to a unique identifier)'''

    # Name generation
    UNIQUE = 0                    #: Source of unique sensor ids.


    def __init__(self, a: Agent= None, id: Any = None):
        if id is None:
            id = f'sensor{Sensor.UNIQUE}'
            id = Sensor.UNIQUE
            Sensor.UNIQUE += 1
        self._id: Any = id
        self._agent: Agent = a


    # ---------- Access ----------

    def id(self) -> Any:
        '''Return the sensor id.

        :returns: the id'''
        return self._id


    def agent(self) -> Agent:
        '''Return the agent to which this sensor is attached.

        :returns: the agent'''
        return self._agent


    def setAgent(self, a: Agent):
        '''Associate the sensor with the given agent.

        :param a: the agent'''

        # detach from previous agent if there is one
        if self._agent is not None:
            self._agent.removeSensor(self)
        self._agent = a


    def position(self) -> Position:
        '''The sensor's position is that of its agent.

        :returns: the position'''
        return self.agent().position()


    def distanceTo(self, a: Agent) -> float:
        '''The distance to another agent is its distance from this
        sensor's agent.

        :param a: the other agent
        :returns: the distance'''
        return self.agent().distanceTo(a)


    def playground(self) -> 'SensorPlayground':
        '''The sensor's playground is that of its agent.

        :returns: the playground'''
        return self.agent().playground()


    def fieldOfView(self) -> BoundingBox:
        '''Return the sensor's current field of view.

        This will typically need to be computed from the sensor's position,
        and so may change with time as the agent moves. The default
        returns None, indicating that the sensor has no field of view.

        :returns: the field of view bounding box'''
        return None


    # ---------- Event interface ----------

    def sample(self, t: float):
        '''Event that causes the event to take a sample.

        This method sould be overridden byb sub-classes. The default
        does nothing.

        :param t: the current siimulation time'''
        pass


# ---------- Simple sensors for debugging ----------

class SimpleTargetCountSensor(Sensor, TargetCount):

    '''A sensor with a circular or spherical sensing field defined
    by its radius that detects targets within this field. The
    sensor doesn't move and so can't be re-positioned or assigned
    a motion.

    For topological reasons the sensor field is an open region, and
    so includes all points at a distance strictly less than the radius.

    :param a: the agent
    :param r: the sensing field radius (defaults to 1.0)
    :param id: (optional) sensor identifier'''


    def __init__(self, a: Agent = None, r: float = 1.0, id: Any = None):
        super().__init__(id, id=a)
        self._detectionRadius = r
        self._targets = 0


    def detectionRadius(self) -> float:
        return self._detectionRadius


    def fieldOfView(self) -> BoundingBox:
        '''Return the sensor's bounding box based on its posiotion
        and detection radius.

        :returns: the bounding box'''
        p = self.position()
        r = self.detectionRadius()
        bl = p.copy()
        tr = p.copy()
        for i in range(len(p)):
            bl[i] = p[i] - r
            tr[i] = p[i] + r
        return (bl, tr)


    def numberOfTargets(self) -> int:
        '''Return the number of targets the sensor last counted.

        :returns: the number of targets'''
        return self._targets


    def detectsTarget(self, t: Agent) -> bool:
        '''Always True (targets in range are always detected.

        :param t: the target
        :returns: True'''
        return True


    # ---------- Events ----------

    def sample(self, t: float):
        '''Count the targets within range of the sensor.

        This involves finding all targets within the sensor's detection
        radius (first using a bounding box, then refining), and then
        checking whether each target is actually detected based on its
        position. The number of targets is recorded for retrieval
        using :meth:`numberOfTargets`.

        :param t: simulation time (ignored)'''
        r = self.detectionRadius()
        p = self.position()

        # retrieve all potentially-detected targets
        bb = self.getBoundingBox()
        possible = self.playground().allWithinBoundingBox(bb, cls=Agent)
        targets = [t for t in possible if self.distanceTo(t) < r]

        # determine which targets are detected
        detected = [t for t in targets if self.detectsTarget(t)]

        # record the detected targets
        self._targets = len(detected)
