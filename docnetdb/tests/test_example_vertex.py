"""This module defines some tests on the examples vertices."""

import pytest

from docnetdb import DocNetDB
from docnetdb.vertex_examples import (
    CustomVertex,
    VertexWithDataValidation,
    VertexWithProcessOnInsertion,
)


def test_vertex_with_data_validation():
    """Test if this Vertex allows only integers as elements values."""
    v = VertexWithDataValidation()
    v["elem1"] = 5
    with pytest.raises(TypeError):
        v["elem2"] = "I'm not an integer"


def test_vertex_with_process_on_insertion(tmp_path):
    """Test if this Vertex adds an extra field with the date when inserted."""
    db = DocNetDB(tmp_path / "db.db")
    v1 = VertexWithProcessOnInsertion()
    assert "insertion_date" not in v1
    db.insert(v1)
    assert "insertion_date" in v1


def test_custom_vertex():
    """Test if this Vertex has an additionnal method."""
    v = CustomVertex()
    assert v.custom_function() == "It works !"


def test_custom_vertex_loaded(tmp_path):
    """Test if this Vertex keeps its methods when saved and loaded."""
    db = DocNetDB(tmp_path / "db.db")
    v = CustomVertex()
    db.insert(v)
    db.save()
    assert v.custom_function() == "It works !"

    db2 = DocNetDB(
        tmp_path / "db.db", vertex_creation_callable=CustomVertex.from_dict
    )
    assert db2[1].custom_function() == "It works !"
