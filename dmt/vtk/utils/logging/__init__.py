"""Logging utilities."""
import sys
import os
import inspect
import time
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.logging.message import *


        


class Logger:
    """Log messages.
    This class will not store any messages and log eagerly.
    For lazy logging (that spits out it's contents when told to)
    use LazyLogger."""

    level = Record(STUDY=0,
                   TEST=0,
                   DEBUG=1,#log everything
                   DEVELOP=2,#no INFO
                   PROD=3)#log only errors and assertions

    message_types = Record(funda=Funda,
                           info=Info,
                           note=Note,
                           remark=Remark,
                           debug=DebugInfo,
                           warn=Alert,
                           error=Error,
                           assertion=Assertion)

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

    def __init__(self, client,
                 name=None,
                 level=None,
                 output_dir_path=None,
                 file_name=None,
                 *args, **kwargs):
        """..."""
        self._level = level if level is not None else Logger.level.PROD
        self._client = client
        self._name\
            = client if isinstance(client, str) else (
                name if name else "{}InstanceLogger".format(client.__name__)
            )
        self._in_file = (
            None if (output_dir_path is None and file_name is None) else 
            os.path.join(
                output_dir_path if output_dir_path else os.getcwd(),
                file_name if file_name else ".".join(self._name.lower())
            )
        )
        if self._in_file:
            self._log_message(self._name)

        self.__statistics = {mt.label: 0 for mt in self.message_types.values}
        try:
            super(Logger, self).__init__(*args, **kwargs)
        except:
            pass

    def get_source_info(self):
        """..."""
        traceback = inspect.getframeinfo(inspect.stack()[1][0])
        return ("{classname}:\n\tfilename: \t{filename}\n\tlineno: \t{lineno}\n"
                "\tcode_context: \t{code_context}\n\tindex: {index}\n"\
                .format(classname=traceback.__class__.__name__,
                        filename=traceback.filename,
                        lineno=traceback.lineno,
                        code_context=traceback.code_context,
                        index=traceback.index))

    def source_info(self):
        """a string to show where the log was generated."""
        traceback = inspect.getframeinfo(inspect.stack()[1][0])
        self.log(SourceCodeInfo(
            "{classname}:\n\tfilename: \t{filename}\n\tlineno: \t{lineno}\n"
            "\tcode_context: \t{code_context}\n\tindex: {index}\n"\
            .format(classname=traceback.__class__.__name__,
                    filename=traceback.filename,
                    lineno=traceback.lineno,
                    code_context=traceback.code_context,
                    index=traceback.index)
        ))

    def _log_message(self, msg):
        """"Log message with time.
            
        Parameters
        ------------------------------------------------------------------------
        msg :: Message #to be logged
        """
        if msg.level >= self._level:
            title = "{}@{} {}".format(self._name,
                                      self.timestamp(time.localtime()),
                                      msg.labelstamp)
            fmsg = "{}".format(msg.value)

            Logger.err_print(title)
            #Logger.err_print(self.get_source_info())
            Logger.err_print(80*'~')
            Logger.err_print(fmsg)
            Logger.err_print(80*"-")

            if self._in_file:
                with open(self._in_file, "a")  as f:
                    f.write(title)
                    f.write(80*'~')
                    f.write(fmsg)
                    f.write(80*"-")
        else:
            pass

        try:
            self.__statistics[msg.label] += 1
        except KeyError:
            self.__statistics[msg.label] = 1

        return self.__statistics

    def log(self, msg):
        """...an alias...
        Parameters
        ------------------------------------------------------------------------
        msg :: Message
        """
        return self._log_message(msg)

    @property
    def client(self):
        """..."""
        return self._client

    def info(self, *msgs):
        """..."""
        return self._log_message(Info(*msgs))

    def note(self, *msgs):
        """..."""
        return self._log_message(Note(*msgs))

    def devnote(self, *msgs):
        """..."""
        return self._log_message(DevNote(*msgs))

    def inform(self, *msgs):
        """..."""
        return self.info(*msgs)

    def study(self, *msgs):
        return self._log_message(Funda(*msgs))

    def remark(self, *msgs):
        return self._log_message(Remark(*msgs))

    def debug(self, *msgs):
        return self._log_message(DebugInfo(*msgs))

    def warning(self, *msgs):
        """..."""
        return self._log_message(Alert(*msgs))

    def beware(self, *msgs):
        """..."""
        return self.warning(*msgs)

    def warn(self, *msgs):
        """..."""
        return self.warning(*msgs)


    def alert(self, *msgs):
        """..."""
        return self.warning(*msgs)
    
    def error(self, *msgs):
        """..."""
        return self._log_message(Error(*msgs))

    def assertion(self, success, *msgs):
        """...
        Parameters
        ------------------------------------------------------------------------
        success :: Boolean
        """
        x = self._log_message(Assertion(*msgs))
        assert success, msgs[0]
        return x


class LazyLogger(Logger):
    """Log lazily.
    Store logs in a file and flush to disc when prompted
    or after a given number of messages."""

    def __init__(self, name=None, 
                 level=None,
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
        self._logger = Logger(self.__class__, *args, **kwargs)
                              

    @property
    def logger(self):
        """..."""
        return self._logger


def with_logging(level, *args, **kwargs):
    """class decorator"""
    def effective(cls):
        """class decorator"""
        cls.logger =  Logger(cls, level=level, *args, **kwargs)
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
