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
from typing import Callable, Iterable, Dict, List, Tuple, Set, Any, Union, Type
from simplicial import Isomorphism
from sensorplayground import Agent, Sensor, Position, BoundingBox


# Events
EventFunction = Callable[[float], None]
Event = Tuple[float, int, Union[Sensor, Agent], EventFunction]


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
        self._indexIds: int = 0
        self._indices: Isomorphism[int, Union[Sensor, Agent]] = Isomorphism()
        self._boundingBoxes: Dict[int, BoundingBox] = dict()

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

    # We use rtree to manage the bounding boxes of agents and sensors,
    # to simplify encounter calculations. Unfortunately rtree insists that
    # the ids associated with the bounding boxes are integers while we
    # want to use arbitrary names (usually strings). So we set up an
    # isomoprphism between the two id classes.
    #
    # We also need to keep track of the bounding boxes explicitly so
    # we can delete them.

    def _getIndex(self, sa: Union[Sensor, Agent]) -> int:
        '''Return the index used in rtree for the given sensor or agent.

        If no index exists, a new unique one is created.

        :param sa: the sensor or agent
        :returns: the index'''
        if sa in self._indices.reverse:
            # sensor or agent has an index
            i = self._indices.reverse[sa]
        else:
            # sensor/agent is new
            i = self._indexIds
            self._indexIds += 1
            self._indices[i] = sa
        return i


    def _getAgent(self, i: int) -> Union[Sensor, Agent]:
        '''Return the agent associated with the given index.

        This method is used to resolve indices from the spatial tree.

        :param i: the index
        :return: the sensor or agent'''
        return self._indices[i]


    def setAgentBoundingBox(self, sa: Union[Sensor, Agent], bb: BoundingBox):
        '''Set the bounding box for an agent. This is used to
        compute the effects of events.

        :param a: the agent
        :param bb: the bounding box'''
        i = self._getIndex(sa)
        self._boundingBoxes[i] = bb
        self._boxes.insert(i, tuple(bb[0] + bb[1]))


    def removeAgentBoundingBox(self, sa: Union[Sensor, Agent]):
        '''Remove the bounding box for an agent.

        :param a: the agent'''
        i = self._getIndex(sa)
        if i in self._boundingBoxes:
            bb = self._boundingBoxes[i]
            self._boxes.delete(i, tuple(bb[0] + bb[1]))
            del self._boundingBoxes[i]


    # ---------- Search functions ----------

    def allWithinFieldOfView(self, s: Sensor, cls: Type[Agent] = None) -> Iterable[Agent]:
        '''Return all the agents that are potentially observable by a given
        sensor.

        The agents are not necessarily actually observable, as the field of view
        of the sensor may be an approximation of the sensor's actrual field of view.

        The sensor is attached to an agent itself, which is not observed. If an agent
        class is provided, only agents of that class (or one of its sub-classes)
        are observed.

        :param s: the sensor
        :param cls: (optional) the class of agents observed (defaults to all)
        :returns: the agents'''

        # find all possibly observed agents
        fov = s.fieldOfView()
        coords = fov[0] + fov[1]
        possibles = [self._getAgent(i) for i in self._boxes.intersection(coords)]

        # filter-out agents not of the correct class
        if cls is not None:
            possibles = [a for a in possibles if isinstance(a, cls)]

        # filter out observer
        possibles = [a for a in possibles if a != s and a != s.agent()]

        return possibles


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
        ev = [t, id, sa, ef]
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
        def repeat(tc):
            ef(tc)
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
            (t, _, sa, ef) = heappop(self._events)

            # skip the event if it is marked as deleted (not associated
            # with an agent or sensor)
            if sa is None:
                continue

            # advance the simulation time
            self.setSimulationTime(t)

            # execute the event
            ef(t)
            n += 1

        return n
