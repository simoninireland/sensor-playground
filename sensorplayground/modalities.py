# Sensor modalities
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

from typing import Iterable
from sensorplayground import Position, Direction


# ---------- Abstract modalities ----------

class Modality:
    '''A sensing modality'''

    pass


class Targetting(Modality):
    '''A modality concerned with detecting and tracking tagrets.

    A "target" is simply an object of interest within the sensor's
    field of attention. Differenmt sub-modalities provide counting,
    distance, and direction measurement.

    '''


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


# ---------- Standard targetting modalities ----------

class TargetCount(Targetting):
    '''A target counting modality.'''

    def counts(self, ts: Iterable[Position]) -> int:
        '''Return the number of targets in ts that this sensor counts.

        :param ts: the target positions
        :returns: the count'''
        return len(list(self.detects(ts)))


class TargetDistance(Targetting):
    '''A target distance modality.

    This modality assigns a distance to each detected target.
    '''

    def distanceTo(self, ts: Iterable[Position]) -> Iterable[float]:
        '''Return the distances xto the targets detected by
        this sensor, or None if the target is not detected.

        :param ts: the targets
        :returns: the distances'''
        raise NotImplementedError('distanceTo')


class TargetDirection(Targetting):
    '''A target direction modality.

    This modality assigns a direction to each detected target.
    '''

    def directionsTo(self, ts: Iterable[Position]) -> Iterable[Direction]:
        '''Return the directions to the targets detected by
        this sensor, or None if the target is not detected.

        :param ts: the targets
        :returns: the directions'''
        raise NotImplementedError('directionTo')
