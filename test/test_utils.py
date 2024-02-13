# Test utility functions
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

import unittest
from sensorplayground import *


class TestZipBoth(unittest.TestCase):

    def testBothEmpty(self):
        '''Test two empty iterators just complete successfully.'''
        for _ in zipboth([], []):
            pass


    def testBothEqual(self):
        '''Test two equal-length iterators complete successfully.'''
        pairs = []
        for p in zipboth([1, 2, 3], [4, 5, 6]):
            pairs.append(p)
        self.assertCountEqual(pairs, [(1, 4), (2, 5), (3, 6)])


    def testUnequalFirst(self):
        '''Test we catch the first iterator finishing before the second.'''
        with self.assertRaises(ValueError):
            for _ in zipboth([1, 2], [4, 5, 6]):
                pass


    def testUnqualSecond(self):
        '''Test we catch the second iterator finishing before the first.'''
        with self.assertRaises(ValueError):
            for _ in zipboth([1, 2, 3], [4, 5]):
                pass
