class MissingArgument(Exception):
    """Used for raising when a function is missing an argument."""
    ...


class ExtraArgument(Exception):
    """Used for raising when there's an extra argument."""
    ...
