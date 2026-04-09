"""Tests for dsr_utils.matplotlib utility module."""

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from dsr_utils.matplotlib import get_artist_bbox


class TestMatplotlibUtilities:
    """
    Test suite for Matplotlib coordinate and artist bounding box helpers.

    Ensures that artist dimensions are correctly translated across
    different coordinate systems using a provided renderer.
    """

    def test_get_artist_bbox_accuracy(self):
        """
        Verify that the bounding box for a Text artist is correctly calculated.

        Ensures the function returns a valid Bbox when provided with a figure,
        an artist, and a valid renderer.
        """
        fig = Figure()
        canvas = FigureCanvasAgg(fig)
        renderer = canvas.get_renderer()
        ax = fig.add_subplot(111)

        # Create a text element for measurement
        text_artist = ax.text(0.5, 0.5, "Test String", fontsize=12)

        # get_artist_bbox requires the object, target transform, and renderer
        bbox = get_artist_bbox(text_artist, transform_to=fig, renderer=renderer)

        assert isinstance(bbox, Bbox)
        assert bbox.width > 0
        assert bbox.height > 0

    def test_get_artist_bbox_translation_to_axes(self):
        """
        Verify bounding box calculation when transforming to an Axes coordinate system.
        """
        fig = Figure()
        canvas = FigureCanvasAgg(fig)
        renderer = canvas.get_renderer()
        ax = fig.add_subplot(111)

        text_artist = ax.text(0.1, 0.1, "Aligned Text")

        # Test translation specifically to the Axes coordinate frame
        bbox = get_artist_bbox(text_artist, transform_to=ax, renderer=renderer)

        assert isinstance(bbox, Bbox)
        # Bbox in Axes coordinates should be within or near the [0, 1] range
        assert bbox.x0 >= -0.1
