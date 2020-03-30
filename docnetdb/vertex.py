"""This module define the Vertex class."""


from typing import Dict, Optional


class Vertex(dict):
    """A Vertex is a dict-like object that is stored in a DocNetDB."""

    def __init__(self, init_dict: Optional[Dict] = None) -> None:
        """Init a Vertex.

        Parameters
        ----------
        init_dict : Dict, optional
            When not None, the Vertex is filled on initialization with the
            content of ``init_dict`` (None by default).
        """
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
        """Show the inserted state of the Vertex.

        Returns
        -------
        bool
            If the Vertex is in a database.
        """
        return self.place != 0

    @classmethod
    def from_dict(cls, init_dict: Dict) -> "Vertex":
        """Create a Vertex from an initial dict.

        Parameters
        ----------
        init_dict : Dict
            The dict that the Vertex will be filled with.

        Returns
        -------
        Vertex
            The freshly-created Vertex.
        """
        return Vertex(init_dict)

    def to_dict(self) -> Dict:
        """Duplicate the Vertex to a dict.

        This mathod is called by the DocNetDB class when saving to a file.

        Returns
        -------
        Dict
            A JSON-serializable copy of the Vertex.
        """
        # A copy is return to avoid the risk of modifying the vertex by
        # mistake.
        return self.copy()

    def on_insert(self) -> None:
        """Do additional process when the Vertex is inserted in a database.

        This callback method can be overriden when subclassing the Vertex
        class. It is called by the DocNetDB object when inserting this
        Vertex.
        """
