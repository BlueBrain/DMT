"""A phenomenon is anything that manifests itself,
an observable fact or event. A phenomenon may be described by a system of
information related to matter, energy, or spacetime"""

import hashlib

class Phenomenon:
    """Phenomenon is an observable fact or event, that can be measured.

    Development Notes
    -----------------
    We start with a simple version,
    that satisfies a bare-minimum specification.
    In the future we can use Phenomenon to store all known models that provide
    a measurement of given phenomenon."""

    registered_instances = {} #phenomena that have been defined

    @staticmethod
    def make_unique(x):
        """Make a unique string.
        This is useful for the purposes of updating a repository of strings (
        or objects indexed by string.) where we are interested in the meaning
        of a string and not it's value.

        Implementation Notes
        --------------------
        Current implementation is a very simple one.
        Add some NLP stemming, remove punctuations, ..."""

        x = x.lower()
        chars_to_remove = [',', ':', '&', '#', '/',
                           '\\', '$', '?', '^', ';', '.']
        for c in chars_to_remove:
            x = x.replace(c, ' ')

        return ' '.join(w for w in x.strip().split(' ') if len(w) > 0)

    def __new__(cls, name, description):
        unique_description = Phenomenon.make_unique(description).encode()
        description_hash = hashlib.sha1(unique_description).hexdigest()
        label = Phenomenon.make_label(name)

        if label not in Phenomenon.registered_instances:
            cls.registered_instances[label] = {}
        if description_hash not in cls.registered_instances[label]:
            cls.registered_instances[label] = {
                description_hash: super(Phenomenon, cls).__new__(cls)
            }
        return cls.registered_instances[label][description_hash]

    def __init__(self, name, description):
        self.name = name
        self.description = description
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
            return [p for dps in Phenomenon.registered_instances.values()
                    for p in dps.values()]

        label = Phenomenon.make_label(name)

        return cls.registered_instances[label].values()

