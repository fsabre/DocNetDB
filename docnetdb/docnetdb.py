"""This module define the DocNetDB class."""


import json
import pathlib
from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple, Union

from docnetdb.edge import Edge
from docnetdb.exceptions import VertexInsertionException
from docnetdb.vertex import Vertex


class DocNetDB:
    """A database class which can store Vertex objects."""

    def __init__(
        self,
        path: Union[str, pathlib.Path],
        vertex_creation_callable: Callable[..., Vertex] = None,
    ) -> None:
        """Init a DocNetDB."""

        # The path we will use is a pathlib.Path.
        # It will be converted from a string if needed.

        if isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        else:
            raise TypeError("path must be a str or a pathlib.Path")

        # All the vertices will go in a dictionary.
        # The index will be the place (an id if you prefer).
        # This place is repeated in the vertex object.

        self._vertices: Dict[int, Vertex]
        self._vertices = dict()

        # All the edges will go in a list with the format
        # (start_place, end_place, edge_link, has_direction)
        # It could have been a Set but it's sont JSON serializable.

        self._edges: List[Tuple[int, int, str, bool]]
        self._edges = list()

        # This variable stores the place of the next vertex, to speed up the
        # next insertion.

        self._next_place = 1

        # To allow Vertex inheritance, we must allow to specify how to create
        # the Vertxt subclasses when the database loads in memory.
        # The make_vertex() function is made for that : the user can specify a
        # custom function if needed.

        if vertex_creation_callable is None:
            self.make_vertex = Vertex.from_dict
        else:
            self.make_vertex = vertex_creation_callable

        # The file database is automaticcaly loaded on instantiation.

        self.load()

    def __repr__(self) -> str:
        """Override the __repr__ method."""

        return f"<DocNetDB {self.path.absolute()}>"

    def __getitem__(self, index):
        """Access vertices from an index."""

        if isinstance(index, int):
            return self._vertices[index]
        raise TypeError("index must be an integer")

    def load(self) -> None:
        """Read the file and load it in memory."""

        try:
            # Read the file and pop the next place
            with open(self.path) as file_:
                dict_data = json.load(file_)
                # The _next_value is extracted from the dict.
                self._next_place = dict_data.pop("_next_place")
                self._edges = dict_data.pop("_edges")

        # If the file can't be found
        except FileNotFoundError:
            dict_data = dict()

        # Then, each Vertex is created in memory and indexed in the
        # _vertices dictionary.
        # Little joke there, it seems that the keys in JSON are always
        # strings. So we have to convert them.

        for place_str, dict_vertex in dict_data.items():

            # We use the custom function to make the Vertices
            vertex = self.make_vertex(dict_vertex)

            vertex.place = int(place_str)
            self._vertices[vertex.place] = vertex

    def save(self) -> None:
        """Save the database in memory to the file."""

        # A new dictionary is created.

        dict_data: Dict[Any, Any]
        dict_data = dict()

        # We fill it with all the vertices converted in a dict, labeled with
        # a place.

        for place, vertex in self._vertices.items():
            dict_data[place] = vertex.to_dict()

        # Append the _next_place value

        dict_data["_next_place"] = self._next_place

        # Append the _edges

        dict_data["_edges"] = self._edges

        # Then it is time to write the data in a file.
        # Before, we ensure the directory exists.

        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True)

        # Then, we can write the data

        with open(self.path, "w") as file_:
            json.dump(dict_data, file_)

    def _get_next_place(self) -> int:
        """Find a new id, return it, then increment it."""

        # The method increments it automatically, but it can't do it after
        # returning. Thus we use a trick.

        self._next_place += 1
        return self._next_place - 1

    def insert(self, vertex: Vertex) -> int:
        """Insert a Vertex in the database."""

        if not isinstance(vertex, Vertex):
            raise TypeError("The parameter should be a Vertex")

        if vertex.is_inserted:
            raise VertexInsertionException("This vertex is already inserted")

        new_place = self._get_next_place()

        # The place is updated in the Vertex object (it was at 0 by default).

        vertex.place = new_place

        # Call the on_insert callback function

        vertex.on_insert()

        # Add the vertex in the _vertices dictionary

        self._vertices[new_place] = vertex

        return new_place

    def remove(self, vertex: Vertex) -> int:
        """Remove a Vertex from the database."""

        if not isinstance(vertex, Vertex):
            raise TypeError("The parameter should be a Vertex")

        if not vertex.is_inserted:
            raise VertexInsertionException("This vertex wasn't inserted")

        try:
            self._vertices.pop(vertex.place)
            # Save the old place for return
            old_place = vertex.place
            # Reset the place of the vertex
            vertex.place = 0
            return old_place

        except KeyError:
            raise ValueError("The vertex couldn't be found")

    def all(self) -> Iterable[Vertex]:
        """Iterate on all the vertices."""
        return self._vertices.values()

    def __len__(self) -> int:
        """Return the number of inserted vertices."""
        return len(self._vertices)

    def __contains__(self, vertex: Vertex) -> bool:
        """Return whether the Vertex is inserted in the DocNetDB."""
        try:
            return self[vertex.place] is vertex
        except KeyError:
            return False

    def search(self, gate_func: Callable[[Vertex], bool]) -> Iterator[Vertex]:
        """Return a generator of the vertices that match the filter
        function."""

        for vertex in self.all():
            try:
                if gate_func(vertex) is True:
                    yield vertex
            except KeyError:
                pass

    def make_edge(
        self,
        first: Vertex,
        last: Vertex,
        name: str = "",
        has_direction: bool = True,
    ) -> None:
        """Make an edge between two vertices."""

        if first not in self or last not in self:
            raise VertexInsertionException(
                "The two vertices must be inserted to make an edge"
            )

        pack = (first.place, last.place, name, has_direction)
        self._edges.append(pack)

    def search_edge(
        self,
        v1: Vertex,
        v2: Vertex = None,
        name: str = None,
        direction: str = "all",
    ):
        """Return a generator of corresponding edges."""

        # In function of the direction filter, several methods are used.
        # We use filters to keep simple and fast generators.

        if direction == "out":
            selection = filter(
                lambda x: x[0] == v1.place and x[3] is True, self._edges
            )
            if v2 is not None:

                def gate(x):
                    return x[1] == v2.place

                selection = filter(gate, selection)

        elif direction == "in":
            selection = filter(
                lambda x: x[1] == v1.place and x[3] is True, self._edges
            )
            if v2 is not None:

                def gate(x):
                    return x[0] == v2.place

                selection = filter(gate, selection)

        elif direction in ("none", "all"):

            # If the direction is None, the edges with direction are removed
            # from the search.

            if direction == "none":
                selection = filter(lambda x: x[3] is False, self._edges)
            else:
                selection = iter(self._edges)

            def gate(x):
                if x[0] == v1.place:
                    if v2 is None:
                        return True
                    else:
                        return x[1] == v2.place
                elif x[1] == v1.place:
                    if v2 is None:
                        return True
                    else:
                        return x[0] == v2.place
                return False

            selection = filter(gate, selection)

        else:
            raise ValueError("Direction must be 'in', 'out', 'all' or 'none'")

        # Filter with name
        if name is not None:
            selection = filter(lambda x: x[2] == name, selection)

        # Convert the pack to an Edge
        return map(lambda x: Edge.from_pack(x, v1, self), selection)

    def remove_edge(
        self, v1: Vertex, v2: Vertex, name: str, has_direction: bool
    ) -> None:
        """Remove an edge from the database."""

        pack = (v1.place, v2.place, name, has_direction)

        if pack in self._edges:
            self._edges.remove(pack)
        elif has_direction is False:
            other_pack = (v2.place, v1.place, name, has_direction)
            if other_pack in self._edges:
                self._edges.remove(pack)
            else:
                raise ValueError(
                    f"No corresponding edge was found for {other_pack}"
                )
