"""This module defines a class for edge return."""

from typing import Optional, Tuple

from docnetdb.exceptions import VertexInsertionException
from docnetdb.vertex import Vertex


class Edge:
    """An Edge is an object that links two vertices in a DocNetDB."""

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
            The inserted Vertex at the start of the edge.
        end : Vertex
            The inserted Vertex at the end of the edge.
        label : str, optional
            A label that defines the edge ("" by default).
        has_direction : bool, optional
            Whether the edge is oriented or not. If False, the order of
            ``start`` and ``end`` has little importance, and ``start`` is set
            to have the lowest place regardless of the order of the
            parameters (True by default).

        Raises
        ------
        VertexInsertionException
            If ``start`` or ``end`` are not inserted vertices.

        The ``anchor``, ``other`` and ``direction`` attributes are None
        until and anchor is given with the ``change_anchor`` method.
        """
        if not start.is_inserted or not end.is_inserted:
            raise VertexInsertionException(
                "Both vertices must be inserted to make an Edge"
            )

        if has_direction is True:
            self._start = start
            self._end = end
        else:
            # If the Edge has no direction, the start and end vertices are
            # sorted by place for consistant use.
            self._start, self._end = sorted(
                (start, end), key=lambda v: v.place
            )
        self._label = label
        self._has_direction = has_direction

        self._anchor: Optional[Vertex] = None
        self._other: Optional[Vertex] = None
        self._direction: Optional[str] = None

        self.is_inserted = False

    # FACTORIES

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
        VertexInsertionException
            If ``anchor`` or ``other`` are not inserted vertices.
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

        edge._anchor = anchor
        edge._other = other
        edge._direction = direction

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

    # CHECK METHODS

    def has_vertex(self, vertex) -> bool:
        """Return whether the given Vertex constitutes one end of the Edge.

        Parameters
        ----------
        vertex : Vertex
            The given Vertex

        Returns
        -------
        bool
            Whether the given vertex constitutes one end of the Edge.
        """
        return self._start is vertex or self._end is vertex

    # ANCHOR RELATED METHODS

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
        if not self.has_vertex(anchor):
            raise ValueError("The given anchor doesn't belong to the edge")

        self._anchor = anchor
        if self._has_direction is False:
            self._other = (
                self._end if self._anchor is self._start else self._start
            )
            self._direction = "none"
        else:
            if self._start is self._anchor:
                self._other = self._end
                self._direction = "out"
            else:
                self._other = self._start
                self._direction = "in"

    # SPECIAL METHODS

    def __repr__(self) -> str:
        """Override the __repr__ method."""
        if self._has_direction:
            return (
                f"<Edge: from {self._start} to {self._end} "
                f"with label '{self._label}'>"
            )
        return (
            f"<Edge: between {self._start} and {self._end} "
            f"with label '{self._label}'>"
        )

    def __eq__(self, other) -> bool:
        """Override the __eq__ method."""
        return (
            self._start is other._start
            and self._end is other._end
            and self._label == other._label
            and self._has_direction is other._has_direction
        )

    # EXPORT METHODS

    def pack(self) -> Tuple[int, int, str, bool]:
        """Return a 4-tuple used for storage."""
        return (
            self.start.place,
            self.end.place,
            self.label,
            self.has_direction,
        )

    # CALLBACK METHODS

    def on_insert(self) -> None:
        """Do additional process when the Edge is inserted in a database.

        This callback method can be overriden when subclassing the Edge
        class. It is called by the DocNetDB object when inserting this
        Edge.
        """

    # PROPERTIES

    @property
    def start(self) -> Vertex:
        """Read-only property for the start attribute."""
        return self._start

    @property
    def end(self) -> Vertex:
        """Read-only property for the end attribute."""
        return self._end

    @property
    def label(self) -> str:
        """Read-only property for the label attribute."""
        return self._label

    @property
    def has_direction(self) -> bool:
        """Read-only property for the has_direction attribute."""
        return self._has_direction

    @property
    def anchor(self) -> Optional[Vertex]:
        """Read-only property for the anchor attribute."""
        return self._anchor

    @property
    def other(self) -> Optional[Vertex]:
        """Read-only property for the other attribute."""
        return self._other

    @property
    def direction(self) -> Optional[str]:
        """Read-only property for the direction attribute."""
        return self._direction
