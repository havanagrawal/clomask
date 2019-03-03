"""Representation for slanted shelf co-ordinates and geometry

    Perform computations on shelf and shelf-region configurations.
"""
from itertools import tee

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.m = (self.end.y - self.start.y) / (self.end.x - self.start.x)
        self.c = self.start.y - (self.m * self.start.x)

    def y_at(self, x):
        """The y-coordinate of the line at point x"""
        return self.m * x + self.c


class ShelfRegion:
    """A shelf region is modeled by two lines that outline the top and bottom
        borders of the shelf.

        0 ________________
        1 |______________|
        2 |______________|
        3 |______________|

        In this case, lines 0 and 1 together encapsulate one shelf region.
    """
    def __init__(self, top_line, bottom_line):
        self.top_line = top_line
        self.bottom_line = bottom_line

    def height_at(self, loc):
        return abs(self.bottom_line.y_at(loc) - self.top_line.y_at(loc))

    @property
    def x_start(self):
        return max(self.top_line.start.x, self.bottom_line.start.x)

    @property
    def x_end(self):
        return max(self.top_line.end.x, self.bottom_line.end.x)

    @property
    def y_start(self):
        return min(self.top_line.start.y, self.top_line.end.y)

    @property
    def y_end(self):
        return max(self.bottom_line.start.y, self.bottom_line.end.y)

class Shelf:
    """A set of shelf regions, modeling the actual shelf
        ________________
        |______________|
        |______________|
        |______________|
        |              |
    """
    def __init__(self, config):
        shelves = self._parse_shelves_config(config["shelves"])
        self._shelf_regions = []
        for line1, line2 in pairwise(shelves):
            self._shelf_regions.append(ShelfRegion(line1, line2))

    def _parse_shelves_config(self, shelves):
        lines = []
        for shelfline in shelves:
            p1 = Point(shelfline["x_start"], shelfline["y_start"])
            p2 = Point(shelfline["x_end"], shelfline["y_end"])
            lines.append(Line(p1, p2))
        return lines

    @property
    def regions(self):
        return self._shelf_regions


def pairwise(iterable):
    """Recipe from itertools documentation for iterating through
        two lists in a pairwise fashion
        s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
