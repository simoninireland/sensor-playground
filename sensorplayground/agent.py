# Agents, the base class for sensors and targets
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
from typing import List, Union, Any, Dict, Iterable, Set, cast
from sensorplayground import Position, BoundingBox, distanceBetween, Trajectory, Sensor

# There is a circular import between Agent and SensorPlayground at the
# typing level (but not at the execution level), when providing types
# for setUp(). To deal with this we only import SensorPlayground in order
# to type-check Agent, and not for execution. (See
# https://www.stefaanlippens.net/circular-imports-type-hints-python.html)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sensorplayground import SensorPlayground, Sensor


# Stationary (immobile) agents

class Agent:
    '''The base class of agents.

    In the general case agents can move. Instances of this class can
    be positioned (and repositioned), but cannot engage in motion.
    They can also have behaviour that is triggered within a
    simulation by defining events that get posted.

    :param id: (optional) the agent's id

    '''

    # Name generation
    UNIQUE = 0                    #: Source of unique agent ids.


    def __init__(self, id: Any = None):
        if id is None:
            id = f'agent-{Agent.UNIQUE}'
            Agent.UNIQUE += 1
        self._id: Any = id
        self._playground: 'SensorPlayground' = None

        # positional state
        self._position: Position = None

        # attached sensors
        self._sensors: Set['Sensor'] = set()
        self._sensorIds: Dict[Any, Sensor] = dict()


    # ---------- Access ----------

    def id(self) -> Any:
        '''Return the agent id.

        :returns: the id'''
        return self._id


    def now(self):
        '''Return the current simulation time in the agent's playground.

        This is a helper method that calls :meth:`SensorPlayground.now`.

        :returns: the current simulation time'''
        return self.playground().now()


    def playground(self) -> 'SensorPlayground':
        '''Returns the agent's playground.

        :returns: the playground'''
        return self._playground


    # ---------- Sensors ----------

    def addSensor(self, s: 'Sensor'):
        '''Add a sensor to the agent. The sensor's position will he
        that of the agent as it possibly moves.

        :param s: the sensor'''
        self._sensors.add(s)
        self._sensorIds[s.id()] = s

        # set the sensor's agent
        s.setAgent(self)


    def removeSensor(self, sid: Union[Sensor, Any]):
        '''Remove a sensor from the agent.

        :param sid: the sensor or its id'''

        # disambiguate
        id = sid.id() if isinstance(sid, Sensor) else sid
        s = self._sensorIds[id]

        # remove the agent
        self._sensors.remove(s)
        del self._sensorIds[id]


    def sensors(self) -> Iterable[Sensor]:
        '''Return the sensors attached to this agent.

        :returns: the sensors'''
        return self._sensors


    # ---------- Position ----------

    def position(self) -> Position:
        '''Returns the agent's position.

        :returns: the agent's position'''
        return self._position


    def isMoving(self) -> bool:
        '''test if the agent is moving. This is always False for "normal" agents.

        :returnsd: True if the agent is moving'''
        return False


    def boundingBox(self) -> BoundingBox:
        '''Return the bounding box for this agent.

        By default the bounding box of an agent is the union of the
        fields of view of all attached sensors.

        :returns: the bounding box or None'''
        if self.isPositioned():
            bb = BoundingBox(self._position)
            for s in self.sensors():
                if bb is None:
                    bb = s.fieldOfView()
                else:
                    bb = bb.union(s.fieldOfView())
            return bb
        else:
            return None


    def setPosition(self, p: Position):
        '''Set the agent's static position.

        :param p: the position'''
        self._position = p
        if p is None:
            self.playground().removeAgentBoundingBox(self)
        else:
            self.playground().setAgentBoundingBox(self, self.boundingBox())


    def isPositioned(self, fatal = False)-> bool:
        '''Test whether the agent has a position.

        :param fatal: (optional) if True, raise an exception is agent has no position (defaults to False)'''
        if self._position is not None:
            return True
        else:
            if fatal:
                raise ValueError(f'Agent {self.id()} is not positioned')
            else:
                return False


    def distanceTo(self, a: 'Agent') -> float:
        '''Return the distance to another agent.

        :param a: the other agent
        :returns: the distance to that agent'''
        return distanceBetween(self.position(), a.position())


    # ---------- Behaviour ----------

    def setUp(self, pg: 'SensorPlayground'):
        '''Set up the agent within a simulation. This will typically
        involve the agent posting an event. Sub-classes should call
        this method before performing their own actions.

        :param pg: the playground'''
        self._playground = pg


class MobileAgent(Agent):
    '''A mobile agent in a simulation.

    Mobile agents can have a static position and can also be moved.
    Their position is sensitive to the motions they engage in.

    :param id: the agent's identifier (defaults to a unique number)

    '''

    def __init__(self, id: Any = None):
        super().__init__(id)
        self._trajectory: Trajectory = None


    # ---------- Motion ----------

    def trajectory(self) -> Trajectory:
        '''Return the agen't current trajectory. This is None if the agent is not moving.

        :returns: the trajectory'''
        return self._trajectory


    def isPositioned(self) -> bool:
        '''A moving agenrt is positioned if it has a position or a trajetory.

        :returns: True if the agent has a position'''
        return self._position is not None or self._trajectory is not None


    def isMoving(self) -> bool:
        '''Test whether the agent is moving.

        An agent is moving if it doesn't have a static positin but
        does have a trajectory.

        :returns: True if theagent is moving'''
        return self._trajectory is not None


    def position(self) -> Position:
        '''Return the agent's position. This is equivalent to calling
        :math:`positionAt` with the time returned by :meth:`now`.

        :returns: the agent's position'''
        if self.isMoving():
            return self._trajectory.positionAt(self.now())
        else:
            return super().position()


    def setTrajectory(self, j: Trajectory):
        '''Set the trajectory being followed by the agent. This
        posts :meth:`startMotion` and :meth:`endMotion` events
        for the trajectory's interval ends.

        :param j: the trajectory'''
        self._trajectory = j
        (st, et) = j.interval()
        self.playground().postEvent(st, self, s.startMotion)
        self.playground().postEvent(et, self, s.endMotion)


    def isMoving(self, fatal = False) -> bool:
        '''Test whether the agent moving.

        :param fatal: (optional) if True, raise an exception is agent is not moving (defaults to False)'''
        if self._trajectory is not None:
            return True
        else:
            if fatal:
                raise ValueError(f'Agent {self.id()} is not moving')
            else:
                return False


    def moveTo(self, end: Position, dt: float):
        '''Move the agent to a given position, starting now and
        reaching the position over the given time.

        The agent will move linearly to the given position. To use
        more complicated motrion, use a dedicated trajectory sub-class
        and set the motion using :meth:`moveAlong`.

        :param end: the end point
        :param dt: the interval for the motion'''
        now = self.now()
        t = Trajectory(self.position(), now, end, now + dt)
        self.setTrajectory(t)


    # ---------- Events ----------

    def startMotion(self):
        '''Event called when the agent starts moving. This is typically
        posted in reponse to setting the trajectory.'''

        # set the trajector's bounding box
        j = self._trajectory
        jb = j.boundingBox()
        self.playground().setAgentBoundingBox(self, jb)

        # compute intersections with other bounding boxes
        intersecting = self.plaground().allBoundingBoxesIntersecting(jb)

        # post enter events for every entry and exit
        for a in intersecting:
            ab = a.getBoundingBox()

            # entry
            t = j.entersAt(ab)
            self.playground().postEvent(t, a, a.enters)

            # exit
            t = j.exitsAt(ab)
            self.playground().postEvent(t, a, a.leaves)


    def endMotion(self):
        '''Event called when the agent starts moving. This is typically
        posted in reponse to setting the trajectory.'''
        self.playground().removeAgentBoundingBox(self)
