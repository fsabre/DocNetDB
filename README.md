# DocNetDB

A pure Python document and graph database engine

**Breaking changes are expected during beta.**

# Features

- Create vertices
- Add elements in them like in a dict
- Link them with edges (as an oriented graph or not)
- Save the database as JSON

Strengths :

- The use is simple
- All is stored in one readable and editable file (in JSON format)
- The Vertex class is subclassable, so you can make custom vertices
- Directed and non-directed edges can cohabit in the same graph

Weaknesses :

- Due to its design, not fast as light
- All the data is loaded in memory
- Elements must be JSON-serializable

# Installation

Just run :

```bash
python3 -m pip --user install docnetdb
```

Or if you use a virtual environment, which is way better :

```bash
pip install docnetdb
```

# Usage

## Creating a DocNetDB object

It's the database object. Give it the path to the file which will be read (if existing) of created (if not).

```python3
from docnetdb import DocNetDB
import pathlib

# You can use a string...
database = DocNetDB("subfolder/file.ext")

# ...or a Path.
database = DocNetDB(pathlib.Path(".") / "subfolder" / "file.ext")
```

## Creating vertices

A Vertex is a dict-like object that contains elements. These should be JSON-serializable as the DocNetDB is written in the JSON format.

```python3
from docnetdb import Vertex

# You can create an empty Vertex...
rush_hour = Vertex()
# ...and assign elements to it like items in a dict.
rush_hour["name"] = "Rush Hour"
rush_hour["length"] = 5.25
rush_hour["url"] = "https://www.youtube.com/watch?v=OXBcBugpHZg"

# Or you can provide directly a dict with initial data.
initial_data = dict(
    name="Nyakuza Manholes",
    length=6.62,
    url="https://www.youtube.com/watch?v=GDxS8oK6hCc"
)
manholes = Vertex.from_dict(initial_data)
```

## Insert vertices in the database

Vertices are not inserted in the database by default.

```python3
# You can easily check if the Vertex is inserted in a database.
rush_hour.is_inserted # Returns False

# And also check if a DocNetDB object contains a Vertex.
rush_hour in database # Returns False
```

Every Vertex in a database has a place (equivalent to an ID), that starts at 1. A Vertex that is not inserted have a place equal to 0.

```Python3
# To insert a Vertex, just run :
database.insert(rush_hour) # Returns the place (1 in this case)

# You can verify it with :
rush_hour.is_inserted # Returns True
rush_hour.place # Returns 1
rush_hour in database # Returns True

# Let's add our second Vertex.
database.insert(manholes) # Returns the place (2 in this case)

# You can access a Vertex from its place in the DocNetDB with item style.
database[1] is rush_hour # Returns True
database[2] is manholes # Returns True
```

The object is the same, so its possible to work directly with the named variables, and modify the content of the DocNetDB as well.

## Save the database to the file

If the file didn't exist, this command creates it.

```python3
database.save()
```

## Use the DocNetDB

You can search for vertices in a DocNetDB.

```python3
# Get the vertices that have a length superior to 6 minutes
def custom_gate(vertex):
    return vertex["length"] > 6

found = database.search(custom_gate) # Returns a generator
```

It doesn't matter if a vertex doesn't have a "length" element, as the KeyError is automatically captured.

You can remove vertices from the DocNetDB.

```python3
# Delete the filtered vertices (just "manholes" in this case)
for vertex in list(found):
    database.remove(vertex)

# "manholes" still exists, it was just detached from the database.
manholes["name"] # Returns "Nyakuza Manholes"
manholes.is_inserted # Returns False
```

And others :

```python3
len(database) # Return the number of inserted vertices

database.all() # Return a iterable of all inserted vertices
```

## Add edges between the vertices

```python3
# Let me create a Vertex for the demo
hat = Vertex.from_dict({"game":"A Hat In Time"})
database.insert(hat)

from docnetdb import Edge
edge = Edge(hat, rush_hour, "ost", True)
```

The parameters of the Edge init are the following :

- start : the first Vertex of the edge
- end : the last vertex of the edge
- label : a label for the edge ("" by default)
- has_direction : whether the edge has a direction between the vertices or not (True by default)

```python3
# Let's insert this edge in the database
database.make_edge(edge)
```

## Specify an anchor for an edge

This specificity of DocNetDB to have both directed and non-directed edges has led me to implement a feature, that I called the edges anchors. This is just a way to see the edge from a different point of view. Let's see the example of our "OST" edge from the "A Hat In Time" vertex to the "Rush Hour" vertex.

```python3
edge.start # Returns the 'hat' vertex
edge.end # Returns the 'rush_hour' vertex

# Then, let's anchor the 'hat' vertex in our edge
edge.change_anchor(hat)
edge.anchor # Returns the 'hat' vertex
edge.other # Returns the 'rush_hour' vertex
edge.direction # Returns 'out'

# Let's specify another anchor
edge.change_anchor(rush_hour)
edge.anchor # Returns the 'rush_hour' vertex
edge.other # Returns the 'hat' vertex
edge.direction # Returns 'in'
```

This is very handy, especially when searching for edges, as we'll see in the next part.

## Search for edges and delete them

The `search_edge` method of a DocNetDB class is very handy. It can search for edges connected to a vertex, and filter it by the other end of the edge, it's label and/or it's direction. You should see it's documentation for more information.

Here, we'll search for all the vertices connected to our 'Rush Hour' vertex.

```python3
found = database.search_edge(rush_hour)

# This is the equivalent of this line
found = database.search_edge(rush_hour, v2=None, label=None, direction="all")

# Like all the search functions, the returned object is a generator.
edges = list(found)

# The returned edges have an anchor, which is the first vertex of the search.
edges[0].anchor # Returns the "rush_hour" vertex
edges[0].other # Returns the "hat" vertex
edges[0].direction # Returns "in"

# Let's delete the first edge (and the only in this case)
database.remove_edge(edges[0])
```

# Subclassing the Vertex class

You can subclass it, and that is something I haven't found in other libraries (I guess).
Thus you can define new methods, process on insertion or conditions when adding/modifying an element.
Some examples are given in the `vertex_examples.py` file.

Let's make a Vertex that add automatically the datetime of creation and the datetime of insertion in the DocNetDB.

```python3
import datetime
from docnetdb import Vertex

class DatedVertex(Vertex):
    """A Vertex that keeps track of the time."""
    
    def __init__(self, initial_dict):
        """Override the __init__ method."""
        
        # Let's create the Vertex first by calling the Vertex __init__.
        super().__init__(initial_dict)
        
        # Let's then add the creation date.
        # We use the ISO format as the value has to be JSON-serializable.
        if "creation_date" not in self:
            self["creation_date"] = datetime.datetime.now().isoformat()
    
    def on_insert(self):
        """Override the on_insert method."""
        
        self["insertion_date"] = datetime.datetime.now().isoformat()

    @classmethod
    def from_dict(cls, dct):
        """Override the from_dict method."""
        
        # Here's the thing.
        # If we don't do that, the next time the file will be loaded by a DocNetDB,
        # the data is going to be encapsulated in Vertex objects.
        # So we add this method to indicate to the database how to load th data.
        
        return DatedVertex(dct)
```

Here, the `from_dict` method is not that useful : we could work with Vertex objects as well when loading the file, as the `DatedVertex` class is only useful before and while inserting vertices in the DocNetDB.
But if we want to add custom methods, like one which could calculate the time between the creation and the insertion of the `DatedVertex`, then we would want the database to load the data in this specific class.

We can provide the function like this.

```python3
database = DocNetDB("db.db", vertex_creation_callable=DatedVertex.from_dict)
```

# Documentation

I've not exported it yet, but I try to give proper docstrings to my code, so check them out if you want.

