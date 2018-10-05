"""A phenomenon is anything that manifests itself,
an observable fact or event. A phenomenon may be described by a system of
information related to matter, energy, or spacetime"""

import hashlib
from dmt.vtk.utils.string_utils import make_name

class Phenomenon:
    """Phenomenon is an observable fact or event, that can be measured.

    Development Notes
    -----------------
    We start with a simple version,
    that satisfies a bare-minimum specification.
    In the future we can use Phenomenon to store all known models that provide
    a measurement of given phenomenon."""

    __registered_instances = {} #phenomena that have been defined

    def __new__(cls, name, description, *args, **kwargs):
        unique_description = make_name(description).encode()
        description_hash = hashlib.sha1(unique_description).hexdigest()
        label = Phenomenon.make_label(name)

        if label not in Phenomenon.__registered_instances:
            cls.__registered_instances[label] = {}
        if description_hash not in cls.__registered_instances[label]:
            cls.__registered_instances[label] = {
                description_hash: super(Phenomenon, cls).__new__(cls)
            }
        return cls.__registered_instances[label][description_hash]

    def __init__(self, name, description, group=None):
        self.name = name
        self.description = description
        self.group = group if group else self.label
        self.__model_registry = [] #models known to measure this phenomenon.
        self.__data_object_registry = [] #data providing a measurement of this phenomenon.

    @property
    def name(self):
        """name of this phenomenon."""
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError('Phenomenon name must be a string!')
        if len(value) == 0:
            raise ValueError('Phenomenon name cannot be empty!')
        self.__name = value
            
    @property
    def title(self):
        """Another (read-only) word for 'name'."""
        return self.name

    @staticmethod
    def make_label(name):
        return  '_'.join(name.lower().split())

    @property
    def label(self):
        """label that can be used as a header entry
        (column name in a data-frame)"""
        return Phenomenon.make_label(self.name)
    
    @property
    def description(self):
        """A wordy description of the phenomenon,
        explaining how it may be evaulated!"""
        return self.__description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError('Phenomenon description must be a string!')
        if len(value) == 0:
            raise ValueError('Phenomenon description cannot be empty!')
        self.__description = value

    def __repr__(self):
        return ("Phenomenon{\n"  +
                "\tname: {}\n\tdescription: {}".format(self.name,
                                                   self.description) +
                "\n}")

    def register(self, measurable_system):
        """Register the measurable system.

        Parameters
        ----------
        @measureable_system :: MeasurableSystem

        a measurable system is either a Model or a DataObject that provides a
        measurement of this phenomenon.

        Status
        ------
        A prototype (20180709) for now.
        A working implementation will depend on how  and where models/data
        are stored."""

        uri = measurable_system.uri
        if isinstance(measurable_system, Model):
            self.__model_registry.append(uri)
            return len(self.__model_registry)
        elif isinstance(measurable_system, DataObject):
            self.__data_object_registry.append(uri)
            return len(self.__data_object_registry)
        else:
            return -1

    @classmethod
    def get_known_phenomena(cls, name=None):
        """Get all known phenomenon with given name."""
        if name is None:
            return [p for dps in Phenomenon.__registered_instances.values()
                    for p in dps.values()]

        label = Phenomenon.make_label(name)

        return cls.__registered_instances[label].values()

