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


# Positions in 2- or 3-space
Position = Union[List[float], numpy.ndarray]

# Directions
Direction = List[float]


# Bounding boxes for trajectories
BoundingBox = Tuple[Position, Position]


# Distance calculations
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


# Trajectories
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
        '''Return trhe interval between start and end times.

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
        (bl, tr) = self.boundingBox()
        for i in range(len(bl)):
            if p[i] < bl[i] or p[i] > tr[i]:
                if fatal:
                    raise ValueError('Point lies outside bounding box')
                else:
                    return False
        return True


    # ---------- Interpolation ----------

    def position(self, t: float) -> Position:
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


    def boundingBox(self) -> BoundingBox:
        '''Return the bounding box for the trajectory.

        By default this is bounded by the endpoints, which
        may be overridden by sub-classses.

        :returns: the bounding box'''

        # check that the trajectory is grounded at a start point
        if self._startp is None:
            raise ValueError('Trajectory does not have a starting point')

        bl = [0] * len(self._startp)
        tr = [0] * len(self._startp)
        for i in range(len(self._startp)):
            bl[i] = min(self._startp[i], self._endp[i])
            tr[i] = max(self._startp[i], self._endp[i])
        return (bl, tr)
