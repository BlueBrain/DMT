"""Pronouncement: a formal or authoritative announcement or declaration.
A Validation will return a Verdict, wrapped inside a Pronouncement which will
be a longer report, and may be posted in a Validation repository."""


class Pronouncement:
    """Data struct to represent a report that compares two MeasurableSystems.

    TODO
    ----
    The attributes in a Pronouncement can be combined to produce a report.
    We have implemented a stub, extend it.
    """


    def __init__(self,
                 reference,
                 alternative,
                 phenomenon,
                 statistical_test_used,
                 verdict,
                 **kwargs):
        self._reference = reference
        self._alternative = alternative
        self._verdict = verdict
        self._phenomenon = phenomenon
        self._statistical_test_used = statistical_test_used

    @property
    def reference(self):
        """@attr: MeasurableSystem"""
        return self._reference

    @property
    def alternative(self):
        """@attr: MeasurableSystem"""
        return self._alternative

    @property
    def verdict(self):
        """@attr: Verdict"""
        return self._verdict

    @property
    def phenomenon(self):
        """@attr: Phenomenon
        Phenomenon measured for this Validation"""
        return self._phenomenon

    @property
    def statistical_test_used(self):
        """@attr: StatisticalTestMethod
        Statistical test used to arrive at the verdict."""
        return self._statistical_test_used


    def __repr__(self):
        """A string representation of this Pronouncement.
        TODO
        ----
        Use all the attributes.
        __repr__ will be used to print reports."""

        ref = self.reference()
        ref_type = ref.system_type() #data-source or model
        ref_name = ref.name() if ref_type is not None else "Reference"

        alt = self.alternative()
        alt_type = alt.system_type() #data-source or model
        alt_name = alt.name() if alt_type is not None else "Alternative"

        phen = self.phenomenon().name()
        stest = self.statistical_test_used().name()
        ver = repr(self.verdict())

        return """
        %(ref_type): %(ref_name)s
        %(alt_type): %(ref name)s
        Tested for %(phen)s
        Statistical Test used %(stest)s
        Verdict: %(ver)s"""
