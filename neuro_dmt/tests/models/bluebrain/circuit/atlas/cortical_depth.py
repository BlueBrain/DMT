"""Test and develop cortical depth analysis and plots."""

import os
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.plotting\
    import BarPlot, LinePlot
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import AtlasRegion, CorticalLayer, CorticalDepth
from neuro_dmt.models.bluebrain.circuit.random_variate\
    import RandomRegionOfInterest
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter
from neuro_dmt.library.bluebrain.circuit.models.sscx\
    import get_sscx_fake_atlas_circuit_model

sscx_circuit_config=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/project/proj64/circuits",
        "O1.v6a/20181207/",
        "CircuitConfig")
sscx_circuit_model=\
    get_sscx_fake_atlas_circuit_model(
        sscx_circuit_config,
        "rat")
sscx_adapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)
cell_density_by_cortical_depth=\
    sscx_adapter.get_cell_density(
        sscx_circuit_model,
        spatial_parameters={
            AtlasRegion(values=["mc{}_Column".format(i) for i in range(7)]),
            CorticalDepth()})
cell_density_by_depth_plotter=\
    LinePlot(
        cell_density_by_cortical_depth
    ).plotting(
        "cell_density"
    ).versus(
        "depth"
    ).given(
        region="mc2_Column"
    ).with_customization(
        title="Somatosensory cortex cell density",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_sscx_analysis"))
cell_density_by_depth_plotter.save(
    cell_density_by_depth_plotter.plot(),
    file_name="cell_density_by_cortical_depth.png")

cell_density_by_cortical_layer=\
    sscx_adapter.get_cell_density(
        sscx_circuit_model,
        spatial_parameters={
            AtlasRegion(values=["mc{}_Column".format(i) for i in range(7)]),
            CorticalLayer()})
cell_density_by_layer_plotter=\
    BarPlot(
        cell_density_by_cortical_layer,
    ).plotting(
        "cell_density"
    ).versus(
        "layer"
    ).given(
        region="mc2_Column"
    ).with_customization(
        title="Somatosensory cortex cell density",
        output_dir_path=os.path.join(
            os.getcwd(),
            "test_sscx_analysis"))
cell_density_by_layer_plotter.save(
    cell_density_by_layer_plotter.plot(),
    file_name="cell_density_by_cortical_depth.png")

