# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 
"""
Analyses and validations for the circuit connectome.
"""

from neuro_dmt.library.analyses.circuit.connectome.suite\
    import AdapterInterface
from neuro_dmt.library.analyses.circuit.connectome.tools.pathway_measurement
    import PathwayMeasurement

def number_connections_afferent(target):
    """

    Arguments
    --------------
    target :: Mapping describing the subset of cells between which the
    ~         connections will be analyzed.
    """
    phenomenon =\
        Phenomenon(
            "Number Afferent Connections",
            description="Number of afferent connections.",
            group="Connectome")
    pathway_measurement =\
        PathwayMeasurement(
            direction="AFF",
            value=lambda connections: 1,
            variable=phenomenon.label,
            specifiers_cell_type=["mtype"],
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            processing_methodology=terminology.processing_methodology.batch,
            batch_size=1000,
            return_primary_info=True,
            target=lambda model, adapter: adapter.get_cells(model, **target))
    introduction =\
        """
        Number of afferent connections of a cell.
        """
    methods =\
        """
        Number of afferent connections in mtype-->mtype pathways were counted.
        """
    def mtypes(adapter, circuit_model):
        return pd.DataFrame(
            adapter.get_mtypes(circuit_model),
            columns=pd.MultiIndex.from_tuples([
                ("post_synaptic_cell_group", "mtype")]))
   return\
        BrainCircuitAnalysis(
            phenomenon=phenomenon,
            introduction=introduction,
            methods=methods,
            AdapterInterface=AdapterInterface,
            measurement_parameters=Parameters(mtypes, labels=["mtype"]),
            sample_measurement=pathway_measurement.collector(),
            measurement_collection=measurement.collection.series_type,
            processing_methodology=terminology.processing_methodology.serial,
            sampling_methodology=terminology.sampling_methodology.exhaustive,
            plotter=MultiPlot(
                mvar=("post_synaptic_cell", "mtype"),
                plotter=Bars(
                    xvar=("pre_synaptic_cell", "mtype"),
                    xlabel="Pre-synaptic Cell Mtype",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name)))
