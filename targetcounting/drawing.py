# Standard methods for drawing sensor fields
#
# Copyright (C) 2024 Simon Dobson
#
# This file is part of target-counting, an experiment in
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

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from typing import Iterable
from targetcounting import Sensor, Position


def drawField(ss: Iterable[Sensor], ts: Iterable[Position] = None,
              ax = None, backgroundColour = '0.95',
              sensorColour = 'r', sensorMarker = '.', sensorSize = 2,
              fieldColour = 'g', fieldAlpha = 0.2,
              targetColour = 'b', targetMarker = 'x', targetSize = 2,
              showCount = False,
              targetCountColour = 'b', targetCountFontSize = 5):
    '''Draw the sensor field containing the given sensors.

    The sensors are drawn with the sensing fields. The axes
    are configured to remove ticks.

    :param ss: the sensors
    :param ts: the targets (default None)
    :param ax: the axes to draw into (default the current main axes)
    :param backgroundColour: the background colour for the field (default '0.95')
    :param sensorColour: colour to mark the sensor position (default 'r')
    :param sensorMarker: the sensor marker (default '.')
    :param sensorSize: size of the sensor marker (default 2)
    :param fieldColour: colour of the sensor field (default 'g')
    :param fieldAlpha: transparency for the field (default 0.2)
    :param targetColour: colour to mark the sensor position (default 'b')
    :param targetMarker: the sensor marker (default 'x')
    :param targetSize: size of the sensor marker (default 2)
    :param showCount: show the non-zero target count at each sensor (default False)
    :param targetCountColour: colour for the count if shown (default 'b')
    :param targetCountFontSize: font size for the count, if shown (default 5)
    '''

    # full in defaults
    if ax is None:
        ax = plt.gca()

    # sensors
    for s in ss:
        p = s.position()

        # field
        c = Circle(p, radius=s.detectionRadius(),
                  color=fieldColour, alpha=fieldAlpha)
        ax.add_patch(c)

        # sensor position
        ax.plot(p[0], p[1],
               color=sensorColour, marker=sensorMarker, markersize=sensorSize)

    # targets
    if ts is not None:
        # positions
        for t in ts:
            plt.plot([t[0]], [t[1]],
                    color=targetColour, marker=targetMarker, markersize=targetSize)

        # counts
        if showCount:
            for s in ss:
                c = s.counts(ts)
                if c > 0:
                    ax.annotate(f'{c}', s.position(),
                                [0.5, -1], textcoords='offset fontsize',
                                fontsize=targetCountFontSize, color=targetCountColour)

    # configure the axes
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.0])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor(backgroundColour)
