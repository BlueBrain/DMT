"""Behavior of a validation expressed as an abstract base class.
"""

from abc import ABC, abstractmethod
from dmt.validation import Pronouncement

class ValidationBase(ABC):
    """Behavior of a Validation that may be called.

    TODO
    -----
    Where should we make the plots?
    Whose responsibility is it?
    render_verdict's?

    We want to have at least two kinds of Pronouncements --- to enable those
    many Validation types. We can have a Pronouncement with output directory
    information, versus another which does not have this information --- which
    should be the case for an interactive session. 
    """

    def __call__(self, reference, alternative, **kwargs):
        """A Validation may be called.
        The call must be made with at least a reference, and an alternative
        MeasurableSystem,

        Parameters
        -----------
        @reference : MeasurableSystem
        @alternative : MeasurableSystem

        kwargs may provide an output directory.
        We do not make it explicitly necessary as we may want the user to use 
        this framework interactively.

        Return
        --------
        The concrete class may decide what to return."""
        p = pronouncement()


    def pronouncement(self, reference, alternative, **kwargs):
        """A Validation should consider the verdict,
        and package a report around it.

        Parameters
        -----------
        @reference: MeasurableSystem
        @alternative: MeasurableSystem

        @kwargs: A concrete implementation may use kwargs to provide some other
        arguments like a pvalue_threshold

        Return
        -------
        A Pronouncement"""

        return Pronouncement(reference,
                             alternative,
                             self.phenomenon_compared(),
                             self.statistical_test_used(),
                             self.render_verdict(reference, alternative, **kwargs)
                             **kwargs)

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

