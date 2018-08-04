"""Verdict : a decision on an issue of fact in a civil or criminal case
or an inquest. A Validation will return a Verdict, summarizing the results of
tests comparing two systems (alternative versus reference, model versus
 experimental data, two models, or two data sets)."""

from enum import Enum

class Verdict(Enum):
    """an enumeration that lists all possible values
    of a Validation's verdict"""

    NA = 0
    FAIL = 1
    INCONCLUSIVE = 2
    PASS = 3







