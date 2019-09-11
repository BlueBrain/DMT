"""
Little methods to manipulate strings.
"""

def make_text_like(
        string,
        separator,
        with_capitalized_words,
        with_characters_to_remove=[
            ',', ':', '&', '#', '/',
            '\\', '$', '?', '^', ';', '.']):
    """
    Turn a string into normal text like.
    Keep only ASCII characters, removing the provided list.
    And capitalize...
    """

    def __removed(word):
        return ''.join(c for c in word if c not in with_characters_to_remove)

    def __captialzed(word):
        return word.capitalize() if with_capitalized_words else word

    return separator\
        .join(
            __captialzed(__removed(word))
            for word in string.lower().strip().split(' ')
            if len(word) > 0)


def make_name(string):
    """
    Make name from a string.
    Unlike a label, a name may have spaces.
    """
    return make_text_like(
        string,
        separator=' ',
        with_capitalized_words=True)

def make_label(string):
    """
    Make label from a string.
    A label cannot have any spaces.
    """
    return make_text_like(
        string,
        separator='_',
        with_capitalized_words=False)
    
