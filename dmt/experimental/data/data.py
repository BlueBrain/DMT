"""
Prototype for Data.
"""
import pandas as pd
from dmt.v2.tk.field import Field, WithFields

class Data(WithFields):
    """
    Well documented data.
    Each attribute must be well documented, such that their documentation
    can be assembled to produce documentation for the entire class.
    """
    index = Field("""
        A dict mapping the name of an index variable to its description.
        The names will be used to name the dataframe index,
        and the description to provide documentation.""",
        __type__=dict)
    measurements = Field("""
        A dict mapping the name of measurement variable to its description.
        The names will be used to name the dataframe columns, 
        and the description to provide documentation.""",
        __type__=dict)
    data =\
        Field("""
            A list of dicts that can be used to construct a pandas.DataFrame.""",
            __type__=list,
            __required__=False)
    def __init__(self,
            data_dicts,
            *args, **kwargs):
        """..."""
        kwargs["data"] = data_dicts
        super().__init__(
            *args, **kwargs)
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
