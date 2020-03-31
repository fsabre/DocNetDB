"""This module defines some tests on the Vertex class."""

import pytest

from docnetdb import Vertex


def test_vertex_init_place():
    """Test if the Vertex init makes a not-inserted vertex."""
    vertex = Vertex()
    assert vertex.is_inserted is False


def test_vertex_init_parameter():
    """Test if the Vertex init uses the dict if provided."""
    vertex = Vertex({"name": "Reflexion", "chapter": 6})
    assert vertex["name"] == "Reflexion"
    assert vertex["chapter"] == 6


def test_vertex_init_dict_copy():
    """Test if the Vertex init doesn't reference the provided dict."""
    initial_data = {"name": "Reflexion", "chapter": 6}
    vertex = Vertex(initial_data)
    initial_data["name"] = "NAME CHANGED"
    assert vertex["name"] == "Reflexion"


def test_vertex_items():
    """Test if the Vertex item access functions like a dict."""
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
