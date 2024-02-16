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
from sensorplayground import TargetCount


# ---------- Helper types ----------

Position = Union[List[float], numpy.ndarray]


# ---------- Abstract base class of sensors ----------

class Sensor:
    '''A sensor.

    :param id: the sensor's identifier (defaults to a unique number)
    '''

    # Name generation
    UNIQUE = 0   #: Source if unique sensor ids.


    def __init__(self, id: Any = None):
        if id is None:
            id = Sensor.UNIQUE
            Sensor.UNIQUE += 1
        self._id = id


    # ---------- Helper methods ----------

    @staticmethod
    def vectorPosition(p: Position) -> numpy.ndarray:
        '''Ensure p is a numpy vector.

        :param p: the vector, as a vector or list.
        :returns: the vector'''
        if type(p) is list:
            return numpy.array(p)
        return cast(numpy.ndarray, p)


    @staticmethod
    def distanceBetween(p: Position, q: Position) -> float:
        '''Return the distance between two points. The points must
        have the same dimensions.

        :param p: one point
        :param q: the other point
        :returns: the distance'''
        return float(norm(Sensor.vectorPosition(p) - Sensor.vectorPosition(q)))


    # ---------- Access ----------

    def position(self) -> Position:
        return self._position


    def setPosition(self, p: Position):
        self._position = p


    def isPositioned(self, fatal = False)-> bool:
        if self._position is not None:
            return True
        else:
            if fatal:
                raise ValueError(f'Sensor {self.id()} is not positioned')
            else:
                return False


    def id(self) -> Any:
        return self._id


# ---------- Sensors with fixed radii fields ----------

class SimpleSensor(Sensor, TargetCount):
    '''A sensor with a circular or spherical sensing field defined
    by its radius that detects targets within this field.

    For topological reasons the sensor field is an open region, and
    so includes all points at a distance strictly less than the radius.

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
