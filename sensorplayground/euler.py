# Euler integration form target counting
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

from itertools import combinations
from typing import Iterable, Dict, Final
from sensorplayground import Sensor,TargetCount, SensorPlayground, Position, zipboth
from simplicial import SimplicialComplex, EulerIntegrator


class EulerEstimator:
    '''An Euler integral overhearing structure and estimator. This
    counts targets using Euler characteristic integration.

    :param pg: the playground
    '''

    COUNT: Final[str] = 'count'   #: Attribute used to hold the count at each sensor simplex.


    def __init__(self, pg: SensorPlayground):
        self._playground = pg
        self._c: SimplicialComplex = None


    def _build(self) -> SimplicialComplex:
        '''Build the overhearing structure for a set of sensors.

        The structure consists of a k-simplex for every set of (k + 1)
        sensors whose sensor fields mutually overlap. Only sensors
        having the :class:`TargetCount` modality are included

        '''

        c = SimplicialComplex()

        # extract the target counters
        ss = [s for s in self._playground if isinstance(s, TargetCount)]

        # add the basis, using the sensors' ids as simplex names
        for s in ss:
            c.addSimplex(id=s.id())

        # add higher simplices
        for k in range(1, len(ss)):
            # track now many k-simplices we create
            created = 0

            # run through all combinations of (k + 1) basis simplices
            for pb in combinations(ss, k + 1):
                pairwise = True

                # check all pairwise distances
                for (i, j) in combinations(pb, 2):
                    if not i.isOverlappingWith(j):
                        # pair is not overlapping, so can't create
                        # a k-simplex from this basis
                        pairwise = False
                        break

                # if all the pairwise distances were overlapping,
                # create the higher simplex on this basis
                if pairwise:
                    bs = [s.id() for s in pb]
                    c.addSimplexWithBasis(bs)
                    created += 1

            # if we created enough k-simplices to potentially build
            # a (k + 1)-simplex, carry on; otherwise we can't build any
            # higher simplices, and so can escape from the loop
            if created < (k + 1) + 1:
                break

        # return the overhearing structure
        return c


    def overhearing(self) -> SimplicialComplex:
        if self._c is None:
            self.rebuild()
        return self._c


    def rebuild(self):
        '''Rebuild the overhearing structure. Needed if the underlying
        playground has changed.'''
        self._c = self._build()


    def clearCounts(self):
        '''Clear all the counts.'''
        c = self.overhearing()
        for s in c.simplices():
            c[s][EulerEstimator.COUNT] = None


    def setCounts(self, cs: Dict[Sensor, int]):
        '''Set the counts observed at all the sensors. Any sensors
        not assigned a count get 0. If a sensor appears more than once
        in the iteration, the last value is the one that's assigned.

        :param ss: the sensors
        :param cs: the counts'''
        self.clearCounts()

        # set the observed counts
        c = self.overhearing()
        for s in cs:
            c[s.id()][EulerEstimator.COUNT] = cs[s]

        # propagate the counts to higher simplices
        for k in range(1, c.maxOrder() + 1):
            for s in c.simplicesOfOrder(k):
                c[s][EulerEstimator.COUNT] = min([c[f][EulerEstimator.COUNT] for f in c.faces(s)])



    def estimateFromCounts(self, cs: Dict[Sensor, int]) -> int:
        '''Estimate the total target count from the counts observed
        at all the sensors. Any senbsors not given a count are assumed
        to count zero.

        :param ss: the sensors
        :param cs: the counts
        :returns: the estimate target count'''

        # set the counts
        self.setCounts(cs)

        # integrate the Euler characteristics
        integrator = EulerIntegrator(EulerEstimator.COUNT)
        count = integrator.integrate(self.overhearing())

        return count


    def estimateFromTargets(self, ts: Iterable[Position]) -> int:
        '''Estimate the count of a collection of targets.

        The estimator computes the counts at each sensor from
        the target positions.

        One simple error measure is the fraction by which the estimate
        differs from the (known) actual number of targets.

        :param ts: the targets
        :returns: the estimated target count'''
        counts = {}

        # compute the counts at each sensor
        for s in self._playground:
            if isinstance(s, TargetCount):
                counts[s] = s.counts(ts)

        # compute the estimate
        return self.estimateFromCounts(counts)
