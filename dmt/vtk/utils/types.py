"""utilities for types in Python."""

def check_mapping(key_type, value_type):
    """..."""
    def check(adict):
        if not isinstance(adict, dict):
            raise TypeError("argument 'adict' is not a dict.")

        for key, value in adict.items():
            if not isinstance(key, key_type) and isinstance(value, value_type):
                raise TypeError(
                    "key-value pair {}, {} does not type check against {} {}"\
                    .format(key, value, key_type.__name__, value_type.__name__)
                )
        return
    return check
