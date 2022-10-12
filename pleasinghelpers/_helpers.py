"""Contains the helper classes and methods used throughout the project."""


class MoneyInputDictionary:
    """Keeps track of all money input classes."""

    _i = 0
    items = {}

    @classmethod
    def generate_id(cls):
        """Return a unique ID for each date-picker input class."""
        cls._i += 1
        return "dp_%s" % cls._i
