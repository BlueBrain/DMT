"""Message, for the purpose of logging or other needs.
Think of it as some way of reporting across method calls.
Because we need to use this across our code-base, we have to keep the code here
from using rest of our code base, other than code in this module 'logging'.
With the exception of 'Record', which we think is more fundamental than Logging.
Of course, we cannot use Logging from Record."""

from abc\
    import ABC\
    ,      abstractmethod\
    ,      abstractclassmethod
import sys
import os
import time
from dmt.vtk.utils\
    import logging


class Message(ABC):
    """Base class for a message.
    This will serve as an example of Scala's case class feature,
    Python style."""

    def __init__(self, *msgs, **kwargs):
        """Default initialization. Override if you please."""
        self._value = '\n'.join(msgs)
        super().__init__(**kwargs)

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
    def labelstamp(self, x=None):
        """enclose a string in a box"""
        return "<{}>".format(self.label)


    @property
    def value(self):
        """"..."""
        return self._value

    def formatted(self, caller):
        """..."""
        return "{}@{} {}"
        return "{}@{} {}  {}\n"\
            .format(caller._name,
                    caller.timestamp(time.localtime()),
                    self.labelstamp, self.value)
        

class Funda(Message):
    """A single unit of fundamental understanding."""
    level = logging.LEVEL.STUDY
    label = "FUNDA"

class Info(Message):
    """General info, can be anything."""
    level = logging.LEVEL.INFO
    label = "INFO"

class ProgressInfo(Info):
    label = "PROGRESS"

class Explanation(Message):
    """Explain something"""
    level = logging.LEVEL.DEBUG
    label = "EXPLANATION"

class Note(Message):
    """Note may be used for testing."""
    level = logging.LEVEL.DEVELOP
    label = "NOTE"

class DevNote(Message):
    """Developer may need """
    level = logging.LEVEL.DEVELOP
    label = "DEVNOTE"

class Remark(Info):
    """A type of 'Info',
    just allows the user to remark if they are feeling like it!"""
    label = "REMARK"

class Advice(DevNote):
    """Another type of Info?"""
    label = "ADVICE"

class DebugInfo(Message):
    """Another type of Info"""
    level = logging.LEVEL.DEBUG
    label = "DEBUGINFO"

class Alert(Message): #Warning is reserved by the language
    """..."""
    level = logging.LEVEL.PROD
    label = "ALERT"

class Notice(Alert):
    """..."""
    label = "NOTICE"

class Attention(Alert):
    """..."""
    label = "ATTENTION"

class Error(Message):
    """..."""
    level = logging.LEVEL.PROD
    label = "ERROR"

class Assertion(Message):
    """..."""
    level = logging.LEVEL.PROD
    label = "ASSERTION"

class Test(Message):
    """..."""
    level = logging.LEVEL.TEST
    label="TEST"

class Success(Message):
    """..."""
    level = logging.LEVEL.PROD
    label = "SUCCESS"

class Failure(Message):
    """..."""
    level = logging.LEVEL.PROD
    label = "FAILURE"

class Dialog(Message):
    """Use this to interact with the (shell) user."""
    level = logging.LEVEL.PROD
    label = "DIALOG"

class SourceCodeInfo(Message):
    """..."""
    label = "SOURCE"

    def __init__(self,
            *msgs, level=0, **kwargs):
        self._level = level
        super().__init__(
            *msgs, **kwargs)

    @property
    def level(self):
        """..."""
        return self._level
    

class Validation:
    """Explains an exception. What happened?
    Not to the user, but client code."""
    def __init__(self, msg, exc=None):
        """...
        Parameters
        ------------------------------------------------------------------------
        msg :: str
        exc <: Exception"""

        self.explanation = Explanation(msg)
        self.exception = exc
        
    def explain(self, logger):
        """"...
        Parameters
        ------------------------------------------------------------------------
        logger <: Logger"""
        if self.exception:
            logger.error("{}: {}".format(self.exception.__class__.__name__,
                                         self.exception))
        logger.log(self.explanation)

        return self.exception is not None

    @property
    def passed(self):
        """did it pass?"""
        return self.exception is not None


class ContextualMessage(Message):
    """Message with a context
    """

    def __init__(self, msg, ctx=None, *args, **kwargs):
        self._context = ctx
        super().__init__(msg, *args, **kwargs)

    @property
    @abstractmethod
    def get_context(self):
        """..."""
        pass
    
    
