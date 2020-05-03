# DocNetDB

A pure Python document and graph database engine

**Breaking changes are to expect during beta.**

# Summary

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
	- [Create the DocNetDB object](#create-the-docnetdb-object)
	- [Create and insert vertices](#create-and-insert-vertices)
	- [Search and remove vertices](#search-and-remove-vertices)
	- [Save the database](#save-the-database)
	- [Add edges between the vertices](#add-edges-between-the-vertices)
	- [Understand anchors in an edge](#understand-anchors-in-an-edge)
	- [Search and remove edges](#search-and-remove-edges)
	- [Other uses of the DocNetDB](#other-uses-of-the-docnetdb)
- [Subclassing the Vertex class](#subclassing-the-vertex-class)
- [Subclassing the Edge class](#subclassing-the-edge-class)
- [Documentation](#documentation)

# Features

- Create vertices
- Add elements in them (with a dict-like style)
- Link them with edges (as an oriented graph or not)
- Save the database as JSON

Strengths :

- Simple use
- Storage in one readable and editable file (JSON format)
- Subclassable vertices and edges for complex uses
- Directed and non-directed edges can cohabit in the same graph

Weaknesses :

- Not designed to be fast
- Data is entirely loaded in memory
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

## Create the DocNetDB object

It's the database object. Give it the path to the file which will be read (if existing) of created (if not).

```python3
from docnetdb import DocNetDB
import pathlib

# You can use a string...
database = DocNetDB("subfolder/file.ext")

# ...or a Path.
database = DocNetDB(pathlib.Path(".") / "subfolder" / "file.ext")
```


## Create and insert vertices

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
manholes = Vertex(initial_data)
```

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

## Search and remove vertices

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

## Save the database

If the file didn't exist, this command creates it.

```python3
database.save()
```


## Add edges between the vertices

```python3
# Let's create a Vertex for the demo
hat = Vertex({"game":"A Hat In Time"})
database.insert(hat)

from docnetdb import Edge
edge = Edge(start=hat, end=rush_hour, label="ost", has_direction=True)
```


The parameters of the Edge init are the following :

- start : the first Vertex of the edge
- end : the last vertex of the edge
- label : a label for the edge ("" by default)
- has_direction : whether the edge has a direction between the vertices or not (True by default)

```python3
# Let's insert this edge in the database
database.insert_edge(edge)
```

## Understand anchors in an edge

This specificity of DocNetDB to have both directed and non-directed edges has led me to implement a feature, that I called the edges anchors. This is just a way to see the edge from a different point of view. Let's see the example of our "OST" edge from the "A Hat In Time" game vertex to the "Rush Hour" music vertex.

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

## Search and remove edges

The `search_edge` method of a DocNetDB class is very handy. It can search for edges connected to a vertex, and filter it by the other end of the edge, its label and/or its direction. You should see its documentation for more information.

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

## Other uses of the DocNetDB

```python3
# Iterate over all the vertices
for vertex in database.vertices():
	pass

# Or just
for vertex in database:
	pass

# Get the number of inserted vertices
len(database)

# Iterate over all the edges
for edge in database.edges():
	pass
```

# Subclassing the Vertex class

You can subclass it, and that is something I haven't found in other libraries (I guess).
Thus you can define new methods, conditions when adding/modifying an element, etc.
Some examples are given in the `vertex_examples.py` file.

Let's make a Vertex that add automatically the datetime of creation, and must have a name to be inserted.

```python3
import datetime
from docnetdb import Vertex

class DatedVertex(Vertex):
    """A Vertex that keeps track of the time and has a name."""
    
    def __init__(self, initial_dict):
        """Override the __init__ method."""
        
        # Let's create the Vertex first by calling the Vertex __init__.
        super().__init__(initial_dict)
        
        # Let's then add the creation date.
        # We use the ISO format as the value has to be JSON-serializable.
        # Be careful, the init is also called on database load, thus the condition.
        if "creation_date" not in self:
            self["creation_date"] = datetime.datetime.now().isoformat()
    
    def is_ready_for_insertion(self)
        """Override the is_ready_for_insertion method."""
        
        # If this method returns False on insertion, il will be cancelled.
        return "name" in self
```

To pack data in the database file on save, and load correctly, we can override the `from_pack` and `pack` methods.
Some examples are given in the `docnetdb/examples/vertices.py` file.

# Subclassing the Edge class

It's quite the same. Some examples are given in the `docnetdb/examples/edges.py` file.

# Documentation

I've not exported it yet, but I try to give proper docstrings to my code, so check them out if you want.
