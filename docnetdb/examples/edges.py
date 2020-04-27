"""This module defines some examples of Edge subclassing."""

from datetime import datetime

from docnetdb.edge import Edge


class EdgeWithProcessOnInsertion(Edge):
    """A special Edge that add an extra attribute when inserted."""

    def __init__(self, *args, **kwargs):
        """Override the __init__ method to add the custom attribute."""
        super().__init__(*args, **kwargs)
        self.insertion_date = None

    def on_insert(self) -> None:
        """Override the on_insert method."""
        self.insertion_date = datetime.now().isoformat()


class ColoredEdge(Edge):
    """A special Edge with a color attribute."""

    def __init__(self, *args, **kwargs):
        """Override the __init__ method."""
        try:
            color = kwargs.pop("color")
        except KeyError:
            color = None
        super().__init__(*args, **kwargs)
        self.color = color

    @classmethod
    def from_pack(cls, pack, db) -> "ColoredEdge":
        """Override the from_pack method to extract the color attribute."""
        *old_pack, color = pack
        edge = super(ColoredEdge, cls).from_pack(old_pack, db)
        assert isinstance(edge, ColoredEdge)
        edge.color = color
        return edge

    def pack(self):
        """Override the pack method to add the color attribute."""
        old_pack = super().pack()
        new_pack = (*old_pack, self.color)
        return new_pack
