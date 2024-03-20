# Bird targets and acoustic sensors
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

from numpy import pi, sin, cos
from numpy.rand import rand
from sensorplayground import Sensor, Target, Playground


class Bird(Target):
    '''A bird.

    Actually currently a ridiculously simple one, but this can serve
    as a basis for a more useful one with more stochastic behaviour,
    for example a probability of detection by distance function.
    (This actually depends on the bird *and* the acoustic sensor, so
    maybe should be provided independently?)

    :param leap: the distance the bird moves
    :param dt: the interval between moves
    :param id: (optional) the bird's identifier

    '''

    def __init__(self, leap: float, dt: float, id: Any = None):
        super().__init__(id)
        self._dxy: float = leap
        self._dt = dt


    def _moveRestTweet(self, t: float):
        '''Event function that moves the bird and then lets it tweet.

        :param t: the simulation time (ignored)'''

        # work out the new position
        theta = 2 * pi * rand(1)
        d = [self._dxy * cos(theta), self._dxy * sin(theta)]
        self.move(d)

        # tweet


    def setUp(self, pg: Playground):
        '''Construct the move-rest-tweet cycle.'''
        pg.postRepeatingEvent(self, self._dt, self._dt, self._moveRestTweet)


class AcousticSensor(Sensor, TargetCount):
    '''An acoustic sensor that hears tweets.'''
