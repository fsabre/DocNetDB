from typing import Dict

import pytest

from docnetdb.docnetdb import DocNetDB, Vertex


class TestDocNetDB:
    def test_opening(self, tmp_path):
        # Use a path with a non existing subfolder
        tmp_path = tmp_path / "subfolder" / "db.db"
        DocNetDB(tmp_path)
        # Use a non valid path
        with pytest.raises(TypeError):
            DocNetDB(123)

    def test_default_load_and_save(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Check that no vertices are present
        assert len(db.all()) == 0
        # Check the initial value of _next_place
        assert db._next_place == 1
        # Check that opening an non-saved database is not a problem
        db2 = DocNetDB(tmp_path / "db")
        assert db2._next_place == 1
        # Check that the save doesn't raise exceptions
        db.save()

    def test_insert_and_index_access(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        vertex_list = [Vertex() for i in range(4)]
        # Insert 4 vertices
        for supposed_place, vertex in enumerate(vertex_list):
            supposed_place += 1
            assert db.insert(vertex) == supposed_place
        # Check that the 3rd is the 3rd
        assert db[2 + 1] == vertex_list[2]

    def test_db_usage(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Store vertices here too
        tracks: Dict[int, Vertex]
        tracks = dict()
        # What are those names ? :-)
        names = [
            "Prologue",
            "First Steps",
            "Resurrections",
            "Awake",
            "Postcard from Celeste Montain",
            "Checking In",
        ]
        for name in names:
            vertex = Vertex(dict(name=name))
            # Check that the vertex is not inserted
            assert not vertex.is_inserted()
            db.insert(vertex)
            # Check that the vertex is inserted
            assert vertex.is_inserted()
            tracks[vertex.place] = vertex
        # Check that all the tracks are distinct vertices
        assert len(tracks) == len(names)
        assert len(db.all()) == len(names)
        # Remove "Checking In"
        assert db.remove(tracks[6]) == 6
        # Check that the place has been reset correctly
        assert not tracks[6].is_inserted()
        # Save that
        db.save()

        # Open the file with a second object
        db2 = DocNetDB(tmp_path / "db")
        # Check if the length is the same
        assert len(db2.all()) == len(names) - 1
        # Check if the vertices have the good name
        for vertex in db2.all():
            assert vertex["name"] == tracks[vertex.place]["name"]
        # Insert a new vertex
        spirit_of_hospitality = Vertex(dict(name="Spirit of Hospitality"))
        db2.insert(spirit_of_hospitality)
        # It should be on the 7th place, cause 6 was used for "Checking In".
        assert spirit_of_hospitality.place == 7

    def test_search_in_db(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Insert 50 vertices
        for a in range(1, 51):
            db.insert(Vertex(dict(text=str(a))))
        # Set a special element for the 34th
        db[34]["special_element"] = "WOW !"

        def gate1(v):
            return v["special_element"] == "WOW !"

        def gate2(v):
            return int(v["text"]) > 48

        assert [vertex.place for vertex in db.search(gate1)] == [34]
        assert [vertex.place for vertex in db.search(gate2)] == [49, 50]


class TestVertex:
    def test_vertex_items(self):
        v = Vertex()
        v["name"] = "v"
        assert v["name"] == "v"

        v["version"] = 2
        assert v["name"] == "v"
        assert v["version"] == 2

        v["version"] = 3
        assert v["name"] == "v"
        assert v["version"] == 3

        del v["name"]
        with pytest.raises(KeyError):
            v["name"]
        assert v["version"] == 3

    def test_vertex_inheritance(self, tmp_path):
        class CustomVertex(Vertex):
            def __setitem__(self, key, value):
                if key == "must_be_true" and value is not True:
                    # Can't set "must_be_true" to False"
                    raise ValueError()
                super().__setitem__(key, value)

            def on_insert(self):
                # Automatically add an element on insertion in a DocNetDB
                self["auto"] = "Set!"

            def custom_function(self):
                # Define a custom function that is not in the base Vertex
                return "It works !"

            @classmethod
            def from_dict(cls, dct):
                # This function will be called be the DocNetDB.
                return CustomVertex(dct)

        db = DocNetDB(tmp_path / "db")
        v = CustomVertex(dict(name="v"))
        # Check that the element "name" is defined
        assert v["name"] == "v"
        # Check that the element "auto" is not set yet
        with pytest.raises(KeyError):
            v["auto"]
        db.insert(v)
        # Check that the element "auto" is defined
        assert v["auto"] == "Set!"
        # Check that the __setattr__ override works
        with pytest.raises(ValueError):
            v["must_be_true"] = False
        # Check that the custom function works
        assert v.custom_function() == "It works !"
        db.save()

        # Check that the DocNetDB load CustomVertex and not base Vertex
        db2 = DocNetDB(
            tmp_path / "db", custom_make_vertex_func=CustomVertex.from_dict
        )
        assert db2[1].custom_function() == "It works !"
