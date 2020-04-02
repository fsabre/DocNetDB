"""This module defines a class for edge return."""

from typing import Optional, Tuple

from docnetdb.vertex import Vertex


class Edge:
    """A class used to return edges properly."""

    def __init__(
        self,
        start: Vertex,
        end: Vertex,
        label: str = "",
        has_direction: bool = True,
    ):
        """Init an Edge between two vertices.

        Parameters
        ----------
        start : Vertex
            The Vertex at the start of the edge.
        end : Vertex
            The Vertex at the end of the edge.
        label : str, optional
            A label that defines the edge ("" by default).
        has_direction : bool, optional
            Whether the edge is oriented or not. If False, the order of
            ``start`` and ``end`` has little importance, and ``start`` is set
            to have the lowest place regardless of the order of the
            parameters (True by default).

        The ``anchor``, ``other`` and ``direction`` attributes are None
        until and anchor is given with the ``change_anchor`` method.
        """
        if has_direction is True:
            self.start = start
            self.end = end
        else:
            # If the Edge has no direction, the start and end vertices are
            # sorted by place for consistant use.
            self.start, self.end = sorted((start, end), key=lambda v: v.place)
        self.label = label
        self.has_direction = has_direction

        self.anchor: Optional[Vertex] = None
        self.other: Optional[Vertex] = None
        self.direction: Optional[str] = None

    @classmethod
    def from_anchor(
        cls,
        anchor: Vertex,
        other: Vertex,
        label: str = "",
        direction: str = "out",
    ) -> "Edge":
        """Create an Edge between two vertices using an anchor.

        This is useful to have a better representation of the direction of
        the edge.

        Parameters
        ----------
        anchor : Vertex
            The anchor Vertex of the edge. The direction will be given in
            regard of this Vertex.
        other : Vertex
            The other Vertex that constitute the other end of the edge.
        label : str, optional
            A label that defines the edge ("" by default).
        direction : {"out", "in", "none"}, optional
            The direction of the edge according to the anchor point. "none" if
            the edge has no direction ("out" by default).

        Returns
        -------
        Edge
            The freshly-created edge.

        Raises
        ------
        ValueError
            If ``direction`` is neither 'out', 'in' nor 'none'.
        """
        has_direction = direction != "none"

        if has_direction is True:
            if direction == "out":
                start = anchor
                end = other
            elif direction == "in":
                start = other
                end = anchor
            else:
                raise ValueError("Direction is either 'in', 'out' or 'none'")
        else:
            # No need to sort here, the __init__ do it already.
            start = anchor
            end = other

        edge = Edge(start, end, label=label, has_direction=has_direction)

        edge.anchor = anchor
        edge.other = other
        edge.direction = direction

        return edge

    @classmethod
    def from_pack(cls, pack: Tuple[int, int, str, bool], db) -> "Edge":
        """Create an Edge between two vertices using a pack of 4 values.

        Parameters
        ----------
        pack : Tuple[int, int, str, bool]
            The pack of 4 values (start_place, end_place, label,
            has_direction) used for storage.
        db : DocNetDB
            The database used to associate places to vertices.

        Returns
        -------
        Edge:
            The freshly-created edge.
        """
        start_place, end_place, label, has_direction = pack
        start = db[start_place]
        end = db[end_place]
        return Edge(start, end, label, has_direction)

    def change_anchor(self, anchor: Vertex) -> None:
        """Change the anchor vertex, thus the perspective of the edge.

        The ``anchor``, ``other`` and ``direction`` attributes are
        recalculated.

        Parameters
        ----------
        anchor : Vertex
            The new anchor vertex of the edge.

        Raises
        ------
        ValueError
            If the ``anchor`` vertex doesn't belong to the edge.
        """
        if anchor is not self.start and anchor is not self.end:
            raise ValueError("The given anchor doesn't belong to the edge")

        self.anchor = anchor
        if self.has_direction is False:
            self.other = self.end if self.anchor is self.start else self.start
            self.direction = "none"
        else:
            if self.start is self.anchor:
                self.other = self.end
                self.direction = "out"
            else:
                self.other = self.start
                self.direction = "in"

    def __eq__(self, other) -> bool:
        """Override the __eq__ method."""
        return (
            self.start is other.start
            and self.end is other.end
            and self.label == other.label
            and self.has_direction is other.has_direction
        )

    def pack(self):
        """Return a 4-tuple used for storage."""
        return (
            self.start.place,
            self.end.place,
            self.label,
            self.has_direction,
        )
