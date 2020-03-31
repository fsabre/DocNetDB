"""This module defines some tests on the DocNetDB class."""

from collections import Generator

import pytest

from docnetdb import DocNetDB, Edge, Vertex, VertexInsertionException

# TESTS ON INIT


def test_docnetdb_init_parameters(tmp_path):
    """Test if the DocNetDB init works with a path or a string."""
    # DocNetDB init should work with a path.
    DocNetDB(tmp_path / "db1.db")
    # DocNetDB init should work with a str.
    DocNetDB(str(tmp_path.absolute()) + "/db2.db")
    # DocNetDB init shouldn't work with another type.
    with pytest.raises(TypeError):
        DocNetDB(123)


def test_docnetdb_init_file_creation(tmp_path):
    """Test if the DocNetDB init doesn't create a file straight away."""
    path = tmp_path / "dont_create_me.db"
    DocNetDB(path)
    assert path.exists() is False


def test_docnetdb_init_with_subfolder(tmp_path):
    """Test if the DocNetDB init works with non existing subfolders."""
    DocNetDB(tmp_path / "subfolder" / "db.db")


def test_docnetdb_init_with_used_file(tmp_path):
    """Test if the DocNetDB init works even if file is already used."""
    path = tmp_path / "db.db"
    DocNetDB(path)
    DocNetDB(path)


def test_docnetdb_init_with_no_vertices(tmp_path):
    """Test if the DocNetDB init doesn't create vertices if there's no file."""
    path = tmp_path / "not_existing_file.db"
    db = DocNetDB(path)
    assert len(db) == 0


# TESTS ON LOAD / SAVE


def test_docnetdb_save_file_creation(tmp_path):
    """Test if the DocNetDB save creates a file."""
    path = tmp_path / "file.db"
    db = DocNetDB(path)
    db.save()
    assert path.exists() is True


def test_docnetdb_save_with_subfolder(tmp_path):
    """Test if the DocNetDB save creates non-existing subfolders."""
    path = tmp_path / "subfolder" / "db.db"
    db = DocNetDB(path)
    db.save()
    assert path.exists() is True


def test_docnetdb_load(tmp_path):
    """Test if the DocNetDB load restores all the vertices in the object."""
    path = tmp_path / "db.db"
    db1 = DocNetDB(path)
    music_names = ["Prologue", "First Steps", "Resurrections"]
    for name in music_names:
        db1.insert(Vertex({"name": name}))
    db1.save()

    db2 = DocNetDB(path)
    assert len(db1) == len(db2)
    for vertex, target_name in zip(db2.all(), music_names):
        assert vertex["name"] == target_name


def test_docnetdb_load_place(tmp_path):
    """Test if the DocNetDB load restores the state of used places."""
    path = tmp_path / "db.db"
    db1 = DocNetDB(path)
    vertex1 = Vertex()
    db1.insert(vertex1)
    db1.remove(vertex1)
    db1.save()

    db2 = DocNetDB(path)
    assert db2.insert(Vertex()) == 2


def test_docnetdb_load_no_duplication(tmp_path):
    """Test if calling DocNetDB load two times doesn't duplicate anything.

    Like the vertices or the edges.
    """
    path = tmp_path / "db.db"
    db1 = DocNetDB(path)
    v1, v2 = Vertex(), Vertex()
    db1.insert(v1)
    db1.insert(v2)
    db1.make_edge(v1, v2, "my_edge", True)
    db1.save()

    # The file is loaded into the same database.
    db1.load()

    assert len(db1) == 2
    assert len(list(db1.search_edge(v1))) == 1


# TESTS ON Vertex INSERTION / REMOVAL


def test_docnetdb_insert_incrementation(tmp_path):
    """Test if the DocNetDB insert returns incrementing places."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    assert db.insert(v1) == 1
    assert db.insert(v2) == 2
    assert db.insert(v3) == 3


def test_docnetdb_insert_place_affectation(tmp_path):
    """Test_if the DocNetDB insert assigns the correct place to vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)
    assert v1.place == 1
    assert v2.place == 2
    assert v3.place == 3


def test_docnetdb_insert_double_insertion_error(tmp_path):
    """Test if the DocNetDB insert refuses inserted vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1 = Vertex()
    db.insert(v1)

    with pytest.raises(VertexInsertionException):
        db.insert(v1)


def test_docnetdb_insert_parameter(tmp_path):
    """Test if the DocNetDB insert fails if the parameter is not a Vertex."""
    db = DocNetDB(tmp_path / "db.db")
    with pytest.raises(TypeError):
        db.insert("this is not valid")


def test_docnetdb_insert_always_increments(tmp_path):
    """Test if the DocNetDB insert always uses a new place.

    Even if vertices have been removed, a new place should always be used.
    """
    db = DocNetDB(tmp_path / "db.db")
    vertices = [Vertex() for __ in range(5)]
    for vertex in vertices:
        db.insert(vertex)
    db.remove(vertices[4])
    assert db.insert(vertices[4]) == 6


def test_docnetdb_remove(tmp_path):
    """Test if the DocNetD remove works properly.

    It should remove the vertex from the DocNetDB and return
    the correct place.
    """
    db = DocNetDB(tmp_path / "db.db")
    vertex = Vertex()
    old_place = db.insert(vertex)
    assert db.remove(vertex) == old_place
    assert vertex not in db


def test_docnetdb_remove_place_affectation(tmp_path):
    """Test if the DocNetDB remove resets the place of a Vertex."""
    db = DocNetDB(tmp_path / "db.db")
    vertex = Vertex()
    db.insert(vertex)
    db.remove(vertex)
    assert vertex.is_inserted is False


def test_docnetdb_remove_not_inserted_vertex(tmp_path):
    """Test if the DocNetDB remove refuses not inserted vertices."""
    db = DocNetDB(tmp_path / "db.db")
    vertex = Vertex()
    with pytest.raises(VertexInsertionException):
        db.remove(vertex)


def test_docnetdb_remove_paramater(tmp_path):
    """Test if the DocNetDB remove fails if the parameter is not a Vertex."""
    db = DocNetDB(tmp_path / "db.db")
    with pytest.raises(TypeError):
        db.remove("this is not valid")


# TESTS ON PROPERTIES


def test_docnetdb_contains(tmp_path):
    """Test if the DocNetDB __contains__ method works."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2:  # Let's not insert v3.
        db.insert(vertex)

    assert v1 in db
    assert v2 in db
    assert v3 not in db


def test_docnetdb_len(tmp_path):
    """Test if the DocNetDB __len___returns the number of inserted vertices."""
    db = DocNetDB(tmp_path / "db.db")
    for __ in range(5):
        db.insert(Vertex())

    assert len(db) == 5


# TESTS ON VERTEX ACCESS


def test_docnetdb_getitem(tmp_path):
    """Test if the DocNetDB item-style access returns correct vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    assert db[1] is v1
    assert db[2] is v2
    assert db[3] is v3


def test_docnetdb_getitem_non_integer(tmp_path):
    """Test if the DocNetDB item access fails for an non-integer value."""
    db = DocNetDB(tmp_path / "db.db")
    db.insert(Vertex())

    with pytest.raises(TypeError):
        db["1"]


def test_docnetdb_getitem_not_existing_vertex(tmp_path):
    """Test if the DocNetDB item access fails if the vertex doesn't exist."""
    db = DocNetDB(tmp_path / "db.db")
    db.insert(Vertex())

    with pytest.raises(KeyError):
        db[2]


def test_docnetdb_all(tmp_path):
    """Test if the DocNetDB all returns all inserted vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    assert list(db.all()) == [v1, v2, v3]


# TESTS ON VERTEX SEARCH


def test_docnetdb_search(tmp_path):
    """Test if the DocNetDB search returns the right vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    def find_the_second(vertex):
        return vertex.place == 2

    result = db.search(find_the_second)
    assert list(result) == [v2]


def test_docnetdb_search_return_type(tmp_path):
    """Test if the DocNetDB search returns a generator."""
    db = DocNetDB(tmp_path / "db.db")

    def false_func(x):
        return False

    result = db.search(false_func)
    assert isinstance(result, Generator) is True


def test_docnetdb_search_keyerror_autocatch(tmp_path):
    """Test if the DocNetDB search catches KeyError automatically."""
    db = DocNetDB(tmp_path / "db.db")
    v1 = Vertex({"special_element": "WOW !"})
    v2 = Vertex()
    db.insert(v1)
    db.insert(v2)

    def find_special_element(vertex):
        return vertex["special_element"] == "WOW !"

    assert list(db.search(find_special_element)) == [v1]


# TESTS ON EDGES


def test_docnetdb_make_edge(tmp_path):
    """Test if the DocNetDB make_edge doesn't raise exceptions."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2 = Vertex(), Vertex()

    with pytest.raises(VertexInsertionException):
        db.make_edge(v1, v2, name="", has_direction=False)

    db.insert(v1)
    db.insert(v2)

    db.make_edge(v1, v2, name="", has_direction=False)


def test_docnetdb_search_edge(tmp_path):
    """Test if the DocNetDB search_edge returns the right edges."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    db.make_edge(v1, v2, name="name", has_direction=False)
    db.make_edge(v2, v3, has_direction=True)

    assert list(db.search_edge(v1)) == [
        Edge(asked=v1, other=v2, name="name", direction="none")
    ]
    assert list(db.search_edge(v2)) == [
        Edge(asked=v2, other=v1, name="name", direction="none"),
        Edge(asked=v2, other=v3, name="", direction="out"),
    ]
    assert list(db.search_edge(v3)) == [
        Edge(asked=v3, other=v2, name="", direction="in")
    ]


def test_docnetdb_search_edge_parameters(tmp_path):
    """Test if the DocNetDB search_edge parameters are working."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    db.make_edge(v1, v2, name="name", has_direction=False)
    db.make_edge(v2, v3, has_direction=True)

    assert list(db.search_edge(v2, direction="all")) == [
        Edge(asked=v2, other=v1, name="name", direction="none"),
        Edge(asked=v2, other=v3, name="", direction="out"),
    ]
    assert list(db.search_edge(v2, direction="none")) == [
        Edge(asked=v2, other=v1, name="name", direction="none")
    ]
    assert list(db.search_edge(v2, direction="in")) == []
    assert list(db.search_edge(v2, direction="out")) == [
        Edge(asked=v2, other=v3, name="", direction="out")
    ]

    assert list(db.search_edge(v2, name="name")) == [
        Edge(asked=v2, other=v1, name="name", direction="none")
    ]
    assert list(db.search_edge(v2, name="")) == [
        Edge(asked=v2, other=v3, name="", direction="out")
    ]

    assert list(db.search_edge(v2, name="another_name")) == []

    assert list(db.search_edge(v3, direction="in")) == [
        Edge(asked=v3, other=v2, name="", direction="in")
    ]
    assert list(db.search_edge(v3, direction="out")) == []


def test_docnetdb_remove_edge(tmp_path):
    """Test if the DocNetDB remove_edge removes one corresponding edge.

    And only one.
    """
    db = DocNetDB(tmp_path / "db.db")
    v1, v2, v3 = Vertex(), Vertex(), Vertex()
    for vertex in v1, v2, v3:
        db.insert(vertex)

    db.make_edge(v1, v2, name="name", has_direction=False)
    db.make_edge(v1, v2, name="name", has_direction=False)
    db.make_edge(v2, v3, has_direction=True)

    db.remove_edge(v1, v2, name="name", has_direction=False)
    db.remove_edge(v2, v3, name="", has_direction=True)

    assert list(db.search_edge(v2)) == [
        Edge(asked=v2, other=v1, name="name", direction="none")
    ]
    assert list(db.search_edge(v3)) == []


def test_docnetdb_egde_persistance(tmp_path):
    """Test if the DocNetDB edges are stored on save.

    And properly loaded too.
    """
    db = DocNetDB(tmp_path / "db.db")
    v1, v2 = Vertex(), Vertex()
    db.insert(v1)
    db.insert(v2)
    db.make_edge(v1, v2, name="edge", has_direction=False)
    db.save()
    del db

    db2 = DocNetDB(tmp_path / "db.db")
    v1, v2 = db2[1], db2[2]
    assert list(db2.search_edge(v1)) == [
        Edge(asked=v1, other=v2, name="edge", direction="none")
    ]
