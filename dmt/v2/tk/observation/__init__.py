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
    return getattr(
        something, "label",
        "unavailable_{}".format(
            something.__class__.__name__))


class ObservationMetaClass(
        ClassAttributeMetaBase):
    """
    A metaclass to define Observation classes.

    This metaclass enforces that a class representing an Observation
    must define class attributes 'parameters' and 'phenomenon'. 
    """

    #knowledge level
    #class attributes that define an Observation
    objectOfObservation = ClassAttribute(
        """
        The object that was observed. It is not expected to be a simple object.
        It may be implemented as a Python object, or as a dict maps all the
        relevant attribute names to their values, or even an informal string
        that describes all of the observed object's relevant attributes.
        """,
        __default_value__="not-available")
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
        kwargs["data"] = data

        super().__init__(
            *args, **kwargs)

    def check_validity(self, data_value):
        """
        Check the validity of data in data_value.

        Arguments
        ---------------
        data_value :: Either a list of dicts or a pandas dataframe
        """
        pheno_label = get_label(self.phenomenon)
        if isinstance(data_value, list): #a list of dicts
            for d in data_value:
                if not isinstance(d, dict):
                    break
                for p in self.parameters:
                    if p not in d:
                        raise ValueError(
                            """
                            Missing (parameter) variable '{}' in dict {}.
                            """.format(p, d))
                if  pheno_label not in d:
                    raise ValueError(
                    """
                    Missing (observed) variable '{}' in dict {}. 
                    """.format(pheno_label, d))
                return True

        if isinstance(data_value, pd.DataFrame):
            for p in self.parameters:
                if p not in data_value.columns:
                    raise ValueError(
                        """
                        Missing column '{}' in dataframe with columns {}.
                        """.format(p, data_value.columns))
                if pheno_label not in data_value.columns:
                    raise ValueError(
                        """
                        Missing column '{}' in dataframe with columns {}.
                        """.format(pheno_label, data_value.columns))
                return True

        raise TypeError(
            """
            Valid data of an Observation should be either a list of dicts,
            or a Pandas DataFrame object. {} is neither.
            """.format(data_value.__class__.__name__))

    @property
    def dataframe(self):
        """
        Data as a dataframe.
        """
        return pd.DataFrame(self.data)\
                 .set_index(list(self.index))

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


class Measurement(Observation):
    """
    Measurement is an Observation whose result is quantitative, 
    which means that it can be measured as a number.
    """
    
    __metaclass_base__ = True
    
    pass
