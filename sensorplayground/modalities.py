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


# There is a circular import between Agent and SensorPlayground at the
# typing level (but not at the execution level), when providing types
# for setUp(). To deal with this we only import SensorPlayground in order
# to type-check Agent, and not for execution. (See
# https://www.stefaanlippens.net/circular-imports-type-hints-python.html)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sensorplayground import Agent


# ---------- Abstract modalities ----------

class Modality:
    '''A sensing modality.

    Modalities are mixin classes defining the interface to a particular
    kind of sensing. They should be applied to objects of type :class:`Sensor`:
    a single sensor class can support multiple modalities.'''

    pass


class Targetting(Modality):
    '''A modality concerned with detecting and tracking targets.

    A "target" is simply an object of interest within the sensor's
    field of attention. Different sub-modalities provide counting,
    distance, and direction measurement.

    '''


    # ---------- Highlevel API ----------

    def detectsTarget(self, t: 'Agent') -> bool:
        '''Test whether a target is detected.

        By default a target marked as detectable by :meth:`canDetectTarget`
        is detected: overriding this method allows for errors in detection.

        This method must be overridden by sub-classes.

        :param q: the target position
        :returns: True if the target is detected'''
        raise NotImplementedError('detectsTarget')



# ---------- Standard targetting modalities ----------

class TargetCount(Targetting):
    '''A target counting modality.'''

    def numberOfTargets(self) -> int:
        '''Return the number of targets the sensor last counted.

        This method must be overridden by sub-classes.

        :returns: the number of targets'''
        raise NotImplementedError('numberOfTargets')


    def countTargetsEvent(self, t: float):
        '''Count the targets within range of the sensor.

        This method must be overridden by sub-classes.

        :param t: simulation time (ignored)'''
        raise NotImplementedError('countTargets')


class TargetDistance(Targetting):
    '''A target distance modality.

    This modality assigns a distance to each detected target.
    '''

    def countTargets(self, t: float):
        '''Count the targets within range of the sensor.

        :param t: simulation time (ignored)'''
        raise NotImplementedError('countTargets')


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


class TargetTrigger(Targetting):
    '''A target modality that is triggered by target action.

    This modality defines a trigger that is called by some action of
    the targets in its field of view.
    '''

    def triggeredBy(self, a: 'Agent'):
        '''Perform the trigger action.

        :param a: the target'''
        raise NotImplementedError('trigger')
