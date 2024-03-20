# Targets
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

from sensorplayground import Agent


class Target(Agent):
    '''A target to be detected.

    Targets are abstract agents. They have position, can move from
    point to point, and take actions. They act independently of
    sensors which may be observing them.

    :param id: (optional) the target's identifier

    '''

    def __init__(self, id: Any = None):
        super().__init__(id)
