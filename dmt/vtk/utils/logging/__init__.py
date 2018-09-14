"""Logging utilities."""
import sys
import os
import time
from dmt.vtk.utils.collections import Record

class Logger:
    """Log messages.
    This class will not store any messages and log eagerly.
    For lazy logging (that spits out it's contents when told to)
    use LazyLogger."""
    message_type = Record(info="INFO",
                          warning="WARNING",
                          error="ERROR",
                          assertion="ASSERTION")
    level = dict(INFO=0,
                 WARNING=1,
                 ERROR=2,
                 ASSERTION=3)
    @staticmethod
    def timestamp(now=None, *args, **kwargs):
        """Time stamp.
        
        Improvements
        ------------------------------------------------------------------------
        We can use method arguments to specify timestamp's format.

        Parameters
        ------------------------------------------------------------------------
        time :: time.struct_time
        """
        def two_char(s):
            """Make string 's' at least two characters long."""
            s = str(s)
            return s if len(s) >= 2 else ("0{}".format(s) if len(s) == 1 else "00")

        now = now if now else time.localtime()
        return "[{}{}{}-{}:{}:{}]".format(two_char(now.tm_year),
                                          two_char(now.tm_mon),
                                          two_char(now.tm_mday),
                                          two_char(now.tm_hour),
                                          two_char(now.tm_min),
                                          two_char(now.tm_sec))

    @staticmethod
    def err_print(*args, **kwargs):
        """Print to stderr"""
        print(*args, file=sys.stderr, **kwargs)

    def __init__(self,  name=None,
                 output_dir_path=None,
                 file_name=None,
                 level=None,
                 *args, **kwargs):
        """..."""
        self._level\
            = Logger.level[level if level  else Logger.message_type.error]
        self._name = name if name else "Output Log"
        self._in_file = (
            None if (output_dir_path is None and file_name is None) else 
            os.path.join(
                output_dir_path if output_dir_path else os.getcwd(),
                file_name if file_name else ".".join(self._name.lower())
            )
        )
        #super(Logger, self).__init__(*args, **kwargs)
        if self._in_file:
            self._log_message(self._name)

    def _log_message(self, msg, msg_type=""):
        """"Log message with time.
            
        Parameters
        ------------------------------------------------------------------------
        msg :: str #to be logged
        """
        if Logger.level[msg_type] >= self._level:
            msg = "{} {}:: {}"\
                  .format(Logger.timestamp(time.localtime()), msg_type, msg)
            Logger.err_print(msg)
            if self._in_file:
                with open(self._in_file, "a")  as f:
                    f.write("{}\n".format(msg))
        else:
            return
                    
    def info(self, msg):
        """..."""
        self._log_message(msg, self.message_type.info)

    def warning(self, msg):
        """..."""
        self._log_message(msg, self.message_type.warning)

    def error(self, msg):
        """..."""
        self._log_message(msg, self.message_type.error)

    def assertion(self, msg):
        """..."""
        self._log_message(msg, self.message_type.assertion)


class LazyLogger(Logger):
    """Log lazily.
    Store logs in a file and flush to disc when prompted
    or after a given number of messages."""

    def __init__(self, name=None, 
                 output_dir_path=None,
                 file_name=None,
                 flush_threshold=None,
                 *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        flush_threshold :: int #number of messages after which to flush.
        """
        self._logs = [] #list of logs
        self._flush_threshold = flush_threshold if flush_threshold else 10000
        super(LazyLogger, self).__init__(name=name,
                                         output_dir_path=output_dir_path,
                                         file_name=file_name,
                                         *args, **kwargs)
        opd = output_dir_path if output_dir_path else os.getcwd()
        fn = file_name if file_name else "output.log"
        self._in_file = os.path.join(opd, fn)
               

    def flush(self):
        """Write all the log messages to the disc"""
        with open(self._in_file, "a") as f:
            for msg in self._logs:
                f.write("{} {}:: {}\n".format(msg.timestamp,
                                              msg.message_type,
                                              msg.message))

            self._logs = []

    def _log_message(self, msg, msg_type=""):
        self._logs.append(Record(timestamp=Logger.timestamp(time.localtime()),
                                 message=msg,
                                 message_type=msg_type))
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
        self._logger = Logger(name=kwargs.get("logger_name", None),
                              level=kwargs.get("logger_level", None),
                              output_dir_path=kwargs.get("log_output_dir_path", None),
                              file_name=kwargs.get("log_file_name", None),
                              *args, **kwargs)

    @property
    def logger(self):
        """..."""
        return self._logger

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
            name=kwargs.get("log_name", None),
            output_dir_path=kwargs.get("log_output_dir_path", None),
            file_name=kwargs.get("log_file_name", None),
            flush_threshold=kwargs.get("log_flush_threshold", None)
            *args, **kwargs)

        super(WithLazyLogging, self).__init__(*args, **kwargs)

    @property
    def logger(self):
        """..."""
        return self._logger
