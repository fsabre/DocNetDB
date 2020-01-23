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


def test_insert_and_save_and_reopen(tmp_path):
    db = DocNetDB(tmp_path / "db")
    v1 = Vertex(dict(name="v1"))
    assert v1.place == 0
    db.insert(v1)
    assert v1.place == 1
    db.save()
    db2 = DocNetDB(tmp_path / "db")
    assert db2[1]._elements == {"name": "v1"}


def test_index_access(tmp_path):
    db = DocNetDB(tmp_path / "db")
    vertex_list = [Vertex()] * 4
    for vertex in vertex_list:
        db.insert(vertex)
    assert db[3] == vertex_list[2]


def test_next_place(tmp_path):
    db = DocNetDB(tmp_path / "db")
    assert db._next_place == 0
    db.insert(Vertex())
    assert db._next_place == 2


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
