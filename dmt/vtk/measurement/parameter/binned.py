"""A binned parameter."""
from abc\
    import abstractmethod
from dmt.vtk.utils.exceptions\
    import OutOfRangeError
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.measurement.parameter\
    import Parameter

class BinnedParameter(
        Parameter):
    """A binned parameter"""

    elem_type  = Field(
        __name__="elem_type",
        __type__=type,
        __doc__="""Type of the elements in the bins.
        We expect bins to contain the same type of elements""")
    value_type = Field(
        __name__ = "value_type",
        __type__ = type,
        __doc__  = """Type of the bins.
        For ordered types like float, value_type of
        the bins can be a Tuple, for example Tuple(float, float)""",
        __examples__=[(float, float), (int, int) ])
    
    @abstractmethod
    def __contains__(self,
            value_x):
        """is value_x in this bin."""
        pass

    @abstractmethod
    def get_bin(self,
            value_x):
        """Get bin for value_x"""
        pass

