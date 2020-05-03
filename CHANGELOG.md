0.6.1
- Remove the callback methods in the Vertex (subclass the DocNetDB if you want to achieve the same result)
- Add the `Vertex.is_ready_for_insertion()` method
- fix bug on `DocNetDB.load()`  (_next_place was not reset)


0.5.2
- Fix a bug on `Edge.from_anchor()` inheritance

0.5.1
- Rework Vertex and Edge inheritance
- Rename methods
- Reorganize files
- Rework iterator methods
