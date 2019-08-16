"""
Utility methods to load datasets.
"""
import os
import yaml
import pandas

def load_file(path_file, method_load):
    """
    Load dataset from the file a `path_file`,
    using loader `method_load`.
    """
    with open(path_file, 'r') as file_data:
        return method_load(file_data)
        #return pandas.Series(**method_load(file_data))

def load_yaml(path_dir, name_data):
    """
    Load YAML file named `name_data.yaml` sitting under directory `path_dir`.
    """
    return load_file(
        os.path.join(path_dir, "{}.yaml".format(name_data)),
        lambda data_file: yaml.load(data_file, Loader=yaml.FullLoader))

def load_json(path_dir, name_data):
    """
    Load JSON file named `name_data.json` sitting under directory `path_dir`.
    """
    return load_file(
        os.path.join(path_dir, "{}.json".format(name_data)),
        json.load)

def load(path_dir, name_data, dtype="YAML"):
    """
    ...
    """
    if dtype.lower() == "yaml":
        return load_yaml(path_dir, name_data)
    if dtype.lower() == "json":
        return load_json(path_dir, name_data)

    raise ValueError(
        "Loaders for datasets of type {} have not been implemented.")
