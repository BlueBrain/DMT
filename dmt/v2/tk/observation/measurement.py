from ..observation import *

class Measurement(
        Observation):
    """
    Measurement is an Observation of a phenomenon described by a numerical
    variable.
    """
    __metaclass_base__ = True

    pass


class StatisticalMeasurement(Measurement):
    """
    A statistical measurement assumes sampling.
    Either the sampled observations are available,
    or a statistical summary is available.
    """

    __metaclass_base__ = True

    def check_validity(self, data_value):
        """
        Check the validity of data in data_value.

        1. Check that all parameters are available in 'data_value'.
        ~  All Observations will have parameters, so we can check their
        ~  validity here.
        2. Check that all the observed variables are in 'data_value'.
        ~  By default, we assume that this Observation's phenomenon provides
        ~  the variable name that labels it's associated data in a dict
        ~  or a data-frame. However, if a statistical summary is provided as
        ~  data, we should expect 'mean' and 'error' as the observed variables. 

        Arguments
        ---------------
        data_value :: Either a list of dicts or a pandas dataframe
        """
        try:
            super().check_validity(data_value)
        except MissingObservationParameter as error:
            raise error
        except MissingObservedVariable as error:
            try:
                self._check_variables(data_value, ["mean", "error"])
            except ValueError as error:
                raise MissingObservedVariable(*error.args)
            finally:
                pass
        finally:
            pass
        return True


    @property
    def summary(self):
        """
        A statistical summary of the data in this measurement.
        As of <20190612>, we assume that the data stored in this statistical
        measurement is itself a summary. This assumption may not apply when we
        store the full observed dataset.
        """
        return self.dataframe
