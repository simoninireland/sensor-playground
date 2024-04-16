# Standard methods for drawing sensor fields
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

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from typing import Iterable
from sensorplayground import Agent, Position


def drawField(ss: Iterable[Agent], ts: Iterable[Position] = None,
              ax = None, backgroundColour = '0.95',
              subfieldXY = None, subfieldWH = None,
              showSensors = True,
              sensorColour = 'r', sensorMarker = '.', sensorSize = 2,
              sensorFilled = True, sensorFillColour =  'r',
              showSensorLabels = False,
              sensorLabelColour = 'b', sensorLabelFontSize = 5,
              showSensorFields = True,
              sensorFieldColour = 'g', sensorFieldAlpha = 0.2,
              showTargets = True,
              targetColour = 'b', targetMarker = 'x', targetSize = 2,
              showCount = False,
              targetCountColour = 'b', targetCountFontSize = 5):
    '''Draw the sensor field containing the given simple sensors.

    It is possible to set a lot of the colours and other attributes
    using further keyword arguments. In particular, it is possible to
    zoom-in on a specific part of the field. Sensors can be filled with
    a constant colour, a colour determined per-sensor (in a dict keyed
    by sensor id), or left open.

    :param ss: the sensors
    :param ts: the targets (default None)
    :param ax: the axes to draw into (default the current main axes)
    :param backgroundColour: the background colour for the field (default '0.95')
    :param subfieldXY: the bottom-left corner of the sub-field to draw (default all)
    :param subfieldWH: the width and heigh of the sub-field to draw (default all)
    :param showSensors: show the sensors positions (default True)
    :param sensorColour: colour to mark the sensor position (default 'r')
    :param sensorMarker: the sensor marker (default '.')
    :param sensorSize: size of the sensor marker (default 2)
    :param sensorFilled: whether the marker is filled (defauil True)
    :param sensorFillColour: colour to fill the sensor (default 'r')
    :param showSensorLabels: show the sensor simplex names (default False)
    :param sensorLabelColour: colour for the label if shown (default 'b')
    :param sensorLabelFontSize: font size for the label if shown (default 5)
    :param showSensorFields: show the sensor fields (default True)
    :param sensorFieldColour: colour of the sensor field (default 'g')
    :param sensorFieldAlpha: transparency for the field (default 0.2)
    :param showTargets: show the targets (default True)
    :param targetColour: colour to mark the sensor position (default 'b')
    :param targetMarker: the sensor marker (default 'x')
    :param targetSize: size of the sensor marker (default 2)
    :param showCount: show the non-zero target count at each sensor (default False)
    :param targetCountColour: colour for the count if shown (default 'b')
    :param targetCountFontSize: font size for the count if shown (default 5)
    '''

    # fill in defaults
    if ax is None:
        ax = plt.gca()
    if subfieldXY is None:
        subfieldXY = [0.0, 0.0]
    if subfieldWH is None:
        subfieldWH = [1.0 - subfieldXY[0], 1.0 - subfieldXY[1]]

    # sensors, fields, and labels
    if showSensors:
        for s in ss:
            p = s.position()

            # mark sensor field
            if showSensorFields:
                c = Circle(p, radius=s.detectionRadius(),
                           color=sensorFieldColour, alpha=sensorFieldAlpha)
                ax.add_patch(c)

            # determine sensor marker colour
            if sensorFilled:
                if sensorFillColour is None:
                    # default colour os red
                    col = 'r'
                elif type(sensorFillColour) is dict:
                    # extract colour from the dict, defaults to unfilled
                    col = sensorFillColour.get(s.id(), 'None')
                    if col is None:
                        col = 'None'   # matplotlib uses a string for unfilled
                else:
                    # use the literal colour provided
                    col = sensorFillColour
            else:
                # leave unfilled
                col = 'None'

            # mark sensor position
            ax.plot(p[0], p[1],
                    color=sensorColour, marker=sensorMarker, markersize=sensorSize,
                    markerfacecolor=col)

            # add sensor label
            if showSensorLabels:
                ax.annotate(f'{s.id()}', s.position(),
                            [1.1 * sensorSize, -1.1 * sensorSize], textcoords='offset pixels',
                            fontsize=sensorLabelFontSize, color=sensorLabelColour)

    # targets
    if showTargets and ts is not None:
        # positions
        for t in ts:
            ax.plot([t[0]], [t[1]],
                    color=targetColour, marker=targetMarker, markersize=targetSize)

    # counts
    if showCount and ts is not None:
        for s in ss:
            c = s.counts(ts)
            if c > 0:
                ax.annotate(f'{c}', s.position(),
                            [0.5, -1], textcoords='offset fontsize',
                            fontsize=targetCountFontSize, color=targetCountColour)

    # configure the axes
    ax.set_xlim(subfieldXY[0], subfieldXY[0] + subfieldWH[0])
    ax.set_ylim(subfieldXY[1], subfieldXY[1] + subfieldWH[1])


    if subfieldXY == [0.0, 0.0] and subfieldWH == [1.0, 1.0]:
        # no ticks for the full field
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # show extent for a subfield
        ax.set_xticks([subfieldXY[0], subfieldXY[0] + subfieldWH[0]])
        ax.set_yticks([subfieldXY[1], subfieldXY[1] + subfieldWH[1]])

    # set the background colour
    ax.set_facecolor(backgroundColour)
