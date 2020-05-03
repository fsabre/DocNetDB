"""This module defines some exceptions."""


class VertexInsertionException(Exception):
    """Raised when the insertion state of a Vertex is wrong.

    This exception happens when the insertion state of the Vertex is wrong
    for the current operation.
    Depending of the situations, it may be inserted, non-inserted or inserted
    in another database.
    """


class VertexNotReadyException(Exception):
    """Raised when the Vertex is_ready_for_insertion method returns False."""
