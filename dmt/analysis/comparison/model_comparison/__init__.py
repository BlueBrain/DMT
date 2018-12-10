"compare two models."

from dmt.model.adapter import Adapter
from dmt.analysis import Analysis
from dmt.analysis.comparison import Comparison
from dmt.vtk.utils.descriptor import Field, document_fields

@document_fields
class ModelComparison(
        Comparison):
    """Compare an alternative model against a reference model."""
    analyses=\
        Field(
            __name__="analyses",
            __type__=Analysis,
            __doc__="""The analysis to do to compare the two models.""")
    reference_adapter=\
        Field(
            __name__="reference_adapter",
            __type__=Adapter,
            __doc__="Adapter for instances of the reference model.")
    alternative_adapter=\
        Field.Optional(
            __name__="alternative_adapter",
            __type__=Adapter,
            __doc__="""Adapter for instances of the alternative model.
            If not provided, reference adapter will be used.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args,
            **kwargs)

    @property
    def reference_data_for_statistical_comparison(self):
        """..."""
        return self.reference_data

    def get_reference_measurement(self,
            reference_model,
            *args, **kwargs):
        """Get measurement for the reference model."""
        return self.reference_analyses.get_measurement(reference_model)

    def get_alternative_measurement(self,
            alternative_model,
            *args, **kwargs):
        """..."""
        return self.alternative_analysis.get_measurement(alternative_model)
        
