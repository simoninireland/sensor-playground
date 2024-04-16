# Init file for the sensor playground package
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

# Utilities
from .utils import zipboth

# Agents, targets, and sensors
from .position import Position, vectorPosition, distanceBetween, Direction, BoundingBox, Trajectory
from .agent import Agent, MobileAgent
from .modalities import Modality, Targetting, TargetCount, TargetDistance, TargetDirection
from .sensor import Sensor, SimpleTargetCountSensor

# Playgrounds
from .playground import SensorPlayground

# Analytics
from .euler import EulerEstimator, FaceMin

# Drawing
from .drawing import drawField
