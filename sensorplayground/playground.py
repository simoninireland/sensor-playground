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
    simulation loop.

    Simulation times are a sequence of integers.

    :param d: (optional) the dimensions of the playground (2 or 3) (defaults to 2)
    '''


    MAXIMUM_TIME = 10000.0   #: Default maximum simulation time.


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
        self._simulationTime: float = 0.0
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


    def __del__(self, aid: Union[Agent, Any]):
        '''Delete an agent. This is equivalent to :meth:`removeAgent`.

        :param aid: the agent or agent id'''
        self.removeAgent(aid)


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

    def _rtreeBoundingBox(self, bb: BoundingBox) -> List[float]:
        '''Turn a bounding box into a list of or-ordinates
        as required by rtree.

        :param bb: the bounding box:
        :returns: the list of edge co-ordinates'''
        (bl, tr) = bb.corners()
        return list(bl) + list(tr)


    def _getAgent(self, i: int) -> Union[Sensor, Agent]:
        '''Return the agent associated with the given index.

        This method is used to resolve indices from the spatial tree.

        :param i: the index
        :return: the sensor or agent'''
        return self._indices[i]


    def setAgentBoundingBox(self, a: Agent, bb: BoundingBox):
        '''Set the bounding box for an agent. This is used to
        compute the effects of events.

        :param a: the agent
        :param bb: the bounding box'''
        i = self._getIndex(a)
        self._boundingBoxes[i] = bb
        self._boxes.insert(i, self._rtreeBoundingBox(bb))


    def removeAgentBoundingBox(self, sa: Union[Sensor, Agent]):
        '''Remove the bounding box for an agent.

        :param a: the agent'''
        i = self._getIndex(sa)
        if i in self._boundingBoxes:
            bb = self._boundingBoxes[i]
            self._boxes.delete(i, self._rtreeBoundingBox(bb))
            del self._boundingBoxes[i]


    # ---------- Search functions ----------

    def allAgentsWithinFieldOfView(self,
                                   s: Sensor,
                                   cls: Type[Agent] = None) -> Iterable[Agent]:
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
        coords = s.position()
        observables= [self._getAgent(i) for i in self._boxes.intersection(coords)]

        # filter-out agents not of the correct class
        if cls is not None:
            observables = [a for a in observables if isinstance(a, cls)]

        # filter out observer
        possibles = [a for a in observables if a != s and a != s.agent()]

        return possibles


    def allBoundingBoxesIntersecting(self,
                                     bb: BoundingBox) -> Iterable[Agent]:
        '''Return all the agents whose bnounding boxes currently
        intersect with the given one.

        :param bb: the bounding box
        :returns: a list of intersecting agents'''
        intersecting = [self._getAgent(i) for i in self._boxes.intersection(self._rtreeeBoundingBox(bb))]
        return intersecting


    def allSensorsObserving(self,
                            a: Agent,
                            cls: Type[Sensor] = None) -> Iterable[Sensor]:
        '''Return all the sensors that can observe an event on the given
        agent.

        The sensors won't necessarily observe the event, as this will
        depend on the observability of the given agent. by that sensor.

        If the agent also has sensors of a potentially observing type attached
        to it, they will be returned as well.

        :param a: the agent
        :param cls: (optional) the class of sensor making the observations
        :returns: the sensors

        '''
        p = a.position()

        # find all agents in whose bounding box we sit
        coords = tuple(p + p)
        possibleAgents = [self._getAgent(i) for i in self._boxes.intersection(coords)]
        print(possibleAgents)

        # extract all sensors from these agents
        ss = [a.sensors() for a in possibleAgents]
        possibleSensors = set.union(*ss)

        # reduce by type
        if cls is not None:
            possibleSensors = [s for s in possibleSensors if isinstance(s, cls)]

        return possibleSensors


    # ---------- Events ----------

    def _newEventId(self) -> int:
        '''Return a new, unique, event id.

        :returns: an event id'''
        self._eventId += 1
        return self._eventId


    def postEvent(self, t: float, sa: Union[Sensor, Agent], f: EventFunction):
        '''Postan event for the given time.

        :param t: the event time (must be in the future)
        :param sa: the agent or sensor that will receive the event
        :param f: the event functionto be called'''
        ev = [t, self._newEventId(), sa, f]
        heappush(self._events, ev)


    def _isDeletedEvent(self, ev: Event) -> bool:
        '''Test if an event has been deleted. A deleted event
        has its target set to None.

        We need this because it's awkward/impossible to delete an
        element from a heap. So we leave them there but mark them as dead.

        :param ev: the event
        :returns: True if the event has been deleted'''
        return ev[2] is None


    def _markEventAsDeleted(self, ev: Event):
        '''Mark the event as deleted by resetting is target to None.

        :param ev: the event'''
        ev[2] = None


    def nextEvent(self,) -> Event:
        '''Pop the next event and return it.

        :returns: the next event'''
        while len(self._events) > 0:
            ev = heappop(self._events)
            if not self._isDeletedEvent(ev):
                return ev

        # if we get here there are no events left
        return None


    # ---------- Discrete-event simulation ----------

    def now(self) -> int:
        '''Return the current simulation time.

        :returns: the current simulation time'''
        return self._simulationTime


    def setSimulationTime(self, t: float):
        '''Set the current simulation time. This is called automatically
        from :meth:`run`, meaning it can be overridden to provide logging
        or other functions.

        :param t: the simulation time'''
        self._simulationTime = t


    def setMaximumSimulationTime(self, t: float):
        '''Set the maximum permitted simulation time.

        :param t: the maximum simulation time'''
        self._maximumTime = t


    def run(self) -> int:
        '''Run the simulation.

        :returns: the number of events executed'''
        n = 0
        self._simulationTime = 0
        while self._simulationTime < self._maximumSimulationTime:
            ev = self.nextEvent()
            if ev is None:
                # no more events to handle
                break

            # handle the event
            # TODO: change this to access the list directly -- obscure but faster
            (_, t, sa, f) = ev
            self.setSimulationTime(t)
            f(t)
            n += 1

        return n
