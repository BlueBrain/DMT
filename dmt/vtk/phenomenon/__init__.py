"""A phenomenon is anything that manifests itself,
an observable fact or event. A phenomenon may be described by a system of
information related to matter, energy, or spacetime"""

from dmt.vtk.utils.string_utils import make_name, make_label
from dmt.vtk.utils.logging import Logger, with_logging

@with_logging(Logger.level.STUDY)
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
        description_hash = hash(unique_description)
        label = make_label(name)

        if label not in Phenomenon.__registered_instances:
            cls.__registered_instances[label] = {}
        if description_hash not in cls.__registered_instances[label]:
            cls.__registered_instances[label] = {
                description_hash: super(Phenomenon, cls).__new__(cls) }
        return cls.__registered_instances[label][description_hash]

    def __init__(self, name, description, group=None, *args, **kwargs):
        self.name = name
        self.description = description
        if group:
            self._group = group
        self.__model_registry = [] #models known to measure this phenomenon.
        self.__reference_data_registry = [] #data providing a measurement of this phenomenon.

        super().__init__(*args, **kwargs)

    @property
    def name(self):
        """name of this phenomenon."""
        return make_name(self.__name)

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError('Phenomenon name must be a string!')
        if len(value) == 0:
            raise ValueError('Phenomenon name cannot be empty!')
        self.__name = value
            
    @property
    def group(self):
        """..."""
        try:
            return self._group
        except AttributeError as e:
            self.logger.alert(
                "No 'group' set for {} instance.".format(
                    self.__class__.__name__),
                "Setting it to its label {}".format(
                    self.label) )
            self._group = self.label

        return self.group

    @property
    def title(self):
        """Another (read-only) word for 'name'."""
        return self.name

    @property
    def label(self):
        """label that can be used as a header entry
        (column name in a data-frame)"""
        return make_label(self.name)

    def __hash__(self):
        """All Phenomenon with the same label are equivalent"""
        return hash("{} {}".format(
            self.label, self.description))

    def __eq__(self, other):
        """..."""
        return (self.label == other.label
                and make_name(self.description) == make_name(other.description))
    
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
        """Show me"""
        r = "Phenomenon\n\tname: {}\n\t description: {}\n"\
            .format(self.name, self.description)
        return "{}\tgroup: {}\n".format(r, self.group) if self.group else r

    def register_model(self, model):
        """..."""
        self.__model_registry.append(model)
        return self.__model_registry

    def register_data(self, data):
        """..."""
        self.__reference_data_registry.append(data)
        return self.__reference_data_registry

    @classmethod
    def get_known_phenomena(cls, name=None):
        """Get all known phenomenon with given name."""
        if name is None:
            return [p for dps in Phenomenon.__registered_instances.values()
                    for p in dps.values()]

        label = make_label(name)

        return cls.__registered_instances[label].values()

