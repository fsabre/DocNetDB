"""This module defines some tests on the examples vertices."""

import pytest

from docnetdb import DocNetDB
from docnetdb.examples.vertices import (
    IntListVertex,
    ListVertex,
    VertexWithDataValidation,
    VertexWithMandatoryFields,
)
from docnetdb.exceptions import VertexNotReadyException


def test_vertex_with_data_validation():
    """Test if this Vertex allows only integers as elements values."""
    v = VertexWithDataValidation()
    v["elem1"] = 5
    with pytest.raises(TypeError):
        v["elem2"] = "I'm not an integer"


def test_vertex_with_mandatory_fields(tmp_path):
    """Test if this Vertex adds an extra field with the date when inserted."""
    db = DocNetDB(tmp_path / "db.db")
    weiss = VertexWithMandatoryFields(
        {
            "name": "Weiss Schnee",
            "weapon": "Myrtenaster",
            "semblance": "Glyphs",
        }
    )
    pyrrha = VertexWithMandatoryFields(
        {
            "name": "Pyrrha Nikos",
            "weapon": "Milo and Akouo",
            "semblance": "Polarity",
        }
    )
    qrow = VertexWithMandatoryFields(
        {"weapon": "Harbinger", "semblance": "Misfortune"}
    )
    db.insert(weiss)
    db.insert(pyrrha)
    with pytest.raises(VertexNotReadyException):
        db.insert(qrow)


def test_intlistvertex():
    """Test if this Vertex works correctly.

    It is to test the correct inheritance of a Vertex subclass.
    """
    v = IntListVertex()

    # Test if the init works
    assert v.list == []

    # Test if the append method works
    v.append(1)
    assert v.list == [1]
    v.append(2)
    assert v.list == [1, 2]

    # Test if the append method only accepts ints
    with pytest.raises(TypeError):
        v.append("3")


def test_intlistvertex_load(tmp_path):
    """Test if this Vertex keeps its type when saved and loaded."""
    db = DocNetDB(tmp_path / "db.db")
    v = IntListVertex()
    v.append(12)
    db.insert(v)
    db.save()

    db2 = DocNetDB(
        tmp_path / "db.db", vertex_creation_callable=IntListVertex.from_pack
    )
    assert isinstance(db2[1], IntListVertex)
    assert db2[1].list == [12]


def test_intlistvertex_from_pack(tmp_path):
    """Test if the from_pack method raises a ValueError."""
    db = DocNetDB(tmp_path / "db.db")
    v = ListVertex()
    v.append("not OK")
    db.insert(v)
    db.save()

    with pytest.raises(ValueError):
        db2 = DocNetDB(
            tmp_path / "db.db",
            vertex_creation_callable=IntListVertex.from_pack,
        )
        del db2
