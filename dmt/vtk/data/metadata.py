"""Metadata for a validation's reference data in particular,
and any other form of metadata as well."""

class ReferenceMetaData:
    """Metadata for a validation's reference data.
    One dataset should have one metadata associated with it."""

    def __init__(self, short_name, uri, citation, what):
        """
        Parameters
        ----------
        @short_name :: String # short, single-word name, should not be empty
        @uri :: String # universal resource identifier, may be empty
        @citation :: String # in the literature or elsewhere, may be empty
        @what :: String # description of what the data is, may be empty.

        Notes
        ----------
        Please provide a good description about your experimental data in the
        what field."""

        self._short_name = short_name
        self._uri = uri
        self._citation = citation
        self._what = what

    @property
    def short_name(self):
        return self._short_name

    @property
    def uri(self):
        return self._uri

    @property
    def url(self):
        return self._uri

    @property
    def citation(self):
        return self._citation

    @property
    def what(self):
        return self._what

    @property
    def description(self):
        return _description


def reference_metadata(reference):
