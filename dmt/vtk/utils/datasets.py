import os
import yaml
from dmt.vtk.utils.collections import Record

def load_file(fpath, load):
    """
    Load dataset from a file sitting at fpath,
    using the loader 'load'
    @param fpath: path to the file.
    @param load:  function to load the file (like yaml.load, or json.load)
    @return: python dict
    """
    with open(fpath) as f:
        return Record(**load(f))

def load_yaml(dpath, file_name):
    """
    Load YAML dataset by name.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @return: python dict
    """
    return load_file(os.path.join(dpath, file_name + ".yaml"), yaml.load)

def load_json(dpath, file_name):
    """
    Load JSON dataset by name.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @return: python dict
    """
    return load_file(dpath, file_name + ".json", json.load)

def load(dpath, file_name, dtype="YAML"):
    """
    Load dataset by name. The dataset file may be either YAML or JSON.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @param dtype:     type of the dataset file (YAML/JSON)
    @return: python dict
    """

    if dtype.lower() == "yaml": return load_yaml(dpath, file_name)
    elif dtype.lower() == "json": return load_json(dpath, file_name)
    else:
        raise ValueError(
            "datasets of type " + dtype + " unknown / unimplemented")




