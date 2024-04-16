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
from numpy.linalg import norm
from typing import List, Union, Any, Dict, Iterable, Set, cast
from sensorplayground import Position, distanceBetween, Direction, Trajectory

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
    simulation.

    :param id: (optional) the agent's id

    '''

    # Name generation
    UNIQUE = 0                    #: Source of unique agent ids.


    def __init__(self, id: Any = None):
        if id is None:
            id = f'agent{Agent.UNIQUE}'
            Agent.UNIQUE += 1
        self._id: Any = id
        self._playground: 'SensorPlayground' = None
        self._position: Position = None
        self._sensors: Set['Sensor'] = []
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
        that of the agent as it possibly movbes.

        :param s: the sensor'''
        self._sensors.add(s)
        self._sensorIds[s.id()] = s

        # set the saensor's agent
        s.setAgent(self)


    def removeSensor(self, sid: Union['Sensor', Any]):
        '''Remove a sensor from the agent.

        :param sid: the sensor or its id'''

        # disambiguate
        id = sid.id() if isinstance(sid, 'Sensor') else sid
        s = self._sensorIds[id]

        # remove the agent
        self._sensors.remove(s)
        del self._sensorIds[id]


    # ---------- Position ----------

    def position(self) -> Position:
        '''Returns the agent's position.

        :returns: the agent's position'''
        return self._position


    def setPosition(self, p: Position):
        '''Set the agent's static position.

        :param p: the position'''
        self._position = p


    def isPositioned(self, fatal = False)-> bool:
        '''Test whether the agent is statically positioned, and therefore not moving.

        :param fatal: (optional) if True, raise an exception is agent is not position (defaults to False)'''
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
        involve the agent posting an event. Sub-classes whoulf call
        this method before performing their own actions.

        :param pg: the playground'''
        self._playground = pg



# General agents

class MobileAgent(Agent):
    '''An agent in a simulation.

    Agents have position and can be moved. Their position is sensitive to the motions
    they engage in.

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


    def position(self) -> Position:
        '''Returns the agent's position. This will be the static position if
        the agent has been explicitly positioned, and an interpolated trajectory
        if the agent is moving.

        If the current simulation time is after the end of any motion, the
        agent is statically positioned at the endpoint.

        :returns: the agent's position'''
        if self.isMoving():
            # check whether we've reached the end of the motion
            (_, et) = self._trajectory.interval()
            if et <= self.now():
                # statically position at the end of the motion
                (_, ep) = self._trajectory.endpoints()
                super().setPosition(ep)
                self._trajectory = None
            else:
                # still moving, interpolate the position
                return self._trajectory.position(self.now())

        return super().position()


    def setPosition(self, p: Position):
        '''Set the agent's static position. An agent so positioned
        cannot have a trajectory, and any it does have is cleared.

        :param p: the position'''
        super().setPosition(p)
        self._trajectory = None


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
        super().setPosition(None)
        self._trajectory = t


    def moveAlong(self, t: Trajectory):
        '''Move the agent along the given trajectory.

        The trajectory's start point and time must match the agent's current
        position and the current simulation time. If the agent is moving,
        its position will be interpolated.

        The main use of this method is to use a specific trajectory with
        specific motion interpolation. For linear interpolation, use
        :meth:`moveTo`.

        :param t: the trajectory'''

        # check start point matches agent
        (sp, _) = t.endpoints()
        if sp != self.position():
            raise ValueError('Trajectory starts somewhere else than the agent')
        (st, _) = t.interval()
        if st != self.now():
            raise ValueError('Trajectory starts at another time')

        self._trajectory = t
        super().setPosition(None)
