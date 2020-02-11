from dmt.tk.plotting import Bars
from dmt.tk.reporting import Reporter
from dmt.model.interface import Interface
from dmt.analysis.structured import StructuredAnalysis
from validations.measurements import \
    CellDensityMeasurement, InhibitoryProportionMeasurement, SynapseDensityMeasurement,\
    ConnectionProbabilityMeasurement,\
    cell_density, inhibitory_proportion, synapse_density


BarplotValidation = StructuredAnalysis(AdapterInterface=Interface,
                                       plotter=Bars(), reporter=Reporter())

CellDensityValidation = BarplotValidation.with_fields(
    measurement_method=CellDensityMeasurement())

InhibitoryProportionValidation = BarplotValidation.with_fields(
    measurement_method=InhibitoryProportionMeasurement())

SynapseDensityValidation = BarplotValidation.with_fields(
    measurement_method=SynapseDensityMeasurement())

ConnectionProbabilityValidation = BarplotValidation.with_fields(
    measurement_method=ConnectionProbabilityMeasurement())
