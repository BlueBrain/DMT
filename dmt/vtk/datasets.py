import os
import yaml

def load_file(fpath, load):
    """
    Load dataset from a file sitting at fpath,
    using the loader 'load'
    @param fpath: path to the file.
    @param load:  function to load the file (like yaml.load, or json.load)
    @return: python dict
    """
    with open(fpath) as f: return load(f)

def load_yaml(dpath, reference):
    """
    Load YAML dataset by name.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @return: python dict
    """
    return load_file(os.path.join(dpath, reference + ".yaml"), yaml.load)

def load_json(dpath, reference):
    """
    Load JSON dataset by name.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @return: python dict
    """
    return load_file(dpath, reference + ".json", json.load)

def load(dpath, reference, dtype="YAML"):
    """
    Load dataset by name. The dataset file may be either YAML or JSON.
    @param dpath:     path to the directory where the data sit.
    @param reference: name of the dataset
    @param dtype:     type of the dataset file (YAML/JSON)
    @return: python dict
    """

    if dtype.lower() == "yaml": return load_yaml(dpath, reference)
    elif dtype.lower() == "json": return load_json(dpath, reference)
    else: raise ValueError("datasets of type " + dtype + " unknown / unimplemented")




