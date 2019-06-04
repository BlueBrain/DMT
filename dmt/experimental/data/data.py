"""
Prototype for Data.
"""
from abc import ABCMeta
import pandas as pd
from dmt.v2.tk.field import Field, WithFields

class Data(WithFields):
    """
    Well documented data.
    Each attribute must be well documented, such that their documentation
    can be assembled to produce documentation for the entire class.
    """
    label = Field("""
        A string to name a Data instance""",
        __type__=str,
        __required__=False)
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
    contents = Field("""
        A list of dicts that can be used to construct a pandas.DataFrame.""",
        __type__=list,
        __required__=False)

    @property
    def dataframe(self):
        """
        Data as a dataframe.
        """
        return pd.DataFrame(self.contents)\
                 .set_index(list(self.index))
   
    @property
    def loc(self):
        """..."""
        return self.dataframe.loc
        
    @property
    def iloc(self):
        """..."""
        return self.dataframe.iloc

    def __call__(self, data_dicts, label):
        """
        Create Data instance containing actual data in addition to description.

        Arguments
        ------------
        data_dicts :: list of dicts that provide single entry of the data.
        Each of these dicts must have this Data instances' index names
        and measurement names as keys.
        """
        for d in data_dicts:
            for i in self.index.keys():
                if i not in d.keys():
                    raise ValueError(
                        """Missing data index '{}' in dict {}""".format(i, d))
            for m in self.measurements.keys():
                if m not in d.keys():
                    raise ValueError(
                        """Missing measurement '{}' in dict {}""".format(i, m))

        return Data(
            label=label,
            index=self.index,
            measurements=self.measurements,
            contents=data_dicts)
