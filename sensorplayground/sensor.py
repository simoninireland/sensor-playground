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
from sensorplayground import Position, Agent, TargetCount


# ---------- Abstract base class of sensors ----------

class Sensor(Agent):
    '''A sensor.

    :param id: (optional) the sensor's identifier
    '''


    def __init__(self, id: Any = None):
        super().__init__(id)


# ---------- Sensors with fixed radii fields ----------

class SimpleSensor(Sensor, TargetCount):
    '''A sensor with a circular or spherical sensing field defined
    by its radius that detects targets within this field.

    For topological reasons the sensor field is an open region, and
    so includes all points at a distance strictly less than the radius.

    The sensor has no default behaviour, and so will be entirely
    passive in a simulation. To provide autonomous behaviour,
    override :meth:`setUp`.

    :param r: the sensing field radius (defaults to 1.0)
    :param id: (optional) sensor identifier'''


    def __init__(self, r: float = 1.0, id: Any = None):
        super().__init__(id)
        self._detectionRadius = r


    def detectionRadius(self) -> float:
        return self._detectionRadius


    def isOverlappingWith(self, s: Sensor) -> bool:
        '''Compute overlaps with another :class:`SimpleSensor`.

        :param s: the other sensor
        :returns: True if the sensors overlap'''
        if type(s) is SimpleSensor:
            # check we know both positions
            self.isPositioned(fatal=True) and s.isPositioned(fatal=True)

            # check whether the sensor fields overlap
            d = Sensor.distanceBetween(self.position(), s.position())
            return d < self.detectionRadius() + s.detectionRadius()
        else:
            # if the other sensor is not a SimpleSensor, fail
            raise ValueError(f'Can\'t compute overlap with an instance of {type(s)}')


    def canDetectTarget(self, q: Position) -> bool:
        '''Detects a target if it is (strictly) within the sensing field radius.

        :param q: the position of the target
        :return: True if the target is detectable by this sensor'''

        # check we know the positions
        self.isPositioned(fatal=True)

        # distance is simply the 2-norm of the difference
        d = Sensor.distanceBetween(self.position(), q)

        return d < self.detectionRadius()
