"""Analyses of the SSCx composition by cortical depth."""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

project_path=\
        "/gpfs/bbp.cscs.ch/project/proj64"
circuit_config= {
    "20171212": os.path.join(
        project_path, "circuits",
        "O1.v6a", "20171212", "CircuitConfig"),
    "20181205": os.path.join(
        project_path, "circuits",
        "O1.v6a", "20181205", "CircuitConfig"),
    "20181207": os.path.join(
        project_path, "circuits",
        "O1.v6a", "20181207", "CircuitConfig")}
atlas_path= {
    "20171212": os.path.join(
        project_path, "entities",
        "dev", "atlas",
        "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"),
    "20181205": os.path.join(
        project_path, "entities",
        "dev", "atlas",
        "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"),
    "20181207": os.path.join(
        project_path, "entities",
        "dev", "atlas",
        "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018") }

sscx_adapter=\
    BlueBrainModelAdapter(
        brain_region=brain_regions.sscx,
        spatial_random_variate=RandomRegionOfInterest,
        model_label="in-silico",
        sample_size=20)

def run_analysis(
        circuit_release_date,
        sample_size=20,
        Plotter=LinePlot,
        file_format="png",
        *args, **kwargs):
    """..."""
    sscx_circuit_model=\
        get_sscx_fake_atlas_circuit_model(
            circuit_config[circuit_release_date],
            "rat",
            atlas_path=atlas_path[circuit_release_date])

    def _all_permissible(*args, **kwargs):
        return True

    def index_with_two_decimal_point_depth(dataframe):
        dataframe_no_index = dataframe.reset_index()
        dataframe.index = pd.MultiIndex.from_tuples(
            list(zip(
                dataframe_no_index.region,
                np.round(dataframe_no_index.depth, 2))),
            names=["region", "depth"])

        return dataframe

    synapse_density_by_depth=\
        sscx_adapter.get_synapse_density(
            sscx_circuit_model,
            spatial_parameters={
                AtlasRegion(values=["mc2_Column"]),
                CorticalDepth()},
            sample_size=sample_size,
            debug=True,
            is_permissible=_all_permissible)
    synapse_density_by_depth.data =\
        index_with_two_decimal_point_depth(
            synapse_density_by_depth.data)
    synapse_density_plotter=\
        Plotter(
            synapse_density_by_depth,
            drawstyle="steps-mid"
        ).plotting(
            "synapse_density"
        ).versus(
            "depth"
        ).given(
            region="mc2_Column"
        ).with_customization(
            title="Somatosensory cortex synapse density",
            output_dir_path=os.path.join(
                os.getcwd(),
                "test_sscx_analysis"))
    syn_plot_figure=\
        synapse_density_plotter.plot(
            {"xticks_rotation": 90})


    max_error=\
        synapse_density_by_depth.data["in-silico"]["std"].max()
    ymin=\
        synapse_density_by_depth.data["in-silico"]["mean"].min() - max_error
    ymax=\
        synapse_density_by_depth.data["in-silico"]["mean"].max() + max_error

    layer_pos=\
        sscx_circuit_model\
        .geometry\
        .get_layer_depths(
            "mc2_Column",
            as_fractions=True)

    if Plotter == BarPlot:
        N = synapse_density_by_depth.data.shape[0]
        layer_pos["upper_mean"] = N * layer_pos.upper_mean.values
        layer_pos["lower_mean"] = N * layer_pos.lower_mean.values

    layer_begin_end=[
        tuple(layer_pos[
            ["upper_mean", "lower_mean"]
        ][layer_pos.layer==layer].values[0])
        for layer in range(1, 7)]
    bottom = layer_begin_end[-1][1]
    layer_names=\
        ["I", "II", "III", "IV", "V", "VI"]
    layer_mids= [(b + e) / 2. for b, e in layer_begin_end]

    for (layer_begin, _) in layer_begin_end:
        plt.plot((layer_begin, layer_begin), (ymin, ymax), "k-", linewidth=4)
    plt.plot((bottom, bottom), (ymin, ymax), "k-", linewidth=4)
    plt.xticks(layer_mids, layer_names, fontsize=20)

    synapse_density_plotter.save(
        syn_plot_figure,
        file_name="synapse_density_by_depth.{}".format(file_format),
        file_format=file_format)

    exc_syn_data_by_depth=\
        sscx_adapter.get_excitatory_synapse_density(
            sscx_circuit_model,
            spatial_parameters={
                AtlasRegion(values=["mc2_Column"]),
                CorticalDepth()},
            sample_size=sample_size,
            debug=True,
            is_permissible=_all_permissible)

    exc_syn_data_by_depth.data =\
        index_with_two_decimal_point_depth(
            exc_syn_data_by_depth.data)
    exc_syn_density_plotter=\
        Plotter(
            exc_syn_data_by_depth,
            drawstyle="steps-mid"
        ).plotting(
            "synapse_density"
        ).versus(
            "depth"
        ).given(
            region="mc2_Column"
        ).with_customization(
            title="Somatosensory cortex excitatory synapse density",
            output_dir_path=os.path.join(
                os.getcwd(),
                "test_sscx_analysis"))

    exc_syn_plot_figure=\
        exc_syn_density_plotter.plot(
            {"xticks_rotation": 90})
    
    for (layer_begin, layer_end) in layer_begin_end:
        plt.plot((layer_begin, layer_begin), (ymin, ymax), "k-", linewidth=4)
    plt.plot((bottom, bottom), (ymin, ymax), "k-", linewidth=4)
    plt.xticks(layer_mids, layer_names, fontsize=20)

    exc_syn_density_plotter.save(
        exc_syn_plot_figure,
        file_name="excitatory_synapse_density_by_depth.{}".format(file_format),
        file_format=file_format)

    inh_syn_data_by_depth=\
        sscx_adapter.get_inhibitory_synapse_density(
            sscx_circuit_model,
            spatial_parameters={
                AtlasRegion(values=["mc2_Column"]),
                CorticalDepth()},
            sample_size=sample_size,
            debug=True,
            is_permissible=_all_permissible)

    inh_syn_data_by_depth.data =\
        index_with_two_decimal_point_depth(
            inh_syn_data_by_depth.data)
    inh_syn_density_plotter=\
        Plotter(
            inh_syn_data_by_depth,
            drawstyle="steps-mid"
        ).plotting(
            "synapse_density"
        ).versus(
            "depth"
        ).given(
            region="mc2_Column"
        ).with_customization(
            title="Somatosensory cortex inhibitory synapse density",
            output_dir_path=os.path.join(
                os.getcwd(),
                "test_sscx_analysis"))

    inh_syn_plot_figure=\
        inh_syn_density_plotter.plot(
            {"xticks_rotation": 90})
    
    for (layer_begin, layer_end) in layer_begin_end:
        plt.plot((layer_begin, layer_begin), (ymin, ymax), "k-", linewidth=4)
    plt.plot((bottom, bottom), (ymin, ymax), "k-", linewidth=4)
    plt.xticks(layer_mids, layer_names, fontsize=20)

    inh_syn_density_plotter.save(
        inh_syn_plot_figure,
        file_name="inhibitory_synapse_density_by_depth.{}".format(file_format),
        file_format=file_format)
