import pytest

from docnetdb.docnetdb import DocNetDB, Vertex


def test_open_random_path(tmp_path):
    tmp_path = tmp_path / "subfolder" / "db.db"
    DocNetDB(tmp_path)


def test_open_invalid_path():
    with pytest.raises(TypeError):
        DocNetDB(123)


def test_default_load_and_save(tmp_path):
    db = DocNetDB(tmp_path / "db")
    assert db._vertices == {}
    db.save()


def test_index_access(tmp_path):
    db = DocNetDB(tmp_path / "db")
    vertex_list = [Vertex() for i in range(4)]
    for vertex in vertex_list:
        db.insert(vertex)
    assert db[3] == vertex_list[2]


def test_next_place(tmp_path):
    db = DocNetDB(tmp_path / "db")
    assert db._next_place == 0
    db.insert(Vertex())
    assert db._next_place == 2


def test_db_usage(tmp_path):
    db = DocNetDB(tmp_path / "db")
    tracks = dict()
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
        # Check if the place is 0 when the vertex is not inserted
        assert vertex.place == 0
        db.insert(vertex)
        # Check if the place is not 0 when the vertex is inserted
        assert vertex.place != 0
        tracks[vertex.place] = vertex
    # Check if all the tracks are distinct vertices
    assert len(tracks) == len(names)
    assert len(db.all()) == len(names)
    # Remove "Checking In"
    db.remove(tracks[6])
    # Check if the place has been reset correctly
    assert tracks[6].place == 0
    db.save()
    db2 = DocNetDB(tmp_path / "db")
    # Check if the length is the same
    assert len(db2.all()) == len(names) - 1
    # Check if the vertices have the good name
    for vertex in db2.all():
        assert vertex["name"] == tracks[vertex.place]["name"]
    spirit_of_hospitality = Vertex(dict(name="Spirit of Hospitality"))
    db2.insert(spirit_of_hospitality)
    # It should be on the 7th place
    assert spirit_of_hospitality.place == 7


def test_vertex_items():
    v = Vertex()
    v["name"] = "v"
    assert v._elements == {"name": "v"}
    v["version"] = 2
    assert v._elements == {"name": "v", "version": 2}
    v["version"] = 3
    assert v._elements == {"name": "v", "version": 3}
    del v["name"]
    assert v._elements == {"version": 3}


class CustomVertex(Vertex):
    def __setitem__(self, key, value):
        if key == "must_be_true" and value is not True:
            raise ValueError()
        # Call the super method to avoid infinite recursion
        super().__setitem__(key, value)

    def on_insert(self):
        self["auto"] = "Set!"

    def custom_function(self):
        return "It works !"

    @classmethod
    def from_dict(cls, dct):
        return CustomVertex(dct)


def test_vertex_inheritance(tmp_path):
    db = DocNetDB(tmp_path / "db")
    v = CustomVertex(dict(name="v"))
    db.insert(v)
    assert v._elements == {"name": "v", "auto": "Set!"}
    with pytest.raises(ValueError):
        v["must_be_true"] = False
    db.save()
    db2 = DocNetDB(
        tmp_path / "db", custom_make_vertex_func=CustomVertex.from_dict
    )
    assert db2[1].custom_function() == "It works !"


def test_search_in_db(tmp_path):
    db = DocNetDB(tmp_path / "db")
    for a in range(1, 51):
        db.insert(Vertex(dict(text=str(a))))
    db[34]["special_element"] = "WOW !"

    def gate1(v):
        return v["special_element"] == "WOW !"

    def gate2(v):
        return int(v["text"]) > 48

    assert [vertex.place for vertex in db.search(gate1)] == [34]
    assert [vertex.place for vertex in db.search(gate2)] == [49, 50]
