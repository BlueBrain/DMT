"""Logging utilities."""
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

    def __init__(self, name=None,
                 output_dir_path=None, file_name=None,
                 *args, **kwargs):
        """..."""
        self._name = name if name else "Output Log"
        self._in_file = (
            None if (output_dir_path is None and file_name is None) else 
            os.path.join(
                output_dir_path if output_dir_path else os.getcwd(),
                file_name if file_name else ".".join(self._name.lower())
            )
        )
        super(Logger, self).__init__(*args, **kwargs)
        if self._in_file:
            self._log_message(self._name)

    def _log_message(self, msg, msg_type=""):
        """"Log message with time.
            
        Parameters
        ------------------------------------------------------------------------
        msg :: str #to be logged
        """
        msg = "{} {}:: {}"\
              .format(Logger.timestamp(time.localtime()), msg_type, msg)
        print(msg)
        if self._in_file:
            with open(self._in_file, "a")  as f:
                f.write("{}\n".format(msg))

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

    def __init__(self, flush_threshold=10000,
                 output_dir_path=None, file_name=None,
                 *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        flush_threshold :: int #number of messages after which to flush.
        """
        self._logs = [] #list of logs
        self._flush_threshold = flush_threshold
        super(LazyLogger, self).__init__(output_dir_path=output_dir_path,
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
