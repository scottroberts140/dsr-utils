"""Matplotlib helpers for computing artist and axis bounding boxes."""

from typing import Union, TYPE_CHECKING
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox
from matplotlib.axes import Axes

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase


def get_artist_bbox(
    obj: Artist, transform_to: Union[Figure, Axes], renderer: "RendererBase"
) -> Bbox:
    """Return an artist's bounding box in axes or figure coordinates.

    Args:
        obj: Matplotlib artist to measure.
        transform_to: Target coordinate space (Figure or Axes).
        renderer: Active renderer used for measurement.

    Returns:
        Bounding box in the target coordinate system.
    """
    fig = obj.get_figure()

    if fig is None:
        raise ValueError("Artist must be attached to a figure to measure Bbox.")

    bbox_px = obj.get_window_extent(renderer=renderer)

    if hasattr(transform_to, "transAxes"):
        inv = transform_to.transAxes.inverted()  # type: ignore
    else:
        inv = transform_to.transFigure.inverted()  # type: ignore

    return bbox_px.transformed(inv)


def get_axis_bbox(ax: Axes, renderer: "RendererBase") -> Bbox:
    """Return an axis' bounding box in axes coordinates.

    Args:
        ax: Target axis.
        renderer: Active renderer used for measurement.

    Returns:
        Bounding box in axes coordinates.
    """
    bbox_px = ax.get_window_extent(renderer=renderer)
    inv = ax.transAxes.inverted()
    return bbox_px.transformed(inv)
