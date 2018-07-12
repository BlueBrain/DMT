"""Test and develop dmt.utils.utils."""

from abc import ABC, abstractmethod
from dmt.utils.utils import ABCwithRegistryMeta

class Color(metaclass=ABCwithRegistryMeta):
    def __init__(self, grade):
        self.__grade = grade

    @property
    @abstractmethod
    def group(self):
        pass

    @property
    def grade(self):
        return self.__grade

class Red(Color):
    group = "red"

class Blue(Color):
    group = "blue"

print(Blue)
print(Red)
print(Color)

for k, v in Color.items():
    print(k, ": ",  v)

class Shape(metaclass=ABCwithRegistryMeta):

    @property
    @abstractmethod
    def number_sides(self):
        pass

class Line(Shape):
    @property
    def number_sides(self):
        return 1

class Angle(Shape):
    @property
    def number_sides(self):
        return 2

class Rectangle(Shape):
    @property
    def number_sides(self):
        return 4

class Dot(Shape):
    @property
    def number_sides(self):
        return 0

class Circle(Shape):
    @property
    def number_sides(self):
        return "infinite"

class Square(Rectangle):
    pass


print(Square)
print(Rectangle)
print(Line)
print(Circle)
print(Shape)
