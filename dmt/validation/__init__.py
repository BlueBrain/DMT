"""Behavior of a validation expressed as an abstract base class.
"""

from abc import ABC, abstractmethod
from dmt.validation import Pronouncement


class Analysis(ABC):
    """Analysis is a base class for a Validation.
    After all, each Validation can be considered an Analysis with additional
    behavior."""

    @property
    @abstractmethod
    def title(self):
        """@attr :: String"""
        pass

    @property
    @abstractmethod
    def authors(self):
        """@attr :: List[Author]"""
        pass

    @property
    @abstractmethod
    def citations(self):
        """@attr :: List[Citation]"""
        pass

    @abstractmethod
    def __call__(self, system, **kwargs):
        """An Analysis may be called.
        Perform an Analysis of a system.

        Parameters
        -----------
        system :: MeasurableSystem

        Return
        ------
        Up to the concrete implementation of Analysis"""
        pass


class Comparison(Analysis):
    """Comparison is an Analysis of two systems,
    data-object vs data-object, data-object vs model, or model vs model.
    However Comparison does not pass any judgements."""


    

class Validation(Comparison):
    """Validation is a Comparison that passes a judgment.
    Validation will pass a judgment.


    TODO
    -----
    Where should we make the plots?
    Whose responsibility is it?
    render_verdict's?

    We want to have at least two kinds of Pronouncements --- to enable that
    many Validation types. We can have a Pronouncement with an output directory
    information, versus another without this information --- which should be 
    the case for an interactive session. 
    """

    def __call__(self, refsys, altsys, **kwargs):
        """A Validation may be called.
        The call must be made with at least a reference, and an alternative
        MeasurableSystem,

        Parameters
        -----------
        @refsys : MeasurableSystem
        @altsys : MeasurableSystem

        kwargs may provide an output directory.
        We do not make it explicitly necessary as we may want the user to use 
        this framework interactively.

        Return
        --------
        We provide a default implementation here,
        which can be overridden by a concrete implementation."""

        p = self.pronouncement(refsys, altsys, **kwargs)
        return p

    def pronouncement(self, refsys, altsys, **kwargs):
        """A Validation should consider the verdict,
        and package a report around it.

        Parameters
        -----------
        @refsys: MeasurableSystem
        @altsys: MeasurableSystem

        @kwargs: A concrete implementation may use kwargs to provide some other
        arguments like a pvalue_threshold

        Return
        -------
        A Pronouncement"""

        return Pronouncement(refsys,
                             altsys,
                             self.phenomenon_compared(),
                             self.statistical_test_used(),
                             self.render_verdict(refsys, altsys, **kwargs),
                             **kwargs)

    @abstractmethod
    def statistical_test_used(self):
        """@attr: StatisticalTest,
        used to compare alternative system against the reference."""
        pass

    @abstractmethod
    def render_verdict(self, reference, alternative, **kwargs):
        """A Validation will pass verdicts.
        The function call must be made with at least a reference, and an
        alternative system that can be measured. These systems must provide a
        measurement for the quantity required by a concrete implementation of
        this abstract base class.

        Parameters
        ----------
        @reference: MeasurableSystem
        @alternative: MeasurableSystem

        @kwargs: A concrete implementation may use kwargs to provide some other
        arguments, like a pvalue_threshold

        Return
        ----------
        A Verdict"""
        pass


class ModelValidation(Validation):
    """ModelValidation is a Comparison of a model against reality (i.e. experimental 
    data source). A Validation will pass a judgment.
