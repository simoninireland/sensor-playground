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


# ---------- Helper types ----------

Position = Union[List[float], numpy.ndarray]


# ---------- Abstract base class of sensors ----------

class Sensor:
    '''A sensor.

    :param p: (optional) the position of the sensor
    :param id: the sensor's identifier (defaults to a unique number)
    '''

    UNIQUE = 0   #: Source if unique sensor ids.


    def __init__(self, p: Position = None, id: Any = None):
        self._position = p
        if id is None:
            id = Sensor.UNIQUE
            Sensor.UNIQUE += 1
        self._id = id


    # ---------- Helper methods ----------

    def _vectorify(self, p: Position) -> numpy.ndarray:
        '''Ensure p is a numpy vector.

        :param p: the vector, as a vector or list.
        :returns: the vector'''
        if type(p) is list:
            return numpy.array(p)
        return cast(numpy.ndarray, p)


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


    # ---------- Subclass API ----------

    def canDetectTarget(self, q: Position) -> bool:
        '''Test whether the sensor can detect a target at posiiton q.

        :param q: the position of the target
        :return: True if the target is detectable by this sensor'''
        raise NotImplementedError('canDetectTarget')


    def isOverlappingWith(self, s: 'Sensor') -> bool:
        '''Test whether this sensor's detections overlap with another's.

        This entirely depends on calculations in sub-classes. Different
        sub-clasess may or may not be able to compute overlapping with
        each other.

        :param s: the other sensor
        :returns True if the two sensors overlap'''
        raise NotImplementedError('isOverlappingWith')


    # ---------- Highlevel API ----------
    # (Constructed from the subclassed operations)

    def detectsTarget(self, q: Position) -> bool:
        '''Test whether a target at position q is detected.

        By default a target marked as detectable by :meth:`canDetectTarget`
        is detected: overriding this method allows for errors in detection.

        :param q: the target position
        :returns: True if the target is detected'''
        return self.canDetectTarget(q)


    def detects(self, ts: Iterable[Position]) -> Iterable[Position]:
        '''Return the targets in ts that this sensor detects.
        :param ts: the target positions
        :returns: the count'''
        return [t for t in ts if self.detectsTarget(t)]


    def counts(self, ts: Iterable[Position]) -> int:
        '''Return the number of targets in ts that this sensor counts.

        :param ts: the target positions
        :returns: the count'''
        return len(list(self.detects(ts)))


# ---------- Sensors with fixed radii fields ----------

class SimpleSensor(Sensor):
    '''A sensor with a circular or spherical sensing field defined
    by its radius.

    For topological reasons the sensor field is an open region, and
    so includes all points at a distance strictly less than the radius.

    :param p: (optional) the sensor position
    :param r: the sensing field radius (defaults to 1.0)'''

    def __init__(self, p: Position = None, r: float = 1.0, id: Any = None):
        super().__init__(p, id)
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
            d = float(norm(self._vectorify(self.position()) - self._vectorify(s.position())))
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
        d = float(norm(self._vectorify(self.position()) - self._vectorify(q)))

        return d < self.detectionRadius()
