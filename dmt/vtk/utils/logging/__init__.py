"""Logging utilities."""
import sys
import os
import inspect
import time
from dmt.vtk.utils.collections import Record, POD

LEVEL=\
    Record(
        STUDY=0,
        TEST=0,
        DEBUG=1,#log everything
        DEVELOP=2,
        INFO=3,
        PROD=4)#log only errors and assertions

from dmt.vtk.utils.logging.message import *
from dmt.vtk.utils.logging.logger import *
