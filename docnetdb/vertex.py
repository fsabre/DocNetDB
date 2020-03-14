"""This module define the Vertex class."""


from typing import Dict, Optional


class Vertex(dict):
    """This is a Vertex that is stored in a DocNetDB."""

    def __init__(self, init_dict: Optional[Dict] = None) -> None:
        """Init a Vertex. An optional dict may be used."""

        # The dict init is called first.
        super().__init__()

        # The default place is 0, which means the Vertex is not yet added to
        # a DocNetDB.
        self.place = 0

        # All the elements (the fields of the Vertex) are strings. The value
        # can be anything.
        if init_dict is not None:
            self.update(**init_dict)

    def __repr__(self) -> str:
        """Override the __repr__ method."""
        place_str = f"{self.place}" if self.is_inserted else ""
        return f"<Vertex ({place_str}) {super().__repr__()}>"

    @property
    def is_inserted(self) -> bool:
        """Return True if the Vertex is in the database."""
        return self.place != 0

    @classmethod
    def from_dict(cls, init_dict: Dict) -> "Vertex":
        """Create a Vertex from an initial dict."""
        return Vertex(init_dict)

    def to_dict(self) -> Dict:
        """Duplicate the Vertex to a dict.
        This mathod is called by the DocNetDB class when saving to a file."""

        # A copy is return to avoid the risk of modifying the vertex by
        # mistake.

        return self.copy()

    def on_insert(self) -> None:
        """Callback function to do additionnal process when inserting the
        Vertex.
        Can be overriden when subclassing the Vertex class."""
