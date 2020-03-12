"""
Analyses, designed for the SSCx Dissemination circuits.
"""
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dmt.data.observation import measurement
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, LinePlot, HeatMap
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.field import NA, Record, Field, LambdaField, lazyfield, WithFields
from neuro_dmt import terminology
from neuro_dmt.models.bluebrain.circuit.atlas import\
    BlueBrainCircuitAtlas
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.adapter import\
    BlueBrainCircuitAdapter
from neuro_dmt.analysis.circuit import\
    BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitProvenance,\
    CircuitAnalysisReport,\
    CheetahReporter
from .tools import PathwayMeasurement
from .composition import CompositionAnalysesSuite
from .connectome import ConnectomeAnalysesSuite


class SSCxDisseminationCircuits(WithFields):
    """
    A class to help with loading SSCx Dissemination circuits.
    """
    path_base = Field(
        """
        Path to the base location...
        """,
        __default_value__="/gpfs/bbp.cscs.ch/project")

    folder = Field(
        """
        Folder for the SSCx Dissemination project under base.
        """,
        __default_value__="proj83")

    @lazyfield
    def home(self):
        return os.path.join(self.path_base, self.folder)

    folder_inputs = Field(
        """
        Folder under base where the input data for SSCx Dissemination circuits
        sits.
        """,
        __default_value__="data")
    folder_atlas = Field(
        """
        Folder for the atlases, under the folder for inputs
        """,
        __default_value__="atlas")
    folder_circuits = Field(
        """
        Folder under base where the circuits are located.
        """,
        __default_value__="circuits")

    def path_atlas(self, circuit="Bio_M/20191206"):
        return os.path.join(
            self.home, self.folder_inputs,
            self.folder_atlas, self.type_atlas,
            self.folder_circuits, circuit)

    def atlas(self, circuit="Bio_M/20191206"):
        """
        Atlas for a circuit.

        For now we assume that argument `circuit` is a string label...

        TODO:  load the atlas from the circuit's bioname...
        """
        return BlueBrainCircuitAtlas(path=self.path_atlas(circuit))

    def path_circuit(self, circuit="Bio_M/20191206"):
        return os.path.join(self.home, self.folder_circuits, circuit)

    @staticmethod
    def _get_variation(circuit):
        """
        Change this method when format of argument `circuit` changes.
        """
        try:
            variation, release_date = tuple(circuit.split('/'))
        except (AttributeError, TypeError, IndexError, ValueError):
            variation = ""
            release_date = "XXXXYYZZ"

        return Record(
            variation=variation,
            label="SSCxVariant{}".format(variation),
            release_date=release_date)


    @lazyfield
    def mock_circuit(self):
        """
        Use this mock circuit to develop analyses.
        """
        from neuro_dmt.models.bluebrain.circuit.mock.circuit import\
            MockBlueBrainCircuitModel
        from neuro_dmt.models.bluebrain.circuit.mock.test.mock_circuit_light\
            import circuit_composition, circuit_connectivity
        return\
            MockBlueBrainCircuitModel(
                circuit_composition,
                circuit_connectivity,
                label="SSCxMockCircuit")

    def get(self, circuit):

        try:
            circuit = getattr(self.variations, circuit)
        except AttributeError:
            pass

        if circuit == "MOCK":
            return self.mock_circuit

        path_circuit = self.path_circuit(circuit)
        variation_circuit = self._get_variation(circuit)

        return BlueBrainCircuitModel(
            path_circuit_data=self.path_circuit(circuit),
            provenance=CircuitProvenance(
                label=variation_circuit.label,
                authors=["BBP-Team"],
                release_date=variation_circuit.release_date,
                uri=path_circuit,
                animal="Wister Rat",
                age="P14",
                brain_region="SSCx"))

    @lazyfield
    def adapter(self):
        return BlueBrainCircuitAdapter()

    @lazyfield
    def variations(self):
        return Record(
            biom="Bio_M/20191206",
            bio0=NA,
            bio1=NA,
            bio2=NA,
            bio3=NA,
            bio4=NA,
            bio5=NA,
            mock="MOCK")


class AnalysisSpec(WithFields):
    """
    Parameterize an analysis.
    "    """
    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=100)
    size_roi = Field(
        """
        Size of ROIs that composition phenomena will be computed in.
        """,
        __default_value__ = 50. * np.ones(3))
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.path.join(os.getcwd(), "reports"))
    morphologies_interneurons = Field(
        """
        Interneuron morphologies that are stained by markers",
        """,
        __default_value__=["BP", "BTC", "CHC", "DB", "LBC", "NBC", "MC", "SBC", "SSC"])
    number_cortical_thickness_bins = Field(
        """
        Number of bins for by depth / height analyses.
        """,
        __default_value__=50)

""
