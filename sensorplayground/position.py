# Agents, the base class for sensors and targets
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

import numpy
from numpy.linalg import norm
from typing import List, Union, Tuple, cast


# ---------- Positions and helper functions ----------

# Positions in 2- or 3-space
Position = Union[List[float], numpy.ndarray]


# Directions
Direction = float


def haveSameDimensions(p1: Position, p2: Position, fatal: bool = True):
    '''Check that the points have the same dimensions.
    If fatal is True(the defaulrt), raise a ValueError.

    :param p1: the first point
    :param p2: the second point:
    :param fatal: (optional) raise exception on failure (defaults to True)
    :returns: True if the points have the same dimension'''
    if len(p1) == len(p2):
        return True
    else:
        if fatal:
            raise ValueError(f"Points {p1} and {p2} have different dimensions")
        else:
            return False


def vectorPosition(p: Position) -> numpy.ndarray:
    '''Ensure p is a numpy vector.

    :param p: the position, as a vector or list.
    :returns: the position as a vector'''
    if type(p) is list or type(p) is tuple:
        return numpy.array(p)
    return cast(numpy.ndarray, p)


def distanceBetween(p: Position, q: Position) -> float:
    '''Return the distance between two points. The points must
    have the same dimensions.

    :param p: one position
    :param q: the other position
    :returns: the distance'''
    return float(norm(vectorPosition(p) - vectorPosition(q)))


# ---------- Bounding boxes ----------

class BoundingBox:
    '''A pessimistic estimate of the area or volume covered by something.

    A bounding box may have zero extent in all directions, and
    therefore represent a point; it can also have zero extent in one or
    more dimensions, for example to support motion along an axis.

    A bounding box is an open area: it doesn't include its boundary. However,
    it it's just a point, it does contain that point.

    :param c1: one corner position
    :param c2: (optional) the other corner position'''

    def __init__(self, c1: Position, c2: Position = None):
        # if we have two corners, they have to have the same dimensions
        if c2 is not None:
            haveSameDimensions(c1, c2)

        if c2 is None or c1 == c2:
            # if the second corner is missing or the same as the first,
            # the box is a point
            self._topRight = c1
            self._bottomLeft = c1
        else:
            # compute the bounding box from the two corners
            self._topRight: Position = []
            self._bottomLeft: Position = []
            for d in range(len(c1)):
                self._topRight.append(max(c1[d], c2[d]))
                self._bottomLeft.append(min(c1[d], c2[d]))


    # ---------- Access ----------

    def dimension(self) -> int:
        '''Returns the dimension of the bounding box.

        :returns the number of dimensions'''
        return len(self._topRight)


    def corners(self) -> Tuple[Position, Position]:
        '''Return the two corners of the bounding box.

        :returns: a pair of corners'''
        return (self._bottomLeft, self._topRight)


    def isPoint(self) -> bool:
        '''Test if the bounding box is just a point.

        :returns: True if the bounding box contains only a single point'''
        return (self._bottomLeft == self._topRight)


    # ---------- Tests ----------

    def contains(self, p: Position) -> bool:
        '''True if the given point is within the bounding box.

        The bounding box doesn't contain its boundary *unless* it
        is either a point (in  which case this is a test for equality
        weith that point) *or* it has zero depth in some dimension
        (indicating motion along an axis).

        It's possible this definition will change in future to
        include the box's boundary as well as its interior
        (describing a closed region instead of an open one, in
        other words).

        :param p: the point to test
        :returns: True if the point is within the bounding box'''
        haveSameDimensions(self._topRight, p)

        for d in range(len(p)):
            if self._topRight[d] == self._bottomLeft[d]:
                # zero depth in this dimension
                if p[d] != self._topRight[d]:
                    return False
            else:
                if p[d] >= self._topRight[d] or p[d] <= self._bottomLeft[d]:
                    return False
        return True


    def __contains__(self, p: Position) ->bool:
        '''Test if the point is within the bounding box.

        This is equivalent for :meth:`contains`.

        :param p: the point to test
        :returns: True if the point is within the bounding box'''
        return self.contains(p)


    # ---------- Operations ----------

    def union(self, bb: 'BoundingBox') -> 'BoundingBox':
        '''Return a new bounding box that is the union of
        the receiver and the given box.

        The two boxes must have the same dimension.

        :param bb: the other box
        :returns: the union of the two boxes'''
        d = self.dimension()
        bd = bb.dimension()
        if d != bd:
            raise ValueError(f"Bounding boxes have different dimensions ({d} and {bd})")

        # compute the bounding box from the two corners
        tr: Position = []
        bl: Position = []
        (bl1, tr1) = self.corners()
        (bl2, tr2) = bb.corners()
        for d in range(len(tr1)):
            tr.append(max(tr1[d], tr2[d]))
            bl.append(min(bl1[d], bl2[d]))
        return BoundingBox(bl, tr)


# ---------- Trajectories ----------

class Trajectory:
    '''A motion in space.

    A trajectory consists of start and end spacetime points consisting
    of a position and a time. It provides access methods to determine
    a position along the trajectory at any time between these two
    points, and the bounding box of the trajectory.

    By default a trajectory performs linear interpolation between the
    endpoints. Sub-classes can modify this to introduce more complicated
    trajectories, which will involve overriding one or both of :meth:`position`
    and :meth:`boundingBox`.

    :param startp: the starting point
    :param startt: the starting time
    :param endp: the ending point
    :param endt: the ending time

    '''

    def __init__(self,
                 startp: Position, startt: float,
                 endp: Position, endt: float):

        # make sure the positions are equal-dimensional
        if len(startp) != len(endp):
            raise ValueError(f'Endpoints have different dimensions ({len(startp)} vs {len(endp)})')

        # check times
        if startt >= endt:
            raise ValueError(f'Trajectory start time ({startt}) is later than its end time ({endt})')

        self._startp = startp
        self._startt = startt
        self._endp = endp
        self._endt = endt


    # ---------- Access ----------

    def interval(self) -> Tuple[float, float]:
        '''Return the interval between start and end times.

        :returns: the pair of start and end times'''
        return (self._startt, self._endt)


    def endpoints(self) -> Tuple[Position, Position]:
        '''Return the start and end points of the trajectory.

        :returns: the start and end points'''
        return (self._startp, self._endp)


    def isWithinInterval(self, t: float, fatal: bool = False) -> bool:
        '''Check that t is within the motion interval for the trajectory,

        If fatal is true an exception is raised if the time
        lies outwith the interval.

        :param t: the time
        :param fatal: (optional) raise an exception if outside (defaults to False)
        :returns: True if t lies within the motion interval'''
        (s, e) = self.interval()
        if t < s or t > e:
            if fatal:
                raise ValueError(f'Requesting a position at tiem {t} outside the motion interval ({s}, {e})')
            else:
                return False
        else:
            return True


    def isWithinBoundingBox(self, p: Position, fatal: bool = False) -> bool:
        '''Check that the given position lies with the trajectory's
        bounding box.

        If fatal is true an exception is raised if the point
        lies outwith the box.

        :param p: the position
        :param fatal: (optional) raise an exception if outside (defaults to False)
        :returns: True if o lies within the bounding box'''
        bb = self.boundingBox()
        if p not in bb:
            if fatal:
                raise ValueError('Point lies outside bounding box')
            else:
                return False
        return True


    # ---------- Interpolation ----------

    def positionAt(self, t: float) -> Position:
        '''Return the interpolated position along the trajectory at the given time.

        The default is constant linear motion, which may be overridden
        by sub-classes.

        An exception is raised if t lies outside the motion interval.

        :param t: the simulation time
        :returns: the interpolated position'''

        # check time
        self.isWithinInterval(t, fatal=True)

        # linearly interpolate the motion
        (s, e) = self.interval()
        dt = t / (e - s)
        p = [self._startp[i] + (self._endp[i] - self._startp[i]) * dt for i in range(len(self._startp))]
        return p


    def advanceTo(self, t: float):
        '''Move along the trajetory to the point indicated by
        the given time.

        :param t: the new time'''
        self._startp = self.positionAt(t)
        self._startt = t


    def boundingBox(self) -> BoundingBox:
        '''Return the bounding box for the trajectory.

        By default this is bounded by the endpoints, which
        may be overridden by sub-classses.

        :returns: the bounding box'''
        return BoundingBox(self._startp, self._endp)


    def entersLeavesAt(self, bb: BoundingBox) -> Tuple[float, float]:
        '''Return the time at which the agent following this trajectory
        will enter and leave the given bounding box.

        For the time being we assume this is the first time for both.

        :param bb: the bounding box
        :returns: the time'''

        # compute all the times
        dt = (self._endt - self._startt)
        cs = bb.corners()
        bd = len(cs[0])
        ts = []
        for d in range(bd):
            for i in range(len(cs)):
                t = (cs[0][i] - self._startp[d]) / dt
                ts.append(t)

        # entry time is the smallest positive time, exit is the next largest
        sts = [t for t in ts if t >= 0]
        sts.sort()
        return (sts[0], sts[1])
