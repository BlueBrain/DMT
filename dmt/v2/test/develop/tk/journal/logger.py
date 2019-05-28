import os
from dmt.v2.tk.journal import *


def test_client_level():
    """
    Client and level are set correctly.
    """
    if "LOGLEVEL" in os.environ:
        logger_os = Logger("Test")
        assert isinstance(logger_os.level, Level),\
            "Logger's level should be an instance of Level, and not {}"\
            .format(type(logger_os.level))
        assert logger_os.level == getattr(Level, os.environ["LOGLEVEL"]),\
            "Logger level {} should have been read from the OS environment."\
            .format(logger_os.level)
    try:
        os.environ.pop("LOGLEVEL")
    except KeyError as error:
        raise Exception(
            """Please add 'LOGLEVEL' to your environment
            to test that logger level can be read from the environment.:
            KeyError {}""".format(error))

    logger_prod = Logger("Test")
    assert logger_prod.name == "Test Logger",\
        """Name of this logger should be set to its client."""
    assert isinstance(logger_prod.level, Level),\
        "Logger's level should be an instance of Level, and not {}"\
        .format(type(logger_prod.level))
    assert logger_prod.level == Level.PROD,\
        "Logger level {} should have been Level.PROD by default"\
        .format(logger_prod.level)

    logger_develop =\
        Logger("Test", level=Level.DEVELOP)
    assert isinstance(logger_develop.level, Level),\
        "Logger's level should be an instance of Level, and not {}"\
        .format(type(logger_develop.level))
    assert logger_develop.level == Level.DEVELOP,\
        """Loggers level {} should have been set to the value passed."""


def test_logging():
    """
    Eye ball that logging produces messages on the screen.
    """
    l = Logger("Test", level=Level.STUDY)

    l.devnote("A development note")

    l.inform("You are informed")

    l.study("Studying to develop a logger")

    l.error("Report an error")
