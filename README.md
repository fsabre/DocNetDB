# DocNetDB

A pure Python document and graph database engine

The *graph* part is coming soon.

# Features

Strengths :
- In one readable file
- The Vertex class is subclassable

Weaknesses :
- Due to its design, not fast as light


# Usage

## Creating a DocNetDB object

```python3
from docnetdb import DocNetDB, Vertex

# Use a string
database = DocNetDB("subfolder/file.ext")
# Or a Path
import pathlib
database = DocNetDB(pathlib.Path(".") / "subfolder" / "file.ext")
```

## Creating vertices

```python3
# Element assignment with item style
rush_hour = Vertex()
rush_hour["name"] = "Rush Hour"
rush_hour["length"] = 5.25
rush_hour["url"] = "https://www.youtube.com/watch?v=OXBcBugpHZg"

# Element assignment with initial data dict
initial_data = dict(
    name="Nyakuza Manholes",
    length=6.62,
    url="https://www.youtube.com/watch?v=GDxS8oK6hCc"
)
manholes = Vertex(initial_data)
# Or
manholes = Vertex.from_dict(initial_data)
```

## Insert vertices in the database

```python3
rush_hour.is_inserted() # Returns False
database.insert(rush_hour) # Returns the place (1 in this case)
rush_hour.is_inserted() # Returns True
rush_hour.place # Returns 1

database.insert(manholes) # Returns the place (2 in this case)

# You can still add elements to a Vertex afterwards
rush_hour is database[1] # Returns True
manholes is database[2] # Returns True
```

## Save the database to the file

```python3
database.save()
```

## Access vertices in the database

```python3
# Get the first vertex
database[1]

# Get the vertices that have a length superior to 6 minutes
def custom_gate(vertex):
    return vertex["length"] > 6

gen = database.search(custom_gate) # Returns a generator

# It doesn't matter if a vertex doesn't have a "length" element, as the
# KeyError is automatically captured.

# Delete the filtered vertices (just "manholes" in this case)
for vertex in list(gen):
    database.remove(vertex)

# "manholes" still exists, it was just detached from the database.
manholes["name"] # Returns "Nyakuza Manholes"
manholes.is_inserted() # Returns False
```
