# Utility functions
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

from typing import TypeVar, Iterable, Tuple

A = TypeVar('A')
B = TypeVar('B')


def zipboth(a: Iterable[A], b: Iterable[B]) -> Iterable[Tuple[A, B]]:
    '''Take two iterators and iterate the corresponding pairs.
    Unlike `zip' or `itertools.zip_longest' an exception is raised if the
    iterators are of uneven length.

    :param s: the first iterator
    :param b: the second iterator
    :returns: an iterator over the pairs'''
    il, ir = iter(a), iter(b)
    l, r = None, None
    while True:
        # get the next value from a
        try:
            l = il.__next__()
        except StopIteration:
            try:
                r = ir.__next__()
            except StopIteration:
                # both iterators are exhausted, finish
                return

            # if we get here, a finished before b
            raise ValueError('First iterator finished before the second')

        # get the next value from b
        try:
            r = ir.__next__()
        except StopIteration:
            # if we get here, b finished before a
            raise ValueError('Second iterator finished before the first')

        # if we get here, return the pair
        yield (l, r)
