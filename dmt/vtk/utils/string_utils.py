"""Some string manipulations"""

def __make_name_like(string, sep, with_caps,
                   with_chars_removed=[',', ':', '&', '#', '/',
                                       '\\', '$', '?', '^', ';', '.']):
    """Make a unique string.
    This is useful for the purposes of updating a repository of strings (
    or objects indexed by string.) where we are interested in the meaning
    of a string and not it's value.
    
    Implementation Notes
    --------------------
    Current implementation is a very simple one.
    Add some NLP stemming, remove punctuations, ..."""
    
    def removed(string):
        if with_chars_removed:
            return ''.join(c for c in string if c not in with_chars_removed)
        return string

    caps = lambda w: (w.capitalize() if with_caps else w)
        
    return sep.join(caps(removed(w))
                    for w in string.lower().strip().split(' ')
                    if len(w) > 0)

def make_name(string):
    """make name from a string"""
    return __make_name_like(string, sep=' ', with_caps=True,
                            with_chars_removed=[',', ':', '&', '#', '/',
                                                '\\', '$', '?', '^', ';'])

def make_label(string):
    """make label from a string"""
    return __make_name_like(string, sep="_", with_caps=False,
                            with_chars_removed=[',', ':', '&', '#', '/',
                                                '\\', '$', '?', '^', ';'])
