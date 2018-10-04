
def cell_density(reference_data_path):
    from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer.cell_density \
        import get_reference_datasets
    return get_reference_datasets(reference_data_path)

def cell_ratio(reference_data_path):
    from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer.cell_ratio \
        import get_reference_datasets
    return get_reference_datasets(reference_data_path)

def inhibitory_synapse_density(reference_data_path):
    from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer.inhibitory_synapse_density\
        import get_reference_datasets
    return get_reference_datasets(reference_data_path)

def synapse_density(reference_data_path):
    from neuro_dmt.data.circuit.composition.hippocampus.ca1.by_layer.synapse_density \
        import get_reference_datasets
    return get_reference_datasets(reference_data_path)
