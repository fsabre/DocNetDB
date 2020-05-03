"""This module defines some examples of Vertex subclassing."""

from typing import Any, Dict

from docnetdb.vertex import Vertex


class VertexWithDataValidation(Vertex):
    """A special Vertex that allow only integers as element values."""

    def __setitem__(self, name: str, value: Any) -> Any:
        """Override the __setitem__ method to allow only integers."""
        if not isinstance(value, int):
            raise TypeError(f"{value} is not an integer")

        # Call the classic Vertex __setitem__ method
        super().__setitem__(name, value)


class VertexWithMandatoryFields(Vertex):
    """A special Vertex that has three mandatory elements."""

    def is_ready_for_insertion(self):
        """Override the is_ready_for_insertion method."""
        mandatory_elements = ("name", "weapon", "semblance")
        for m_elem in mandatory_elements:
            if m_elem not in self.keys():
                return False
        return True


class ListVertex(Vertex):
    """A special Vertex that has an integrated list."""

    def __init__(self, init_dict=None):
        """Override __init__ method to add a empty list."""
        super().__init__(init_dict)
        self.list = []

    @classmethod
    def from_pack(cls, pack: Dict) -> "ListVertex":
        """Override the from_pack method."""
        list_pack = pack.pop("list")

        # Call the parent factory
        vertex = super(ListVertex, cls).from_pack(pack)

        # This is for mypy.
        # I could have done vertex = cast(ListVertex, vertex) but an assertion
        # will help me to debug for the moment.
        assert isinstance(vertex, ListVertex)

        vertex.list = list_pack
        return vertex

    def append(self, value: Any) -> None:
        """Append an item to the list."""
        self.list.append(value)

    def pack(self) -> Dict:
        """Override the pack method."""
        pack = super().pack()
        pack["list"] = self.list
        return pack


class IntListVertex(ListVertex):
    """A special Vertex that has an integrated list of integers."""

    def append(self, value: int) -> None:
        """Append an integer to the list."""
        if isinstance(value, int):
            super().append(value)
        else:
            raise TypeError("Only integers are accepted")

    @classmethod
    def from_pack(cls, pack):
        """Override the from_pack method."""
        # Let's check that the from_pack method from the parent can be called.
        # This is not very useful, but it illustrates how to handle this case.
        list_pack = pack["list"]
        print(list_pack)
        if any([True for item in list_pack if not isinstance(item, int)]):
            raise ValueError("Not all items in the pack are integers")
        return super(IntListVertex, cls).from_pack(pack)
