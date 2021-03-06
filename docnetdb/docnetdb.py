"""This module define the DocNetDB class."""


import json
import pathlib
from typing import Any, Callable, Dict, Iterator, List, Union

from docnetdb.edge import Edge
from docnetdb.exceptions import (
    VertexInsertionException,
    VertexNotReadyException,
)
from docnetdb.vertex import Vertex


class DocNetDB:
    """A database class which can store Vertex objects."""

    def __init__(
        self,
        path: Union[str, pathlib.Path],
        vertex_creation_callable: Callable[..., Vertex] = None,
        edge_creation_callable: Callable[..., Edge] = None,
    ) -> None:
        """Init a DocNetDB.

        Parameters
        ----------
        path : Union[str, pathlib.Path]
            The path to the database file. If it doesn't exists, it will be
            created on the next save.
        vertex_creation_callable : Callable[..., Vertex]
            The callable which is used to create the vertices from a pack.
            Provide it if you are using subclasses of Vertex.
        edge_creation_callable : Callable[..., Edge]
            The callable which is used to create the edges from a pack.
            Provide it if you are using subclasses of Edge.
        """
        # The path we will use is a pathlib.Path.
        # It will be converted from a string if needed.
        if isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        else:
            raise TypeError("path must be a str or a pathlib.Path")

        # To allow Vertex inheritance, we must allow to specify how to create
        # the Vertex subclasses when the database loads in memory.
        # The make_vertex() function is made for that : the user can specify a
        # custom function if needed.
        if vertex_creation_callable is None:
            self.make_vertex = Vertex.from_pack
        else:
            self.make_vertex = vertex_creation_callable

        # Same thing for the edges
        if edge_creation_callable is None:
            self.make_edge = Edge.from_pack
        else:
            self.make_edge = edge_creation_callable

        # Use the default values
        self._use_defaults()

        # The file database is automatically loaded on instantiation.
        self.load()

    def _use_defaults(self) -> None:
        """Reset the database attributes."""
        # All the vertices will go in a dictionary.
        # The index will be the place (an id if you prefer).
        # This place is repeated in the vertex object.
        self._vertices: Dict[int, Vertex]
        self._vertices = dict()

        # All the edges will go in a list.
        # It could have been a Set but it's not JSON serializable.
        self._edges: List[Edge]
        self._edges = list()

        # This variable stores the place of the next vertex, to speed up the
        # next insertion.
        self._next_place = 1

    # SPECIAL METHODS

    def __repr__(self) -> str:
        """Override the __repr__ method."""
        return f"<DocNetDB {self.path.absolute()}>"

    def __getitem__(self, index) -> Vertex:
        """Access vertices from an index.

        Example
        -------
        >>> database[1]
        <Vertex (1) {}>
        """
        if isinstance(index, int):
            return self._vertices[index]
        raise TypeError("index must be an integer")

    def __len__(self) -> int:
        """Return the number of inserted vertices."""
        return len(self._vertices)

    def __contains__(self, vertex: Vertex) -> bool:
        """Return whether the Vertex is inserted in the DocNetDB or not."""
        try:
            return self[vertex.place] is vertex
        except KeyError:
            return False

    def __iter__(self) -> Iterator[Vertex]:
        """Iterate over all the inserted vertices.

        Example
        -------
        >>> for vertex in database:
        >>>     print(v)
        """
        return self.vertices()

    # LOAD AND SAVE METHODS

    def load(self) -> None:
        """Read the file and load it in memory.

        This method is called on instantiation.
        The path is read in the self.path attribute.
        """
        # Reset the attributes
        self._use_defaults()

        # Try to open the file
        try:
            with open(self.path) as file_:
                decoded_json = json.load(file_)
                self._load_packed_data(decoded_json)

        # If the file can't be found
        except FileNotFoundError:
            pass

    def _load_packed_data(self, packed_data: Dict) -> None:
        """Read the packed data and load it in memory.

        Parameters
        ----------
        packed_data : Dict
            The decoded JSON that was in a file.
        """
        # The _next_place value is extracted from the dict.
        self._next_place = packed_data.pop("_next_place")
        # The packed edges are extracted from the dict.
        packed_edges = packed_data.pop("edges")
        # The packed vertices are the remaining data.
        packed_vertices = packed_data

        # Then, each Vertex is created in memory and indexed in the
        # _vertices dictionary.
        # Little joke there, it seems that the keys in JSON are always
        # strings. So we have to convert them.

        for place_str, packed_vertex in packed_vertices.items():

            # We use the custom function to make the Vertices
            vertex = self.make_vertex(packed_vertex)

            vertex.place = int(place_str)
            self._vertices[vertex.place] = vertex

        # Finally, the edges are created as well.

        for pack in packed_edges:

            edge = self.make_edge(pack, self)
            edge.is_inserted = True
            self._edges.append(edge)

    def save(self) -> None:
        """Save the database in memory to a file.

        The path is read in the self.path attribute.
        The file is completely overriden.
        """
        # A new dictionary is created.

        packed_data: Dict[Any, Any]
        packed_data = dict()

        # We fill it with all the vertices converted in a dict, labeled with
        # a place.

        for place, vertex in self._vertices.items():
            packed_data[place] = vertex.pack()

        # Append the _next_place value

        packed_data["_next_place"] = self._next_place

        # Append the edges

        packed_edges = []
        for edge in self._edges:
            packed_edges.append(edge.pack())
        packed_data["edges"] = packed_edges

        # Then it is time to write the data in a file.
        # Before, we ensure the directory exists.

        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True)

        # Then, we can write the data

        with open(self.path, "w") as file_:
            json.dump(packed_data, file_)

    # VERTEX INSERTION AND REMOVAL METHODS

    def _get_next_place(self) -> int:
        """Find a new place, return it, then increment it.

        Return
        ------
        int
            The new place to use.
        """
        # The method increments it automatically, but it can't do it after
        # returning. Thus we use a trick.

        self._next_place += 1
        return self._next_place - 1

    def insert(self, vertex: Vertex) -> int:
        """Insert a Vertex in the database.

        Parameters
        ----------
        vertex : Vertex
            The Vertex to insert in the database.

        Returns
        ------
        int
            The place of the Vertex after the insertion.

        Raises
        ------
        TypeError
            If ``vertex`` is not a Vertex.
        VertexInsertionException
            If the Vertex is already inserted in a database.
        VertexNotReadyException
            If the ``is_ready_for_insertion`` method of the Vertex returns
            False.
        """
        if not isinstance(vertex, Vertex):
            raise TypeError("The parameter should be a Vertex")

        if vertex.is_inserted:
            raise VertexInsertionException("This vertex is already inserted")

        if vertex.is_ready_for_insertion() is False:
            raise VertexNotReadyException()

        new_place = self._get_next_place()

        # The place is updated in the Vertex object (it was at 0 by default).
        vertex.place = new_place
        # Add the vertex in the _vertices dictionary
        self._vertices[new_place] = vertex

        return new_place

    def remove(self, vertex: Vertex) -> int:
        """Remove an inserted Vertex from the database.

        The Vertex still exists afterwards, it's just detached from the
        database.

        Parameters
        ----------
        vertex : Vertex
            The Vertex to remove from the database.

        Returns
        -------
        int
            The place of the Vertex before it's detached.

        Raises:
        -------
        TypeError
            If ``vertex`` is not a Vertex.
        VertexInsertionException
            If the vertex is not already inserted in this database.
        ValueError:
            If the vertex couldn't be found in this database.
        """
        if not isinstance(vertex, Vertex):
            raise TypeError("The parameter should be a Vertex")

        if not vertex.is_inserted:
            raise VertexInsertionException("This vertex wasn't inserted")

        if len(list(self.search_edge(vertex))) != 0:
            raise ValueError("Can't remove: Vertex still connected to others")

        try:

            self._vertices.pop(vertex.place)
            # Save the old place for return
            old_place = vertex.place
            # Reset the place of the vertex
            vertex.place = 0
            return old_place

        except KeyError:
            raise ValueError("The vertex couldn't be found")

    # VERTICES ITERATION METHODS

    def vertices(self) -> Iterator[Vertex]:
        """Return an iterator over all the inserted vertices.

        Returns
        -------
        Iterator[Vertex]
            An iterator over of the vertices in the database.
            Those are not supposed to be sorted by place.
        """
        return iter(self._vertices.values())

    def search(self, gate_func: Callable[[Vertex], bool]) -> Iterator[Vertex]:
        """Return a generator of the vertices that match the filter function.

        The KeyError is catched, so accessing a non-existant element in a
        Vertex doesn't raise an exception.

        Parameters
        ----------
        gate_func : Callabl[Vertex, bool]
            The function which will filter the vertices.

        Returns
        -------
        Iterator[Vertex]
            A generator on all the vertices in the database that have passed
            the ``gate_func`` function.

        Example
        -------
        >>> def more_than_14_years_old(v: Vertex):
        ...     return v["age"] > 14
        >>> accepted = list(database.search(more_than_14_years_old))
        """
        for vertex in self.vertices():
            try:
                if gate_func(vertex) is True:
                    yield vertex
            except KeyError:
                pass

    # EDGE INSERTION AND REMOVAL METHODS

    def insert_edge(self, edge: Edge) -> None:
        """Insert an Edge in the database.

        Parameters
        ----------
        edge : Edge
            The edge to insert.

        Raises
        ------
        VertexInsertionException
            If the two vertices that make the edge are not inserted is this
            database.
        """
        if edge.is_inserted is True:
            raise ValueError("This Edge is already inserted")

        if edge.start not in self or edge.end not in self:
            raise VertexInsertionException(
                "The two vertices are not inserted in this DocNetDB"
            )

        edge.is_inserted = True
        self._edges.append(edge)

    def remove_edge(self, edge: Edge) -> None:
        """Remove an edge from the database.

        The Edge does not need to be the same object (reference) as the one in
        the databse.

        Parameters
        ----------
        edge : Edge
            The edge to remove from the database.

        Raises
        ------
        ValueError
            If no corresponding edge was found in the database.
        """
        if edge in self._edges:
            self._edges.remove(edge)
            edge.is_inserted = False
        else:
            raise ValueError(f"No Edge such as {edge} was found")

    # EDGES ITERATION METHODS

    def edges(self) -> Iterator[Edge]:
        """Return an iterator over all the inserted edges.

        Returns
        -------
        Iterator[Edge]
            An iterator over all the edges in the database.
        """
        return iter(self._edges)

    def search_edge(
        self,
        v1: Vertex,
        v2: Vertex = None,
        label: str = None,
        direction: str = "all",
    ) -> Iterator[Edge]:
        """Return a generator of corresponding edges.

        This method is used to search for edges with differents filters :
        - One or two vertices
        - A label
        - The oriented state of the edge

        Parameters
        ----------
        v1 : Vertex
            The base anchor of the edges. Returned edges all have this Vertex
            in common.
        v2 : Vertex, optional
            The second anchor of the edges. If not None, all returned edges
            will be between ``v1`` and ``v2`` (None by default).
        label : str, optional
            The label of the edge. If not None, all returned edges will have
            this label. If "", all returned edges will have no label (None
            by default).
        direction : str {'out', 'in', 'none', 'all'}, optional
            The direction of the returned edges.
            If "out", all returned edges will be oriented edges from ``v1``
            to ``v2``.
            If "in", all returned edges will be oriented edges from ``v2``
            to ``v1``.
            If "none", all returned edges will be non-oriented edges between
            ``v1`` and ``v2``.
            If "all", no further filtering is done ("all" by default).

        Returns
        -------
        Iterator[Edge]
            A generator on all the corresponding edges.
        """

        def filter_by_v1(edge):
            if edge.has_vertex(v1):
                edge.change_anchor(v1)
                return True
            return False

        selection = filter(filter_by_v1, self._edges)

        if v2 is not None:
            selection = filter(lambda edge: edge.other is v2, selection)

        if direction != "all":
            selection = filter(
                lambda edge: edge.direction == direction, selection
            )

        if label is not None:
            selection = filter(lambda edge: edge.label == label, selection)

        return selection
