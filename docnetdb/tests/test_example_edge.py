"""This module defines some tests on the examples edges."""

import pytest

from docnetdb import DocNetDB, Vertex
from docnetdb.edge_examples import ColoredEdge, EdgeWithProcessOnInsertion


@pytest.fixture
def db_2_vertices(tmp_path):
    """Create a DocNetDB and two inserted vertices."""
    db = DocNetDB(tmp_path / "db.db")
    v1, v2 = Vertex(), Vertex()
    db.insert(v1)
    db.insert(v2)
    return db, v1, v2


def test_edge_with_process_on_insertion(db_2_vertices):
    """Test if this Edge gets an extra attribute when inserted."""
    db, v1, v2 = db_2_vertices
    edge = EdgeWithProcessOnInsertion(v1, v2)
    assert edge.insertion_date is None
    db.insert_edge(edge)
    assert hasattr(edge, "insertion_date")


def test_colorededge(db_2_vertices):
    """Test if this custom Edge works properly."""
    db, v1, v2 = db_2_vertices

    # Test if the init works
    edge = ColoredEdge(v1, v2, label="", has_direction=None, color="green")
    assert edge.color == "green"

    # Test the init default when there's no color argument
    edge = ColoredEdge(v1, v2)
    assert edge.color is None


def test_colorededge_load(db_2_vertices):
    """Test if this Edge keeps its type when saved and loaded."""
    db, v1, v2 = db_2_vertices
    path = db.path
    edge = ColoredEdge(v1, v2, color="blue")
    db.insert_edge(edge)
    db.save()

    db2 = DocNetDB(path, edge_creation_callable=ColoredEdge.from_pack)
    edge = next(db2.edges())
    assert isinstance(edge, ColoredEdge)
    assert edge.color == "blue"
    assert edge.start is db2[1]
    assert edge.end is db2[2]
