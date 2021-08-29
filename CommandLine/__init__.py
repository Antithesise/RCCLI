"""
Python based utility for creating CLIs and other commandline-driven utilities.
"""

from CommandLine.CommandLine import *
from CommandLine import ext

del TYPE_CHECKING # remove TYPE_CHECKING constant
del ext.TYPE_CHECKING

del ext.check # remove function from CheckUnix
