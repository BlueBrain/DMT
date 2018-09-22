"""Message, for the purpose of logging or other needs.
Think of it as some way of reporting across method calls.
Because we need to use this across our code-base, we have to keep the code here
from using rest of our code base, other than code in this module 'logging'.
With the exception of 'Record', which we think is more fundamental than Logging.
Of course, we cannot use Logging from Record."""

from abc import ABC, abstractmethod, abstractclassmethod
import sys
import os
import time


class Message(ABC):
    """Base class for a message.
    This will serve as an example of Scala's case class feature,
    Python style."""

    def __init__(self, msg):
        """Default initialization. Override if you please."""
        self._value = msg

    @property
    @abstractmethod
    def level(self):
        """..."""
        pass

    @property
    @abstractmethod
    def label(self):
        """..."""
        pass

    @property
    def value(self):
        """"..."""
        return self._value

class Funda(Message):
    """A single unit of fundamental understanding."""
    level = 0
    label = "FUNDA"

class Info(Message):
    """General info, can be anything."""
    level = 1
    label = "INFO"

class Note(Message):
    """Note may be used for testing."""
    level = 0
    label = "NOTE"

class Remark(Info):
    """A type of 'Info',
    just allows the user to remark if they are feeling like it!"""
    label = "REMARK"

class Advice(Message):
    """Another type of Info?"""
    label = "ADVICE"

class DebugInfo(Info):
    """Another type of Info"""
    label = "DEBUGINFO"

class Alert(Message): #Warning is reserved by the language
    """..."""
    level = 2
    label = "WARNING"

class Notice(Alert):
    """..."""
    label = "NOTICE"

class Attention(Alert):
    """..."""
    label = "ATTENTION"

class Error(Message):
    """..."""
    level = 3
    label = "ERROR"

class Assertion(Message):
    """..."""
    level = 4
    label = "ASSERTION"
