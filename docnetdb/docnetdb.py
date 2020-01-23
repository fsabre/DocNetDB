"""This module define a graph/document databas called DocNetDB."""


import json
import pathlib
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Union


class DocNetDB:
    """This is the database."""

    def __init__(
        self,
        path: Union[str, pathlib.Path],
        custom_make_vertex_func: Callable[..., "Vertex"] = None,
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

        # This variable stores the place of the next vertex, to speed up the
        # next insertion.

        self._next_place = 0

        # To allow Vertex inheritance, we must allow to specify how to create
        # the Vertxt subclasses when the database loads in memory.
        # The make_vertex() function is made for that : the user can specify a
        # custom function if needed.

        if custom_make_vertex_func is None:
            self.make_vertex = Vertex.from_dict
        else:
            self.make_vertex = custom_make_vertex_func

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

        # Ensure the directory and the file exist.

        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True)

        if not self.path.exists():
            with open(self.path, "w") as f:
                f.write("{}")

        # First, the whole dict is loaded.

        with open(self.path) as f:
            dict_data = json.load(f)

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

        dict_data = dict()

        # We fill it with all the vertices converted in a dict.

        for place, vertex in self._vertices.items():
            dict_data[place] = vertex.to_dict()

        # Then it is wrote to a file
        with open(self.path, "w") as f:
            json.dump(dict_data, f)

    def _get_next_place(self) -> int:
        """Find a new id, return it, then increment it."""

        # The _next_place variable has the 0 value on the database
        # instantiation. If needed, it will be set to the greater place
        # plus one.

        if self._next_place == 0:
            keys = self._vertices.keys()
            self._next_place = max(keys) + 1 if len(keys) > 0 else 1

        # The method increments it automatically, but it can't do it after
        # returning. Thus we use a trick.

        self._next_place += 1
        return self._next_place - 1

    def insert(self, vertex: "Vertex") -> None:
        """Insert a Vertex in the database."""

        new_place = self._get_next_place()

        # The place is updated in the Vertex object (it was at 0 by default).

        vertex.place = new_place

        # Call the on_insert callback function

        vertex.on_insert()

        # Add the vertex in the _vertices dictionary

        self._vertices[new_place] = vertex

    def all(self) -> Iterable["Vertex"]:
        """Iterate on all the vertices."""
        return self._vertices.values()

    def search(
        self, gate_func: Callable[["Vertex"], bool]
    ) -> Iterator["Vertex"]:
        """Return a generator of the vertices that match the filter
        function."""

        for vertex in self.all():
            try:
                if gate_func(vertex) is True:
                    yield vertex
            except KeyError:
                pass


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
        """Make a Vertex from a dict for the JSON import."""

        # The elements are given to the constructor to make the Vertex.

        vertex = Vertex(dict_vertex)
        return vertex

    def to_dict(self) -> Dict:
        """Duplicate the Vertex to a dict for the JSON export."""

        # A copy is return to avoid the risk of modifying the vertex by
        # mistake.

        return self._elements.copy()

    def on_insert(self) -> None:
        """Callback function to do additionnal process when inserting the
        Vertex."""
