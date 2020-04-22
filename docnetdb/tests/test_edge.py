"""This module defines some tests on the Edge class."""


import pytest

from docnetdb import DocNetDB, Edge, Vertex, VertexInsertionException


@pytest.fixture
def db_3_vertices(tmp_path):
    """Make a DocNetDB and insert 3 vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v_list = [Vertex() for __ in range(3)]
    for vertex in v_list:
        db.insert(vertex)
    return (db, *v_list)


# TEST INIT


def test_edge_init(db_3_vertices):
    """Test if the init works and use the correct defaults."""
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v1, v2)
    assert e1.label == ""
    assert e1.has_direction is True
    assert e1.is_inserted is False


def test_edge_init_no_direction(db_3_vertices):
    """Test if vertices are sorted by place when the edge is not oriented."""
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v1, v2, has_direction=False)
    assert e1.start is v1
    assert e1.end is v2
    e2 = Edge(v3, v2, has_direction=False)
    assert e2.start is v2
    assert e2.end is v3


def test_edge_init_vertexinsertionexception():
    """Test if the Edge init with non-inserted vertices raises an exception."""
    v1, v2 = Vertex(), Vertex()
    with pytest.raises(VertexInsertionException):
        edge = Edge(v1, v2)
        del edge


# TEST FACTORIES


def test_edge_from_anchor(db_3_vertices):
    """Test if the from_anchor method works works properly."""
    db, v1, v2, v3 = db_3_vertices

    # Test if the defaults are the same as in the __init__.
    e1 = Edge.from_anchor(v1, v2)
    assert e1 == Edge(v1, v2)

    # Test if it works for "none" direction.
    e2 = Edge.from_anchor(v3, v2, direction="none")
    assert e2 == Edge(v2, v3, has_direction=False)

    # Test if it works for 'in" direction.
    e3 = Edge.from_anchor(v3, v2, direction="in")
    assert e3 == Edge(v2, v3)


def test_edge_from_anchor_valueerror(db_3_vertices):
    """Test if the from_anchor mathod raises an exception.

    With incorrect direction.
    """
    db, v1, v2, v3 = db_3_vertices
    with pytest.raises(ValueError):
        e1 = Edge.from_anchor(v1, v2, direction="incorrect")
        del e1


def test_edge_from_pack(db_3_vertices):
    """Test if the from_pack method generate the same edges that the init()."""
    db, v1, v2, v3 = db_3_vertices
    pack1 = (2, 3, "", True)
    assert Edge.from_pack(pack1, db) == Edge(v2, v3)

    pack2 = (1, 3, "edge", False)
    assert Edge.from_pack(pack2, db) == Edge(v3, v1, "edge", False)


# TEST CHECK METHODS


def test_edge_has_vertex(db_3_vertices):
    """Test if the has_vertex method works."""
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v1, v2)
    assert e1.has_vertex(v1) is True
    assert e1.has_vertex(v2) is True
    assert e1.has_vertex(v3) is False
    e2 = Edge(v1, v3)
    assert e2.has_vertex(v1) is True
    assert e2.has_vertex(v2) is False
    assert e2.has_vertex(v3) is True


# TEST ANCHORS METHODS


def test_edge_change_anchor(db_3_vertices):
    """Test if the change_anchor method changes the right attributes."""
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v1, v2)
    e1.change_anchor(v1)
    assert e1.anchor is v1
    assert e1.other is v2
    assert e1.direction == "out"
    e1.change_anchor(v2)
    assert e1.anchor is v2
    assert e1.other is v1
    assert e1.direction == "in"

    e2 = Edge(v2, v3, has_direction=False)
    e2.change_anchor(v2)
    assert e2.anchor is v2
    assert e2.other is v3
    assert e2.direction == "none"
    e2.change_anchor(v3)
    assert e2.anchor is v3
    assert e2.other is v2
    assert e2.direction == "none"


def test_edge_change_anchor_valuerror(db_3_vertices):
    """Test if the change_anchor method raises an exception.

    When the given anchor doesn't belong the the edge.
    """
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v1, v2)
    with pytest.raises(ValueError):
        e1.change_anchor(v3)


# TEST EXPORT METHODS


def test_edge_pack(db_3_vertices):
    """Test if the pack method return the correct pack."""
    db, v1, v2, v3 = db_3_vertices
    e1 = Edge(v2, v3, label="edge", has_direction=True)
    assert e1.pack() == (2, 3, "edge", True)
    e2 = Edge(v2, v1, has_direction=False)
    assert e2.pack() == (1, 2, "", False)


# TEST PROPERTIES


def test_edge_properties_read_only(db_3_vertices):
    """Test if modifiying a read-only property raises an exception."""
    db, v1, v2, v3 = db_3_vertices
    edge = Edge(v1, v2)

    def wrapper(prop_name):
        """Test if it raises an AttributeError."""
        with pytest.raises(AttributeError):
            setattr(edge, prop_name, 1)

    wrapper("start")
    wrapper("end")
    wrapper("label")
    wrapper("has_direction")
    wrapper("anchor")
    wrapper("other")
    wrapper("direction")
