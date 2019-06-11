"""
Prototypes and documentation to help us develop Observation
"""

from abc import\
    abstractmethod
import pandas as pd
from ..field import\
    Field,\
    ClassAttribute,\
    WithFields,\
    ClassAttributeMetaBase

from ..quantity import Quantity


#move this helper method elsewhere
def get_label(something):
    """
    Get label of something that may have a label attribute.
    """
    if isinstance(something, str):
        return something
    if isinstance(something, dict):
        return something.get("label", "unavailable")
    return getattr(
        something, "label",
        "unavailable_{}".format(
            something.__class__.__name__))


class MissingObservationParameter(Exception):
    """
    Exception that will be thrown when a data does not provide one of the
    Observation's parameters.
    """
    pass


class MissingObservedVariable(Exception):
    """
    Exception that will be thrown when a data does not provide an observed
    variable.
    """
    pass


class ObservationMetaClass(
        ClassAttributeMetaBase):
    """
    A metaclass to define Observation classes.

    This metaclass enforces that a class representing an Observation
    must define class attributes 'parameters' and 'phenomenon'. 
    """

    #knowledge level
    #class attributes that define an Observation
    parameters = ClassAttribute(
        """
        A dict mapping the name of each variable parameterizing this
        observation / measurement to its description.
        The names will be used to name the dataframe indices,
        and the descriptions to provide documentation.
        """,
        __type__=dict)
    phenomenon = ClassAttribute(
        """
        Phenomenon observed.
        """)


class Observation(
        WithFields,
        metaclass=ObservationMetaClass):
    """
    Observation of a phenomenon.

    We model an Observation as a callable.
    We expect the measured system to be complex,
    whose description requires several dimensions.
    For example, a model of a brain circuit's properties can be observed as 
    functions of spatial variables X, Y, and Z, or as functions of biologically
    meaningful variables such as brain-regions, cortical layers
    and columns. Such spatial properties include cell density,
    synapse densities, and firing rates. In addition to spatial parameters,
    we may want to add synapse-class to the set of parameters conditioning the
    measurement. Such a measurement would have a separate entry for
    inhibitory and excitatory neurons for each combination of the
    spatial variables.
    """

    __metaclass_base__ = True

    #operational level
    #attributes that will depend on the instance 
    objectOfObservation = Field(
        """
        The object that was observed. It is not expected to be a simple object.
        It may be implemented as a Python object, or as a dict maps all the
        relevant attribute names to their values, or even an informal string
        that describes all of the observed object's relevant attributes.
        """,
        __default_value__="not-available")
    data = Field(
        """
        Data resulting from this Observation.
        This data should contain all parameter, phenomenon value combinations.
        The simplest data-structure to use would be a dict, while a Pandas
        data-frame would be the most convenient.
        """)
    procedure = Field(
        """
        Description of how this Observation / Measurement was made.
        """,
        __default_value__="not-available")
    label = Field(
        """
        A string to name a Data instance. 
        """,
        __type__=str,
        __required__=True)
    provenance = Field(
        """
        Description of the origin of this data.
        """,
        __type__=object,
        __default_value__="Unknown")

    def __init__(self,
            data,
            *args, **kwargs):
        """..."""
        assert self.check_validity(data)
        super().__init__(
            *args,
            data=data,
            **kwargs)

    @property
    def properties_observed(self):
        """
        Properties observed.

        Returns
        -------
        A list of the properties(variable names) observed.
        By default, we assume that only a single variable,
        labeled by the phenomenon is observed. However, if the
        observation is reported as a statistical summary of a
        measure of the phenomenon, ['mean', 'error', 'sample_size']
        make more sense.
        """
        return [get_label(self.phenomenon)]

    @staticmethod
    def _check_variables(data_value, variable_list):
        """
        Check that the list of variables in variable_list is
        provided by data in data_value
        """
        if isinstance(data_value, list):#a list of dicts
            for d in data_value:
                if not isinstance(d, dict):
                    break
                for v in variable_list:
                    if v not in d:
                        raise ValueError(
                            """
                            '{}' not provided by dict {}.
                            """.format(v, d))
            return True

        if isinstance(data_value, pd.DataFrame):
            for p in variable_list:
                if p not in data_value.columns:
                    raise ValueError(
                        """
                        '{}' not provided by data-frame columns {}
                        """.format(p, data_value.columns))
            return True

        raise TypeError(
            """
            Valid data of an Observation should be either a list of dicts,
            or a Pandas DataFrame object. {} is neither.
            """.format(data_value.__class__.__name__))
    
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
            self._check_variables(data_value, self.parameters)
        except ValueError as error:
            raise MissingObservationParameter(*error.args)
        finally:
            pass

        try:
            self._check_variables(data_value, [get_label(self.phenomenon)])
        except ValueError as error:
            raise MissingObservedVariable(*error.args)
        finally:
            pass

        return True

    @property
    def dataframe(self):
        """
        Data as a dataframe.
        """
        return pd.DataFrame(self.data)\
                 .set_index(list(self.parameters))

    @property
    def loc(self):
        """..."""
        return self.dataframe.loc

    @property
    def iloc(self):
        """..."""
        return self.dataframe.iloc

    @property
    def what(self):
        """Needs improvement"""
        return "{}\n Provided by {}"\
            .format(
                self.__class__.__doc__.strip(),
                self.provenance)

    def __call__(**params):
        """
        Result of this measurement for the parameters in the
        keyword arguments 'params'.

        Arguments
        ----------
        params :: keyword arguments containing each parameter in
        'Field parameters' as a keyword.
        """
        raise NotImplementedError()

from .measurement import Measurement
