"""
Summarize the circuit.
"""
from collections import namedtuple

class Point(namedtuple("Point", "x y z")):
    __slots__ = ()
    @property
    def hypot(self):
        return (self.x ** 2 + self.y ** 2 + + self.z ** 2) ** 0.5
    def __str__(self):
        return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (
            self.x, self.y, self.z, self.hypot)

class 
