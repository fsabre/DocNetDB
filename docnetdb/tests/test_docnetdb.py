from typing import Dict

import pytest

from docnetdb import DocNetDB, Vertex


class TestDocNetDB:
    def test_init(self, tmp_path):
        # With a path
        DocNetDB(tmp_path / "file1")
        # With a string
        DocNetDB(str(tmp_path.absolute()) + "/file2")
        # With a number
        with pytest.raises(TypeError):
            DocNetDB(123)

    def test_load(self, tmp_path):
        # With non existing subfolder
        path1 = tmp_path / "subfolder" / "db.db"
        db1 = DocNetDB(path1)
        assert len(db1.all()) == 0
        # Check that opening an non-saved database is not a problem
        DocNetDB(path1)
        # Check that loading doesn't create a file
        path_to_nothing = tmp_path / "dont_create_me.db"
        DocNetDB(path_to_nothing)
        assert not path_to_nothing.exists()

    def test_save(self, tmp_path):
        # With non existing subfolder
        custom_path = tmp_path / "subfolder" / "db"
        db = DocNetDB(custom_path)
        db.save()
        # Check that saving actually creates a file
        assert custom_path.exists()

    def test_get_next_place(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        assert db._next_place == 1
        assert db._get_next_place() == 1
        assert db._get_next_place() == 2
        assert db._get_next_place() == 3

    def test_insert(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Insert an empty Vertex
        v1 = Vertex()
        assert db.insert(v1) == 1
        assert v1.place == 1
        v2 = Vertex.from_dict({"elem1": "ok", "elem2": 15})
        assert db.insert(v2) == 2
        assert v2.place == 2
        # Insert a second time the same Vertex
        with pytest.raises(ValueError):
            db.insert(v1)

    def test_getattr(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        for i in range(1, 6):
            vertex = Vertex.from_dict({"number": i})
            db.insert(vertex)
            # Check that the reference is shared
            assert db[i] is vertex
        # Access a non integer item
        with pytest.raises(TypeError):
            db["invalid"]

    def test_remove(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Remove an empty Vertex
        v1 = Vertex()
        v1_old_place = db.insert(v1)
        assert db.remove(v1) == v1_old_place
        assert v1.is_inserted() is False
        # Remove a second time the Vertex
        with pytest.raises(ValueError):
            db.remove(v1)

    def test_all(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        vertex_list = [Vertex.from_dict({"number": i}) for i in range(1, 6)]
        for vertex in vertex_list:
            db.insert(vertex)
        assert vertex_list == list(db.all())

    def test_search(self, tmp_path):
        db = DocNetDB(tmp_path / "db")
        # Insert 50 vertices
        for i in range(1, 51):
            db.insert(Vertex.from_dict(dict(text=f"I'm n°{i}")))
        # Set a special element for the 34th vertex
        db[34]["special_element"] = "WOW !"

        def gate1(v):
            return v["special_element"] == "WOW !"

        def gate2(v):
            return int(v["text"][6:]) > 48

        assert [vertex.place for vertex in db.search(gate1)] == [34]
        assert [vertex.place for vertex in db.search(gate2)] == [49, 50]


class TestIntegrationDocNetDB:
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


class TestVertex:
    def test_init(self):
        v1 = Vertex()
        assert v1.place == 0
        assert len(v1._elements) == 0
        v2 = Vertex({"name": None})
        assert v2.place == 0
        assert v2._elements["name"] is None

    def test_from_dict(self):
        initial_data = {"name": "v1", "version": "1"}
        v1 = Vertex.from_dict(initial_data)
        # Check that those are the right values
        assert v1._elements["name"] == "v1"
        assert v1._elements["version"] == "1"
        # Check that there are no others elements
        assert len(v1._elements) == 2
        # Check that the dict has been copied
        assert v1._elements is not initial_data

    def test_items(self):
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

    def test_to_dict(self):
        initial_data = {"name": "v1", "version": "1"}
        v1 = Vertex.from_dict(initial_data)
        exported_data = v1.to_dict()
        # Check that the data is the same
        assert exported_data == initial_data
        # Check that the dict has been copied
        assert exported_data is not v1._elements


class TestIntegrationVertex:
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
