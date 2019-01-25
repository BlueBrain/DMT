import os
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.plotting\
    import BarPlot, LinePlot
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion, CorticalLayer, CorticalDepth
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import *
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import *
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.library.bluebrain.circuit.models.sscx\
    import get_rat_sscx_O1_circuit_model,\
    get_sscx_fake_atlas_circuit_model
from neuro_dmt.library.bluebrain.circuit.models.iso_cortex\
    import get_iso_cortex_circuit_model

iso_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj68/circuits",
        "dev-large/20180904/",
        "CircuitConfig")
iso_circuit_model=\
    get_iso_cortex_circuit_model(
        iso_circuit_config,
        "mouse")
iso_adapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.cortex,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
iso_geometry=\
    iso_circuit_model.geometry
random_pos=\
    iso_geometry.random_position(
        condition=Condition([
            ("region", "SSp-ll"),
            ("depth", 0.1)]))
# iso_cortex_layer_cell_density=\
#     iso_adapter.get_cell_density(
#         iso_circuit_model,
#         spatial_parameters={
#             AtlasRegion(values=["SSp-ll"]),
#             CorticalLayer()})
iso_cortex_depth_cell_density=\
    iso_adapter.get_cell_density(
        iso_circuit_model,
        spatial_parameters={
            AtlasRegion(values=["SSp-ll"]),
            CorticalDepth()})
iso_cortex_bar_plotter=\
    BarPlot(
        iso_cortex_depth_cell_density,
        title="Iso Cortex SSp-ll Cell Density",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_iso_cortex_analysis"))
iso_cortex_line_plotter=\
    LinePlot(
        iso_cortex_depth_cell_density
    ).plotting(
        "cell_density"
    ).versus(
        "depth"
    ).given(
        region="SSp-ll"
    ).with_customization(
        title="Iso Cortex SSp-ll Cell Density",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_iso_cortex_analysis"))
iso_cortex_cell_density_plot=\
    iso_cortex_line_plotter.plot()
iso_cortex_line_plotter.save(
    iso_cortex_cell_density_plot)

ssp_ll_column=\
    iso_geometry.get_cortical_column(
        "SSp-ll")
