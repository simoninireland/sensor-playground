# Sensor playground
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

from typing import Iterator, Iterable, Callable
from sensorplayground import Sensor, Position, Modality


class SensorPlayground:
    '''A field of sensors.

    '''


    def __init__(self):
        self._sensors = []


    # ---------- Sensor management ----------

    def addSensor(self, s: Sensor, p: Position):
        '''Insert a sensor into the playground at the given position.

        :param s: the sensor
        :param p: tghe sensor position'''
        self._sensors.append(s)
        s.setPosition(p)


    def __len__(self) -> int:
        '''Return the number of sensors in the playground.

        :returns: the number of sensors'''
        return len(self._sensors)


    def __iter__(self) -> Iterator[Sensor]:
        '''Return an iteratror over the sensors.

        :returns: self (the iterator)'''
        for s in self._sensors:
            yield s


    # ---------- Search functions ----------

    def sensorNearestTo(self, p: Position) -> Sensor:
        '''Return the sensor nearest to the given position.

        :param p: the position
        :returns: the nearest sensor, or None if there are no sensors'''
        pos = Sensor.vectorPosition(p)
        nearest = 0
        nearest_s = None
        for s in self:
            if s.isPositioned():
                if nearest_s is None:
                    nearest_s = s
                else:
                    d = Sensor.distanceBetween(s.position(), pos)
                    if d < nearest:
                        nearest_s = s
                        nearest = d
        return nearest_s


    def allSensors(self, p: Callable[[Sensor], bool]) -> Iterable[Sensor]:
        '''Return all sensors for which the precicate is true.

        :param p: the predicate
        :returns: the passing sensors'''
        return [s for s in self if p(s) ]


    def allSensorsWithModality(self, m: type) -> Iterable[Modality]:
        '''Return all sensors with the given modality. The modality
        should be specified by class, and be a sub-class of :class:`Modality`.

        :param m: the sensor modality
        :returns: all sensors with that modality'''
        return self.allSensors(lambda s: isinstance(s, m))
