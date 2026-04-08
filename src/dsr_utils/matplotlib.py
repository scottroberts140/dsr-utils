"""Matplotlib helpers for computing artist and axis bounding boxes."""

from typing import TYPE_CHECKING, Union

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase


def get_artist_bbox(
    obj: Artist, transform_to: Union[Figure, Axes], renderer: "RendererBase"
) -> Bbox:
    """
    Return an artist's bounding box in axes or figure coordinates.

    This function calculates the window extent of an artist in pixels and
    transforms it into the coordinate space of the target Figure or Axes.

    Parameters
    ----------
    obj : Artist
        The Matplotlib artist to measure (e.g., text, line, or patch).
    transform_to : Figure or Axes
        The target coordinate space for the resulting bounding box.
    renderer : RendererBase
        The active renderer used for measurement.

    Returns
    -------
    Bbox
        The bounding box transformed into the target coordinate system.

    Raises
    ------
    ValueError
        If the artist is not attached to a figure, making measurement impossible.
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
    """
    Return an axis' bounding box in axes coordinates.

    Calculates the extent of an entire Axes object and transforms it into
    normalized axes coordinates.

    Parameters
    ----------
    ax : Axes
        The target Matplotlib axis to measure.
    renderer : RendererBase
        The active renderer used for measurement.

    Returns
    -------
    Bbox
        The bounding box in normalized axes coordinates.
    """
    bbox_px = ax.get_window_extent(renderer=renderer)
    inv = ax.transAxes.inverted()
    return bbox_px.transformed(inv)
