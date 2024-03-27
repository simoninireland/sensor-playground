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
from typing import List, Union, Any, Iterable, cast
from sensorplayground import Position, TargetCount


class Agent:
    '''An agent in a simulation.

    Agents have position and can be moved. They can also have behaviour that
    is triggered within a simulation.

    :param id: the agent's identifier (defaults to a unique number)
    '''

    # Name generation
    UNIQUE = 0                    #: Source of unique agent ids.


    def __init__(self, id: Any = None):
        if id is None:
            id = Agent.UNIQUE
            Agent.UNIQUE += 1
        self._id: Any = id


    # ---------- Helper methods ----------

    @staticmethod
    def vectorPosition(p: Position) -> numpy.ndarray:
        '''Ensure p is a numpy vector.

        :param p: the position, as a vector or list.
        :returns: the position as a vector'''
        if type(p) is list or type(p) is tuple:
            return numpy.array(p)
        return cast(numpy.ndarray, p)


    @staticmethod
    def distanceBetween(p: Position, q: Position) -> float:
        '''Return the distance between two points. The points must
        have the same dimensions.

        :param p: one position
        :param q: the other position
        :returns: the distance'''
        return float(norm(Agent.vectorPosition(p) - Agent.vectorPosition(q)))


    # ---------- Access ----------

    def position(self) -> Position:
        return self._position


    def setPosition(self, p: Position):
        self._position = p


    def move(self, d: Direction) -> Position:
        if len(self._position) != len(d):
            raise ValueError(f'Direction dimension mismatch ({len(d)} not {len(self._position)})')
        for i in range(len(d)):
            self._position[i] += d[i]
        return self._position


    def distanceTo(self, a: Agent) -> float:
        '''Return the distance to another agent.

        :param a: the other agent
        :returns: the distance to that agent'''
        return Agent.distanceBetween(self.position(), a.position())


    def isPositioned(self, fatal = False)-> bool:
        if self._position is not None:
            return True
        else:
            if fatal:
                raise ValueError(f'Agent {self.id()} is not positioned')
            else:
                return False


    def id(self) -> Any:
        return self._id


    # ---------- Behaviour ----------

    def setUp(self, pg: Playground):
        '''Set up the agent within a simulation. This will typically
        involve the agent posting an event.

        :param pg: the playground'''
        pass
