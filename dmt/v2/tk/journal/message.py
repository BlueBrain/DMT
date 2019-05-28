"""Message, to be passed around and logged into a journal..."""

from abc import\
    ABC, abstractmethod
import time
from . import utils, Level

class Message(ABC):
    """Base Message"""

    def __init__(self, *msgs, **kwargs):
        """Initialize Me"""
        self._value = '\n'.join(msgs)
        self._time_creation  = time.localtime()

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
    def labelstamp(self):
        """Enclose a string in a box."""
        return "<{}>".format(self.label)

    @property
    def value(self):
        """..."""
        return self._value

    @property
    def timestamp(self):
        """..."""
        return utils.timestamp(
            time_value=self._time_creation)

    def formatted(self, caller=None):
        """Message value formatted according to a class 'caller'
        """
        if not caller:
            return "@{} {} {}"\
                .format(
                    self.timestamp,
                    self.labelstamp,
                    self.value)
        return "{}@{} {} {}\n"\
            .format(
                caller.__name__,
                self.timestamp,
                self.labelstamp,
                self.value)


class Funda(Message):
    """A single unit of fundamental understanding."""
    level = Level.STUDY
    label = "FUNDA"

class Info(Message):
    """General Info, can be anything."""
    level = Level.INFO
    label = "INFO"

class ProgressInfo(Info):
    """Info about progress"""
    label = "PROGRESS"

class Explanation(Message):
    """Explain something"""
    level = Level.DEBUG
    label = "EXPLANATION"

class Note(Message):
    """Note may be used for testing."""
    level = Level.DEVELOP
    label = "NOTE"

class DevNote(Note):
    """A note to develop code..."""
    label = "DEVNOTE"

class Remark(Info):
    """If programmer may want to """
    label = "REMARK"

class DebugInfo(Message):
    """Use to provide info when debugging."""
    level = Level.DEBUG
    label = "DEBUGINFO"

class Alert(Message):
    """..."""
    level = Level.PROD
    label = "ALERT"

class Notice(Alert):
    """..."""
    label = "NOTICE"

class Attention(Alert):
    """..."""
    label = "ATTENTION"

class Error(Message):
    """..."""
    level = Level.PROD
    label = "ERROR"

class Assertion(Message):
    """..."""
    level = Level.PROD
    label = "ASSERTION"

class Test(Message):
    """..."""
    level = Level.TEST
    label = "TEST"

class Success(Message):
    """..."""
    level = Level.PROD
    label = "SUCCESS"

class Failure(Message):
    """..."""
    level = Level.PROD
    label = "FAILURE"

class Dialog(Message):
    """Use this to interact with the (shell) user."""
    level = Level.PROD
    label = "DIALOG"


class SourceCodeInfo(Message):
    """..."""
    label = "SOURCE"

    def __init__(self,
            level=0, 
            *msgs, **kwargs):
        self._level = level
        super().__init__(
            *msgs, **kwargs)

    @property
    def level(self):
        """..."""
        return self._level


class ContextualMessage:
    """A message with a context."""

    def __init__(self,
            context,
            message,
            *args, **kwargs):
        """Initialize Me"""
        self._context = context
        self._message = message
        super().__init__(
            *args, **kwargs)

    @property
    def context(self):
        """..."""
        return self._context

    @property
    def message(self):
        """..."""
        return self._message
