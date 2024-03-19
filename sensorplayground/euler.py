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
from typing import Iterable, Dict, cast
from sensorplayground import Sensor, TargetCount, SensorPlayground, Position
from simplicial import SimplicialComplex, Simplex, SimplicialFunction, InferredSFRepresentation, EulerIntegrator


# ---------- Minimum-of-faces metric ----------

class FaceMin(SimplicialFunction[int]):
    '''A simplicial function that assigns to a simplex the minimum of
    the values assigned to its faces. The values assigned to 0-simplices
    must be set explicitly. By constructionthis is a valid metric
    for Euler integration.

    :param c: the complex'''

    @staticmethod
    def minimumValueOfFaces(sf, c, s):
        '''Return the minimum of the values assigned face of the given simplex.

        :param sf: the function (self)
        :param c: the complex
        :param s: the simplex
        :returns: the value'''
        return min([sf[f] for f in c.faces(s)])


    # We use an inferred representation to let us set explicit values
    # for simplices, with an inference function that fills-in the
    # values not explicitly set for other simplces.

    def __init__(self, c: SimplicialComplex = None):
        rep = InferredSFRepresentation(FaceMin.minimumValueOfFaces)
        super().__init__(c, rep=rep)


    def setValueForSimplex(self, s: Simplex, v: int):
        '''Only allow values to be set for 0-simplices (sensors).

        :param s: the 0-simplex
        :param v: the value'''
        if self.complex().orderOf(s) == 0:
            super().setValueForSimplex(s, v)
        else:
            raise ValueError(f'Trying to set the value of higher simplex {s}')


# ---------- The estimator ----------

class EulerEstimator:
    '''An Euler integral overhearing structure and estimator. This
    counts targets using Euler characteristic integration over
    a simplicial function defining the "heights" of simplices,
    which must be integers.

    :param pg: the playground
    :param sf: (optional) the metric function (defaults to :class:`FaceMin`)
    '''


    def __init__(self, pg: SensorPlayground, sf: SimplicialFunction[int] = None):
        self._playground = pg
        if sf is None:
            sf = FaceMin()
        self._f = sf
        self._c = self._build()


    def _build(self) -> SimplicialComplex:
        '''Build the overhearing structure for a set of sensors.

        The structure consists of a k-simplex for every set of (k + 1)
        sensors whose sensor fields mutually overlap. Only sensors
        having the :class:`TargetCount` modality are included

        '''

        c = SimplicialComplex()

        # extract the target counters
        ss = self._playground.allSensorsWithModality(TargetCount)

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

        # set the overhearing structure as the complex underlying the height function
        self._f.setComplex(c)

        # return the overhearing structure
        return c


    def overhearing(self) -> SimplicialComplex:
        '''Return the overhearing complex.

        :returns: the complex'''
        if self._c is None:
            self.rebuild()
        return self._c


    def metric(self) -> SimplicialFunction[int]:
        '''Return the metric function.

        :returns: the function'''
        return self._f


    def rebuild(self):
        '''Rebuild the overhearing structure. Needed if the underlying
        playground has changed.'''
        self._c = self._build()


    def setCounts(self, cs: Dict[Sensor, int]):
        '''Set the counts observed at all the sensors. If a sensor
        appears more than once in the iteration, the last value is the
        one that's assigned. The metric function is responsible
        for computing the values of non-sensor higher simplices.

        :param ss: the sensors
        :param cs: the counts

        '''

        # set the observed counts
        sf = self.metric()
        for s in cs:
            sf[s.id()] = cs[s]


    def estimateFromCounts(self, cs: Dict[Sensor, int]) -> int:
        '''Estimate the total target count from the counts observed
        at all the sensors. Any sensors not given a count are assumed
        to count zero.

        :param ss: the sensors
        :param cs: the counts
        :returns: the estimated target count'''

        # set the counts
        self.setCounts(cs)

        # integrate the Euler characteristics
        integrator = EulerIntegrator()
        count = integrator.integrate(self.overhearing(), self.metric())

        return count


    def estimateFromTargets(self, ts: Iterable[Position]) -> int:
        '''Estimate the count of a collection of targets.

        The estimator computes the counts at each sensor from
        the target positions.

        One simple error measure is the fraction by which the estimate
        differs from the (known) actual number of targets.

        :param ts: the targets
        :returns: the estimated target count'''

        # compute the counts at each sensor
        cs = {}
        for s in self._playground.allSensorsWithModality(TargetCount):
            cs[s] = cast(TargetCount, s).counts(ts)

        # compute the estimate
        return self.estimateFromCounts(cs)
