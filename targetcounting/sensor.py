# Sensors
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

import numpy
from numpy.linalg import norm
from typing import List, Union, Iterable, cast, override


# ---------- Helper types ----------

Position = Union[List[float], numpy.ndarray]


# ---------- Abstract base class of sensors ----------

class Sensor:
    '''A sensor.

    :param p: the position of the sensor'''

    def __init__(self, p: Position):
        self._position = self._vectorify(p)


    # ---------- Helper methods ----------

    def _vectorify(self, p: Position) -> numpy.ndarray:
        '''Ensure p is a numpy vector.

        :param p: the vector, as a vectore or list.
        :returns: the vector'''
        if type(p) is list:
            return numpy.array(p)
        return cast(numpy.ndarray, p)

    # ---------- Access ----------

    def position(self) -> Position:
        return self._position


    # ---------- Sensing ----------

    def canDetectTarget(self, q: Position) -> bool:
        '''Test whether the sensoir can detect a target at posiiton q.

        :param q: the position of the target
        :return: True if the target is detectable by this sensor'''
        raise NotImplementedError('canDetectTarget')


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

    :param, p: the sensor position
    :param r: the sensing field radius'''

    def __init__(self, p: Position, r: float):
        super().__init__(p)
        self._detectionRadius = r


    def detectionRadius(self) -> float:
        return self._detectionRadius


    @override
    def canDetectTarget(self, q: Position) -> bool:
        '''Detects a target if it is (strictly) within the sensing field radius.

        :param q: the position of the target
        :return: True if the target is detectable by this sensor'''
        d = float(norm(self._vectorify(self.position()) - q))
        return d < self.detectionRadius()
