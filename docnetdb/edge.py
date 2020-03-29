"""This module defines a class for edge return."""

from typing import Tuple

from docnetdb.vertex import Vertex


class Edge:
    """A class used to return edges properly."""

    def __init__(
        self, asked: Vertex, other: Vertex, name: str, direction: str
    ):
        self.asked = asked
        self.other = other
        self.name = name
        self.direction = direction

        self._make_start_and_end()

    def __eq__(self, other) -> bool:
        """Override the __eq__ method."""
        return (
            self.asked is other.asked
            and self.other is other.other
            and self.name == other.name
            and self.direction is other.direction
        )

    def _make_start_and_end(self):
        """Create the self.start and self.end Vertex attributes."""

        if self.direction != "none":
            if self.direction == "in":
                self.start = self.other
                self.end = self.asked
            else:
                self.start = self.asked
                self.end = self.other

    @classmethod
    def from_pack(
        cls, pack: Tuple[int, int, str, bool], asked: Vertex, db
    ) -> "Edge":
        """Create a Edge from a 4-values tuples."""

        edge_asked = asked
        edge_name = pack[2]
        if pack[0] == asked.place:
            edge_other = pack[1]
            edge_direction = "out" if pack[3] else "none"
        else:
            edge_other = pack[0]
            edge_direction = "in" if pack[3] else "none"

        return Edge(edge_asked, db[edge_other], edge_name, edge_direction)