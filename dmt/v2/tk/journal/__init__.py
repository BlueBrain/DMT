"A logging utility"

from enum import Enum


class Level(Enum):
    """Level at which a Journal should log"""
    STUDY   = 0
    DEBUG   = 1
    DEVELOP = 2
    TEST    = 2
    INFO    = 3
    PROD    = 4


class Color(Enum):
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

from .logger import Logger
from .message import *

