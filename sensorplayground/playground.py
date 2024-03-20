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

from heapq import heappush, heappop
from typing import Iterator, Iterable, Callable, Union, List, Tuple
from sensorplayground import Sensor, Target, Position, Modality


# Events
Agent = Union[Sensor. Target]
EventFunction = Callable[[Agent, float], None]
Event = Tuple[float, int, Callable[[], None]]


class SensorPlayground:
    '''A field of sensors, targets, and other elements, coupled with a
    discrete-event simulator.

    '''


    def __init__(self):
        # state
        self._sensors: List[Sensor] = []
        self._targets: List[Target] = []

        # simulation
        self._simulationTime: float = 0
        self._maximumSimulationTime: float = 10000
        self._events: List[Event] = []
        self._eventId: int = 0


    # ---------- Sensor management ----------

    def addSensor(self, s: Sensor, p: Position):
        '''Insert a sensor into the playground at the given position.

        :param s: the sensor
        :param p: the sensor position'''
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


    # ---------- Target management ----------

    def addTarget(self, t: Target, p: Position):
        '''Insert a targetinto the playground at the given position.

        :param t: the target
        :param p: the target's initial position'''
        self._targets.append(t)
        t.setPosition(p)


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


    # ---------- Discrete-event simulation ----------

    def now(self) -> float:
        '''Return the current simulation time.

        :returns: the current simulation time'''
        return self._simulationTime


    def setSimulationTime(self, t: float):
        '''Set the current simulation time. This is called automatically
        from :meth:`run`, meaning it can be overridden to provide logging
        or other functions.

        :param t: the simulation time'''
        self._simulationTime = t


    def maximumSimulationTime(self) -> float:
        '''Return the maximum permitted simulation time.

        :returns: the maximumsimulation time'''
        return self._maximumTime


    def setMaximumSimulationTime(self, t: float):
        '''Set the maximum permitted simulation time.

        :param t: the maximum simulation time'''
        self._maximumTime = t


    def newEvent(self) -> int:
        '''Return a new, unique, event identifier.

        :returns: a unique identifier'''
        id = self._eventId
        self._eventId += 1
        return id


    def postEvent(self, a: Agent, t: float, ef: EventFunction) -> int:
        '''Post an event for a specific time.

        :param a: the agent
        :param t: the simulation time
        :param ef: the event function
        :returns: an event id'''

        # sanity checks
        if t < self.now():
            raise ValueError(f'Event posted for the past (t={t})')

        # insert the event into the right place in the event queue
        id = self.newEvent()
        ev = [t, id, (lambda: ef(t, a))]
        heappush(self._events, ev)
        return id


    def postEventIn(self, a: Agent, dt: float, ef: EventFunction) -> int:
        '''Post an event for a time relative to now.

        :param a: the agent
        :param dt: the interval
        :param ef: the event function
        :returns: an event id'''
        return self.postEvent(a, self.now() + dt, ef)


    def postRepeatingEvent(self, a: Agent, t: float, dt: float, ef: EventFunction) -> int:
        '''Post an event for a time in the fiture that then
        repoeates at a fixed interval.

        :param a: the agent
        :param t: the first event time
        :param dt: the interval
        :param ef: the event function'''

        # event function to fire an event and then re-schedule it
        def repeat(a, tc):
            ef()
            self.postEvent(a, tc + dt, repeat)

        self.postEvent(a, t, repeat)


    def hasEvents(self) -> bool:
        '''True if there are events to run and the maximum
        simulation time has not been exceeded.

        :returns: True if there are events left to run'''
        return len(self._events) > 0 and self.now() < self._maximumTime


    def run(self) -> int:
        '''Run the simulation.

        :returns: the number of events executed'''
        n = 0
        while self.hasEvents():
            # extract the next event
            (t, _, ef) = heappop(self._events)

            # advance the simulation time
            self.setSimulationTime(t)

            # execute the event
            ef()
            n += 1

        return n
