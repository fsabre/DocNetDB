"""This module define the Vertex class."""


from typing import Any, Dict, Optional


class Vertex:
    """This is a Vertex that is stored in a DocNetDB."""

    def __init__(self, init_dict: Optional[Dict[str, Any]] = None) -> None:
        """Init a Vertex. An optional dict may be used."""

        # The default place is 0, which means the Vertex is not yet added to
        # a DocNetDB.

        self.place = 0

        # All the elements (the fields of the Vertex) are strings. The value
        # can be anything.

        self._elements: Dict[str, Any]
        self._elements = dict()
        if init_dict is not None:
            self._elements.update(init_dict)

    def __repr__(self) -> str:
        """Override the __repr__ method."""
        return f"<Vertex {self._elements}>"

    def __getitem__(self, key):
        """Access the elements by name."""
        return self._elements[key]

    def __setitem__(self, key, value) -> None:
        """Modify the elements by name."""
        self._elements[key] = value

    def __delitem__(self, key) -> None:
        """Delete the elements by name."""
        del self._elements[key]

    @classmethod
    def from_dict(cls, dict_vertex: Dict[str, Any]) -> "Vertex":
        """Make a Vertex from a dict.
        This method is called by the DocNetDB class when loading a file."""

        # The elements are given to the constructor to make the Vertex.

        vertex = Vertex(dict_vertex)
        return vertex

    def to_dict(self) -> Dict:
        """Duplicate the Vertex to a dict.
        This mathod is called by the DocNetDB class when saving to a file."""

        # A copy is return to avoid the risk of modifying the vertex by
        # mistake.

        return self._elements.copy()

    def on_insert(self) -> None:
        """Callback function to do additionnal process when inserting the
        Vertex.
        Can be overriden when subclassing the Vertex class."""
