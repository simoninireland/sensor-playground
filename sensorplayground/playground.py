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
from rtree import index
from typing import Callable, Iterable, Dict, List, Tuple, Set, Any, Union
from sensorplayground import Agent, Sensor, Position, BoundingBox


# Events
EventFunction = Callable[[float], None]
Event = Tuple[float, int, Union[Sensor, Agent], Callable[[], None]]


class SensorPlayground:
    '''A field of sensors, targets, and other elements, coupled with a
    discrete-event simulator.

    :param d: (optional) the dimensions of the playground (2 or 3) (defaults to 2)
    '''


    MAXIMUM_TIME = 10000    #: Default maximum simulation time.


    def __init__(self, d: int = 2):
        # state
        self._agents: Set[Agent] = set()
        self._agentIds: Dict[Any, Agent] = dict()

        # locations tree
        p = index.Property()
        p.dimension = d
        self._boxes: index.Index = index.Index(properties=p)
        self._boxes.interleaved = True

        # simulation
        self._simulationTime: float = 0
        self._maximumSimulationTime: float = SensorPlayground.MAXIMUM_TIME
        self._events: List[Event] = []
        self._eventId: int = 0


    # ---------- Agent management ----------

    def addAgent(self, a: Agent):
        '''Add an agent to the playground.

        :param a: the agent'''
        self._agents.add(a)
        self._agentIds[a.id()] = a

        # set up the agent within the playground
        a.setUp(self)


    def removeAgent(self, aid: Union[Agent, Any]):
        '''Remove an agent and any events associated with it.

        :param aid: the agent or agent id'''

        # disambiguate
        id = aid.id() if isinstance(aid, Agent) else aid
        a = self._agentIds[id]

        # remove the agent
        self._agents.remove(a)
        del self._agentIds[id]

        # remove associated events (mark as associated with no agent)
        self._events = [(t, id, (None if eva == a else eva), ef) for (t, id, eva, ef) in self._events]


    def getAgent(self, id: Any) -> Agent:
        '''Retrieve the agent with the given id.

        A KeyError will be raised if there is no such agent in the playground.

        :param id: the agent id
        :returns: the agent'''
        return self._agentIds[id]


    def agents(self) -> Iterable[Agent]:
        '''Return the agents in the playground.

        :returns: the agents'''
        return self._agents


    # ---------- dict interface ----------

    # There is no __setitem__() as it sits awkwardly with the use of agents in addAgent()


    def __getitem__(self, id: Any) -> Agent:
        '''Get an agent by id.

        This is equivalent to calling :meth:`getAgent`.

        :param id: the agent id
        :returns: the agent'''
        return self.getAgent(id)


    def __contains__(self, id: Any) -> bool:
        '''Test whether the agent is in the playground.

        :param id: the agent id
        :returns : True if the playground contains this agent'''
        return id in self._agentIds


    # ---------- Location functions ----------

    def setAgentPosition(self, a: Agent, bb: BoundingBox):
        '''Set the bounding box for an agent. This is used to
        compute the effects of events.

        :param a: the agent
        :param bb: the bounding box'''
        self._boxes.insert(a.id(), bb[0] + bb[1])


    # ---------- Search functions ----------

    def allWithinBoundingBox(self, bb: BoundingBox) -> Iterable[Agent]:
        '''Return all the egents that are potentially observable by a sensor
        with the given field of view bounding box.

        The agents are not necessarily actually observable, as the bounding box
        may be an approximation of the sensor's actrual field of view.

        :param bb: the bounding box of the field of view
        :returns: the agents'''

        # TBD -- return all agents for now
        return self.agents()



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


    def _newEvent(self) -> int:
        '''Return a new, unique, event identifier.

        :returns: a unique identifier'''
        id = self._eventId
        self._eventId += 1
        return id


    def postEvent(self, sa: Union[Sensor, Agent], t: float, ef: EventFunction) -> int:
        '''Post an event for a specific time.

        :param sa: the sensor or agent the event is occurs on
        :param t: the simulation time
        :param ef: the event function
        :returns: an event id'''

        # sanity checks
        if t < self.now():
            raise ValueError(f'Event posted for the past (t={t})')

        # insert the event into the right place in the event queue
        id = self._newEvent()
        ev = [t, id, sa, (lambda: ef(t))]
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
            ef(a, tc)
            self.postEvent(a, tc + dt, repeat)

        return self.postEvent(a, t, repeat)


    def hasEvents(self) -> bool:
        '''True if there are events to run and the maximum
        simulation time has not been exceeded.

        :returns: True if there are events left to run'''
        return len(self._events) > 0 and self._simulationTime < self._maximumSimulationTime


    def run(self) -> int:
        '''Run the simulation.

        :returns: the number of events executed'''
        n = 0
        while self.hasEvents():
            # extract the next event
            (t, _, a, ef) = heappop(self._events)

            # skip the event if it is marked as deleted (not associated
            # with an agent)
            if a is None:
                continue

            # advance the simulation time
            self.setSimulationTime(t)

            # execute the event
            ef()
            n += 1

        return n
