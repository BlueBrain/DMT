"""Collection utils."""

import collections

class Namespace:
    """A namespace!"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Record:
    """A record, like a C-struct"""
    def __init__(self, **kwargs):
        self.__field_names = [k for k, _ in kwargs.items()]
        self.__dict__.update(kwargs)

    @property
    def fields(self):
        return self.__field_names

    def __str__(self):
        """String representation of this Record."""
        return self.__repr__()
                   
    def __repr__(self):
        """Represent self."""
        msg = "Record\n"
        for field in self.__field_names[:-1]:
            msg += "\t{}: {},\n".format(field, getattr(self, field))
        field = self.__field_names[-1]
        msg += "\t{}: {}".format(field, getattr(self, field))
        msg += "\n"
        msg += "\n"
        return msg

class FrozenDict(collections.Mapping):
    """A dictionary that cannot be changed."""

    def __init__(self, *args, **kwargs):
        self._store = dict(*args, **kwargs)

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __getitem__(self, key):
        return self._store[key]

    def __hash__(self):
        """convert to a FrozenSet and hash that!"""
        return hash(frozenset(self._store.items()))

    def __repr__(self):
        """can be represented as a dict!"""
        return "FrozenDict(" + repr(self._store) + ")"

    def updated(self, other_dict):
        """update this dict at values given in other
        Parameters
        ----------
        @other_dict :: Mapping
        """
        new_store = {k: v for k, v in self._store.items()}
        new_store.update(other_dict)
        return FrozenDict(new_store)


