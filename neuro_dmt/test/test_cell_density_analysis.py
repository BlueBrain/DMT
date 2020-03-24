import pandas as pd
from dmt.tk.terminology.data import data as data
from dmt.tk.plotting import Bars
# TODO: perhaps eventually we will prefer to have BrainCircuitAnalysis,
#       BlueBrainCircuitAdapter, and BlueBrainCircuitModel
#       (as the most commonly used parts) available from one high-level module
#       neuro_dmt directly? or neuro_dmt.library? neuro_dmt.library.bluebrain?
from neuro_dmt.terminology import circuit, cell
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainCircuitAdapter
from neuro_dmt.models.bluebrain.circuit import BlueBrainCircuitModel
from neuro_dmt.models.adapters import AtlasAdapter
from neuro_dmt.models.bluebrain.circuit.atlas import BlueBrainCircuitAtlas



"""
create cell density measurement_method. Could be a class with __call__,
but here a function suffices
"""
from dmt.tk.terminology import Term


def cell_density(model, adapter, **parameters):
    """get cell density for a model through its adapter"""
    return adapter.get_cell_density(model, **parameters)
cell_density.phenomenon = Term("cell density", "number of cells per mm^3")


"""
create a cell density analysis with default measurements_parameters
(default is to replicate reference_data)
"""
class AdapterInterface:
    """
    Interface for any cell density validation
    """
    def get_cell_density(self, model, **params):
        """get the cell density from the model"""
        raise NotImplementedError()


DataReplicationCellDensityAnalysis = BrainCircuitAnalysis(
    measurement_method=cell_density,
    plotter=Bars(),
    default_adapter=BlueBrainCircuitAdapter(),
    AdapterInterface=AdapterInterface)


class TestNCXO1:

    circuit_config =\
        "/gpfs/bbp.cscs.ch/project/proj68/circuits/O1/20190307/CircuitConfig"
    circuit_model = BlueBrainCircuitModel(circuit_config)

    def test_NCX_O1_by_layer(self):
        """
        basic cell density by layer validation
        """
        by_layer_example_cell_density = pd.DataFrame(
            {circuit.layer: [L for L in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
                             for n in range(3)],
             data.samples: [100000, 110000, 90000,
                            120000, 130000, 140000,
                            110000, 200000, 60000,
                            130000, 130000, 130000,
                            100000, 130000, 160000,
                            231000, 214000, 121000]})

        example_report = DataReplicationCellDensityAnalysis.with_fields(
            reference_data=by_layer_example_cell_density)\
            ((self.circuit_model, BlueBrainCircuitAdapter()))
        assert example_report.figure

    def test_NCX_O1_by_layer_and_sclass(self):
        """
        sometimes will want to have multiple parameters, or multiple
        values for a parameter.
        """
        EXC_by_layer_data = pd.DataFrame({
            circuit.layer: [['L2', 'L3'], ['L4'], ['L5'], ['L6']],
            cell.synapse_class: 'EXC',
            data.samples: [120000, 100000, 200000, 100000]
        })
        EXC_by_layer_report = DataReplicationCellDensityAnalysis.with_fields(
            reference_data=EXC_by_layer_data)(self.circuit_model)


class TestAtlasAnalysis:
    """
    We've used my prototype before to analysze atlases.
    The full framework should be just as capable
    """

    def test_thalamus_densities(self):
        thalamus_atlas = BlueBrainCircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj55/entities/atlas/20190628/")
        thalamus_atlas.label = "Thalamus Atlas"

        DataReplicationCellDensityAnalysis.with_fields(
            reference_data=pd.DataFrame({
                data.samples: [72802.84, 65364.87, 56678.06, 75391.47],
                circuit.region: ['RT', '@VPL|VPM', 'VPL', 'VPM']}))\
            ((thalamus_atlas, AtlasAdapter()))

    def test_dissemination_density_checks(self):
        import yaml
        DefilipeDatapath = "/gpfs/bbp.cscs.ch/project/proj64/"\
                           "dissemination data/DeFelipe2017.yaml"
        with open(DefilipeDatapath) as DFDF:
            DFDict = yaml.load(DFDF)

        DefilipeCellDensityData = {
            subj: pd.DataFrame([
                {circuit.layer: "L{}".format(l),
                 data.mean: DFDict['circuits'][subj]['densities'][l]}
                for l in range(1, 6)])
            for subj in DFDict['circuits'].values()}

        rat = "P14-12"
        ratlas = BlueBrainCircuitAtlas("/gpfs/bbp.cscs.ch/project/proj64/"
                                       "dissemination/data/atlas/O1/DAN/"+rat)
        DataReplicationCellDensityAnalysis.with_fields(
            reference_data=DefilipeCellDensityData[rat])\
            ((ratlas, AtlasAdapter()))
