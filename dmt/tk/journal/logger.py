# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""Log journal messages."""
import sys
import os
import inspect
from collections import defaultdict
from ..journal import Level, Color
from .message import *

class Logger:
    """Log messages.
    This class will not store any messages, but log them eagerly.
    For lazy logging use LazyLogger."""
    Level = Level
    def get_level(self, level):
        """Resolve logging level from available information.
        Arguments
        ~   level :: Either name of a level as a string, or an actual Level.
        """
        if level is not None:
            if isinstance(level, str):
                try:
                    return getattr(Level, level)
                except AttributeError as error:
                    sys.stderr.write(
                        """Unknown logging level {}.
                        Please choose one of {}. """.format(
                            level,
                            [level_name for level in Level]))
            return level
        
        if self._level_env_var in os.environ:
            return getattr(Level, os.environ[self._level_env_var])

        return Level.PROD
                
    @staticmethod
    def with_color(color, message):
        """Add color to the message"""
        return color.value + message + Color.ENDC.value if color else message

    @staticmethod
    def underlined(text):
        """underline a message"""
        return Logger.with_color(Color.UNDERLINE, text)

    @staticmethod
    def err_print(
            *args, **kwargs):
        """Print to stderr"""
        print(*args, file=sys.stderr, **kwargs)

    def __init__(self,
            client,
            name=None,
            level=None,
            output_dir_path=None,
            file_name=None,
            level_environment_variable="LOGLEVEL",
            log_line_length=80,
            log_start_sep="=",
            log_end_sep="=",
            *args, **kwargs):
        """Initialize Me"""
        self._level_env_var =\
            level_environment_variable
        self._level = self.get_level(level)
        self._client = client
        self._name =\
            "{} Logger".format(client) if isinstance(client, str)\
            else (name if name else str(client))
                
        self._in_file =\
            None if (output_dir_path is None and file_name is None) else\
            os.path.join(
                output_dir_path if output_dir_path else os.getcwd(),
                file_name if file_name else "_".join(self._name.lower()))

        self._statistics = defaultdict(lambda: 0)

        if self._in_file:
            with open(self._in_file, "a") as log_file:
                log_file.write(self._name + "\n")

        self._log_line_length = log_line_length
        self._log_start_sep   = log_line_length * log_start_sep
        self._log_end_sep     = log_line_length * log_end_sep
        try:
            super().__init__(
                *args, **kwargs)
        except:
            pass

    @property
    def name(self):
        """Name of this logger instance."""
        return self._name

    @property
    def level(self):
        """Level of this logger instance."""
        return self._level

    def get_source_info(self):
        """..."""
        traceback =\
            inspect.getframeinfo(
                inspect.stack()[1][0])
        return (
            "{classname}:\n\tfilename: \t{filename}\n\tlineno: \t{lineno}\n"
            "\tcode_context: \t{code_context}\n\tindex: {index}\n"\
            .format(
                classname=traceback.__class__.__name__,
                filename=traceback.filename,
                lineno=traceback.lineno,
                code_context=traceback.code_context,
                index=traceback.index))

    def _left_justified(self, text):
        """Justify text to left.
        Arguments
        ~   text :: String without any newline
        """
        if len(text) > self._log_line_length:
            return text
        post_length = self._log_line_length - len(text)
        return text + (post_length * " ")

    def _right_justified(self, text):
        """Justify text to right.
        Arguments
        ~   text :: String without any newline
        """
        if len(text) > self._log_line_length:
            return text
        pre_length = self._log_line_length - len(text)
        return pre_length * " " + text

    def _pretty_message_string(self,
            message,
            color=None):
        """..."""
        title =\
            Logger.underlined(
                self._left_justified(self._name))
        stamp =\
            Logger.underlined(
                self._left_justified(
                    "{}@{}".format(message.label, message.timestamp)))
        formatted_message =\
            Logger.with_color(
                color,
                "{}".format(message.value))
        return "{}\n{}\n{}\n{}\n{}\n".format(
            self._log_start_sep,
            title,
            stamp,
            formatted_message,
            self._log_end_sep)

    def _log_message(self,
            message,#: Message
            color=None,
            out=sys.stderr):
        """Log message with a time stamp."""
        if message.level.value >= self._level.value:
            if self._in_file:
                with open(self._in_file, "a") as log_file:
                    log_file.write(
                        self._pretty_message_string(
                            message, color))
            else:
                out.write(
                    self._pretty_message_string(message, color))
        self._statistics[message.label] += 1
        return self._statistics

    def log(self, message):
        """...another word for _log_message"""
        return self._log_message(message)

    @property
    def client(self):
        """..."""
        return self._client

    def ignore(self, *messages):
        """..."""
        pass

    def info(self, *messages):
        """..."""
        return self._log_message(
            Info(*messages))
    
    def progress(self, *messages):
        """..."""
        return self._log_message(
            ProgressInfo(*messages))

    def note(self, *messages):
            """..."""
            return self._log_message(
                Note(*messages))

    def devnote(self, *messages):
        """..."""
        return self._log_message(
            DevNote(*messages))

    def inform(self, *messages):
        """..."""
        return self.info(*messages)

    def suggest(self, *messages):
        """..."""
        return self._log_message(
            Suggestion(*messages))

    def study(self, *messages):
        """..."""
        return self._log_message(
            Funda(*messages))

    def remark(self, *messages):
        """..."""
        return self._log_message(
            Remark(*messages))

    def debug(self, *messages):
        """..."""
        return self._log_message(
            DebugInfo(*messages))
    
    def warning(self, *messages):
        """..."""
        return self._log_message(
            Alert(*messages),
            out=sys.stderr)
    
    def beware(self, *messages):
        """..."""
        return self.warning(
            *messages)
    
    def warn(self, *messages):
        """..."""
        return self.warning(
            *messages)
    
    def status(self, *messages):
        """..."""
        return self._log_message(
            Status(*messages),
            out=sys.stderr)

    def alert(self, *messages):
        """..."""
        return self.warning(
            *messages)
    
    def error(self, *messages):
        """..."""
        return self._log_message(
            Error(*messages),
            out=sys.stderr)
    
    def test(self, *messages):
        """..."""
        return self._log_message(
            Test(*messages))
    
    def success(self, *messages):
        """..."""
        return self._log_message(
            Success(*messages),
            color=Color.OKGREEN)
    
    def failure(self, *messages):
        """..."""
        return self._log_message(
            Failure(*messages),
            color=Color.FAIL,
            out=sys.stderr)
    
    def dialog(self, *messages):
        """..."""
        return self._log_message(
            Dialog(*messages),
            color=Color.OKBLUE,
            out=sys.stdout)
    
    def assertion(self, success, *messages):
        """Assert, and then log 
           Arguments
           ~   success :: Boolean"""
        assert success, messages[0]
        return self._log_message(
            Assertion(*messages),
            out=sys.stderr)
    

class LazyLogger(Logger):
    """Log lazily.
    Store log messages in a file, and flush to disc when prompted,
    or after a given number of messages."""

    def __init__(self,
            name=None,
            level=None,
            output_dir_path=None,
            file_name=None,
            flush_threshold=10000,
            *args, **kwargs):
        """..."""
        self._logs = []
        self._flush_threshold = flush_threshold
        super().__init__(
            name=name,
            output_dir_path=output_dir_path,
            file_name=file_name,
            *args, **kwargs)
        self._in_file =\
            os.path.join(
                output_dir_path if output_dir_path else os.getcwd(),
                file_name if file_name else "output.log")

    def flush(self):
        """write all the log messages to disc"""
        with open(self._in_file, "a") as log_file:
            for message in self._logs:
                log_file.write(
                    self._pretty_message_string(message))

            self._logs = []

    def _log_message(self,
            message):
        """..."""
        self._logs.append(message)
        if len(self._logs) > self._flush_threshold:
            self.flush()


class WithLogging:
    """A base class that will allow the deriving class to log to an
    output resource. Attribute values to pass to Logger will be read
    from keyword arguments."""
    def __init__(self, *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        output :: Either[File, stdio]#where logger will output to.
        """
        self._logger =\
            Logger(self.__class__, *args, **kwargs)

    @property
    def logger(self):
        """..."""
        return self._logger


def with_logging(level, *args, **kwargs):
    """class decorator"""
    def effective(cls):
        """class decorator"""
        cls.logger =\
            Logger(cls, level=level, *args, **kwargs)
        return cls
    return effective

class WithLazyLogging:
    """A base class that will allow the deriving class to log to an
    output resource. Attribute values to pass to Logger will be read
    from keyword arguments."""
    def __init__(self, *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        output :: Either[File, stdio]#where logger will output to.
        """
        self.logger = LazyLogger(
            name="{}Logger".format(self.__class__.__name__),
            level=Logger.level.DEVELOP,
            output_dir_path=kwargs.get("log_output_dir_path", None),
            file_name=kwargs.get("log_file_name", None),
            flush_threshold=kwargs.get("log_flush_threshold", None)
            *args, **kwargs)

        super(WithLazyLogging, self).__init__(*args, **kwargs)

    @property
    def logger(self):
        """..."""
        return self._logger
