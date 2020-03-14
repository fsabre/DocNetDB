"""This module defines some examples of Vertex subclassing."""

from datetime import datetime
from typing import Any, Dict

from docnetdb.vertex import Vertex


class VertexWithDataValidation(Vertex):
    "A special Vertex that allow only integers as element values." ""

    def __setitem__(self, name: str, value: Any) -> Any:
        """Override the __setitem__ method to allow only integers."""

        if not isinstance(value, int):
            raise TypeError(f"{value} is not an integer")

        # Call the classic Vertex __setitem__ method
        super().__setitem__(name, value)


class VertexWithProcessOnInsertion(Vertex):
    """A special Vertex that add an extra field when inserted."""

    def on_insert(self) -> None:
        """Override the on_insert method."""
        self["insertion_date"] = datetime.now().isoformat()


class CustomVertex(Vertex):
    """A custom Vertex with additional methods."""

    def custom_function(self) -> str:
        return "It works !"

    @classmethod
    def from_dict(cls, init_dict: Dict) -> "CustomVertex":
        return CustomVertex(init_dict)
