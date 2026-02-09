"""Table rendering utilities for report-friendly layouts and PDF export."""

from __future__ import annotations
import textwrap
from typing import Tuple, TYPE_CHECKING, Optional, List, Literal, Union, Any, Hashable
from dataclasses import dataclass, field
import pandas as pd
from dsr_utils.matplotlib import get_artist_bbox
from dsr_files.pdf_handler import PDFDocument
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
import matplotlib.axes
from matplotlib.collections import LineCollection

if TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.backend_bases import RendererBase


@dataclass
class TableEdgeColor:
    """Border color configuration for table edges."""

    left: str = "none"
    right: str = "none"
    top: str = "none"
    bottom: str = "none"

    @classmethod
    def _edge_color(cls, color: Optional[str], default_color: Optional[str]) -> str:
        """Resolve a single edge color with fallback to a default."""
        bc = color if color is not None else default_color
        return bc if bc is not None else "none"

    @classmethod
    def _edge_colors(
        cls,
        left_border_color: Optional[str] = None,
        right_border_color: Optional[str] = None,
        top_border_color: Optional[str] = None,
        bottom_border_color: Optional[str] = None,
        default_color: Optional[str] = None,
    ) -> TableEdgeColor:
        """Build a `TableEdgeColor` with optional per-edge overrides.

        Example:
            >>> TableEdgeColor._edge_colors(default_color="k")
            TableEdgeColor(left='k', right='k', top='k', bottom='k')
        """
        lbc = cls._edge_color(left_border_color, default_color)
        rbc = cls._edge_color(right_border_color, default_color)
        tbc = cls._edge_color(top_border_color, default_color)
        bbc = cls._edge_color(bottom_border_color, default_color)
        return TableEdgeColor(lbc, rbc, tbc, bbc)

    @classmethod
    def closed(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with all borders set to a single color."""
        return cls._edge_colors(default_color=color)

    @classmethod
    def open(
        cls,
    ) -> TableEdgeColor:
        """Return edge colors with all borders set to 'none'."""
        return cls._edge_colors()

    @classmethod
    def horizontal(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with left/right borders set (no top/bottom)."""
        return cls._edge_colors(
            left_border_color=color,
            right_border_color=color,
        )

    @classmethod
    def bottom_edge(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with only the bottom border set."""
        return cls._edge_colors(bottom_border_color=color)

    @classmethod
    def right_edge(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with only the right border set."""
        return cls._edge_colors(right_border_color=color)

    @classmethod
    def top_edge(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with only the top border set."""
        return cls._edge_colors(top_border_color=color)

    @classmethod
    def left_edge(
        cls,
        color: Optional[str] = "k",  # Black
    ) -> TableEdgeColor:
        """Return edge colors with only the left border set."""
        return cls._edge_colors(left_border_color=color)


@dataclass
class TableEdgeLinewidth:
    """Border line width configuration for table edges."""

    left: float = 0.0
    right: float = 0.0
    top: float = 0.0
    bottom: float = 0.0

    @classmethod
    def _border_linewidth(
        cls, linewidth: Optional[float], default_linewidth: Optional[float]
    ) -> float:
        """Resolve a single edge linewidth with fallback to a default."""
        lw = linewidth if linewidth is not None else default_linewidth
        return lw if lw is not None else 0.0

    @classmethod
    def edge_linewidths(
        cls,
        left_linewidth: Optional[float] = None,
        right_linewidth: Optional[float] = None,
        top_linewidth: Optional[float] = None,
        bottom_linewidth: Optional[float] = None,
        default_linewidth: Optional[float] = None,
    ) -> TableEdgeLinewidth:
        """Build a `TableEdgeLinewidth` with optional per-edge overrides."""
        llw = cls._border_linewidth(left_linewidth, default_linewidth=default_linewidth)
        rlw = cls._border_linewidth(
            right_linewidth, default_linewidth=default_linewidth
        )
        tlw = cls._border_linewidth(top_linewidth, default_linewidth=default_linewidth)
        blw = cls._border_linewidth(
            bottom_linewidth, default_linewidth=default_linewidth
        )
        return TableEdgeLinewidth(llw, rlw, tlw, blw)

    @classmethod
    def all_edges(cls, linewidth: float) -> TableEdgeLinewidth:
        """Return a `TableEdgeLinewidth` with all borders set to the same width."""
        return TableEdgeLinewidth(linewidth, linewidth, linewidth, linewidth)


@dataclass
class TableColumnStyle:
    """Styling options for a table column (fonts, colors, alignment)."""

    face_color: str = "none"
    text_color: Optional[str] = None
    edge_color: TableEdgeColor = field(default_factory=TableEdgeColor.open)
    fontfamily: Optional[str] = None
    fontsize: Optional[
        Union[
            int,
            Literal[
                "xx-small",
                "x-small",
                "small",
                "medium",
                "large",
                "x-large",
                "xx-large",
                "larger",
                "smaller",
            ],
        ]
    ] = None
    fontstyle: Optional[str] = None
    fontweight: Optional[str] = None
    fontstretch: Optional[str] = None
    math_fontfamily: str = "cm"
    alpha: Optional[float] = None
    ha: Optional[str] = None
    va: Optional[str] = None

    def yields_same_size(self, tcs: TableColumnStyle) -> bool:
        """Compare font metrics to see if two styles yield identical sizing.

        Example:
            >>> TableColumnStyle().yields_same_size(TableColumnStyle())
            True
        """
        # Compares font metrics that influence bounding box size. Assumes external layout
        # factors (such as rotation) are constant across the comparison context.
        attrs = [
            "fontfamily",
            "fontsize",
            "fontstyle",
            "fontweight",
            "fontstretch",
            "math_fontfamily",
        ]
        return all(getattr(self, a) == getattr(tcs, a) for a in attrs)


class TableColumn:
    """Schema definition for a table column, including display styles."""

    @property
    def detail_style(self) -> TableColumnStyle:
        return self._detail_style

    @property
    def header_style(self) -> Optional[TableColumnStyle]:
        return self._header_style

    @property
    def first_row_style(self) -> Optional[TableColumnStyle]:
        return self._first_row_style

    @property
    def even_row_style(self) -> Optional[TableColumnStyle]:
        return self._even_row_style

    @property
    def unique_detail_sizing_styles(self) -> List[TableColumnStyle]:
        return self._unique_detail_sizing_styles

    @property
    def lpad_fraction(self) -> float:
        return self._lpad_fraction

    @lpad_fraction.setter
    def lpad_fraction(self, value) -> None:
        self._lpad_fraction = value

    @property
    def rpad_fraction(self) -> float:
        return self._rpad_fraction

    @rpad_fraction.setter
    def rpad_fraction(self, value) -> None:
        self._rpad_fraction = value

    @property
    def clip(self) -> bool:
        return self._clip

    @clip.setter
    def clip(self, value) -> None:
        self._clip = value

    @property
    def is_fixed_width(self) -> bool:
        return self._is_fixed_width

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._scaled_width = value

    @property
    def scaled_width(self) -> float:
        return self._scaled_width

    def __init__(
        self,
        detail_style: TableColumnStyle,
        header_style: Optional[TableColumnStyle] = None,
        first_row_style: Optional[TableColumnStyle] = None,
        even_row_style: Optional[TableColumnStyle] = None,
        fixed_width: Optional[float] = None,
        max_proportional_width: Optional[float] = None,
        max_width: Optional[float] = None,
        max_width_chars: Optional[int] = None,
        has_consistent_width: bool = False,
        has_consistent_height: bool = False,
        rotation: Optional[float] = None,
        lpad: float = 0.0,
        rpad: float = 0.0,
        include_in_column_expansion: bool = True,
    ):
        self._detail_style = detail_style
        self._header_style = header_style
        self._first_row_style = first_row_style
        self._even_row_style = even_row_style

        if fixed_width is not None:
            self._is_fixed_width = True
            w = fixed_width
        else:
            self._is_fixed_width = False
            w = 0.0

        self._width = w
        self._scaled_width = w
        self.max_proportional_width = max_proportional_width
        self.max_width = max_width
        self.max_width_chars = max_width_chars
        self.has_consistent_width = has_consistent_width
        self.has_consistent_height = has_consistent_height
        self.rotation = rotation
        self.lpad = lpad
        self.rpad = rpad
        self._lpad_fraction = 0.0
        self._rpad_fraction = 0.0
        self._clip: bool = False
        self._is_first_column: bool = False
        self._is_last_column: bool = False
        self.include_in_column_expansion = include_in_column_expansion

        # Determine unique detail sizing styles
        all_styles = [self.detail_style]
        if self.first_row_style is not None:
            all_styles.append(self.first_row_style)
        if self.even_row_style is not None:
            all_styles.append(self.even_row_style)

        unique_sizing_styles: List[TableColumnStyle] = []
        for s in all_styles:
            if not any(s.yields_same_size(u) for u in unique_sizing_styles):
                unique_sizing_styles.append(s)

        self._unique_detail_sizing_styles = unique_sizing_styles

    def calc_scaled_width(self, scale: float) -> None:
        """Apply a scaling factor to the column width.

        Example:
            >>> col = TableColumn(detail_style=TableColumnStyle(), fixed_width=2.0)
            >>> col.calc_scaled_width(scale=0.5)
            >>> col.scaled_width
            1.0
        """
        if scale == 1.0:
            self._scaled_width = self.width
        else:
            self._scaled_width = self.width * scale


class Table:
    """Container for table data, columns, and layout metadata."""

    @property
    def detail_row_height_fraction(self) -> float:
        return self._detail_row_height_fraction

    @property
    def header_row_height_fraction(self) -> float:
        return self._header_row_height_fraction

    @property
    def fixed_row_height(self) -> float:
        return self._fixed_row_height

    @property
    def fontsize(self) -> int:
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value) -> None:
        self._fontsize = value
        self._row_height_padding = value * 0.4

    @property
    def table_edge_color(self) -> TableEdgeColor:
        return self._table_edge_color

    @property
    def detail_tpad_fraction(self) -> float:
        return self._detail_tpad_fraction

    @detail_tpad_fraction.setter
    def detail_tpad_fraction(self, value) -> None:
        self._detail_tpad_fraction = value
        self._calc_detail_vert_padding_fraction()

    @property
    def detail_bpad_fraction(self) -> float:
        return self._detail_bpad_fraction

    @detail_bpad_fraction.setter
    def detail_bpad_fraction(self, value) -> None:
        self._detail_bpad_fraction = value
        self._calc_detail_vert_padding_fraction()

    @property
    def header_tpad_fraction(self) -> float:
        return self._header_tpad_fraction

    @header_tpad_fraction.setter
    def header_tpad_fraction(self, value) -> None:
        self._header_tpad_fraction = value
        self._calc_header_vert_padding_fraction()

    @property
    def header_bpad_fraction(self) -> float:
        return self._header_bpad_fraction

    @header_bpad_fraction.setter
    def header_bpad_fraction(self, value) -> None:
        self._header_bpad_fraction = value
        self._calc_header_vert_padding_fraction()

    @property
    def detail_vert_padding_fraction(self) -> float:
        return self._detail_vert_padding_fraction

    @property
    def header_vert_padding_fraction(self) -> float:
        return self._header_vert_padding_fraction

    @property
    def num_rows(self) -> int:
        return self._num_rows

    @property
    def num_cols(self) -> int:
        return self._num_cols

    def __init__(
        self,
        # The dataframe is expected to have (formatted) strings in all columns.
        # Rows are printed in iloc order.
        data: pd.DataFrame,
        max_table_height: float,  # As a percentage of the axis
        mid_x: float,  # As a percentage of the axis
        top_y: float,  # As a percentage of the axis
        fontsize: int,
        columns: dict[str, TableColumn],
        cell_edge_linewidth: TableEdgeLinewidth,
        table_edge_linewidth: TableEdgeLinewidth,
        table_edge_padding: Tuple[float, float, float, float] = (
            0.0,
            0.0,
            0.0,
            0.0,
        ),  # L, R, T, B
        table_edge_color: TableEdgeColor = TableEdgeColor.open(),
        detail_tpad: float = 0.0,
        detail_bpad: float = 0.0,
        header_tpad: float = 0.0,
        header_bpad: float = 0.0,
        max_col_width: Optional[float] = None,
        include_headers: bool = True,
        equal_width_columns: bool = False,
        center_at_col: Optional[str] = None,
        use_full_axis_width: bool = False,
        fixed_row_height: bool = False,
    ):
        shape = data.shape
        self._num_rows = shape[0]
        self._num_cols = shape[1]

        if self.num_cols != len(columns):
            raise ValueError(
                f"Length of columns list ({len(columns)}) does not match number of columns in data ({self.num_cols})."
            )

        for col in data.columns:
            if col not in columns:
                raise ValueError(f"TableColumn object not specified for column {col}.")

            if include_headers:
                if columns[col].header_style is None:
                    raise ValueError(f"Header style not specified for column {col}.")

        columns[data.columns[0]]._is_first_column = True
        columns[data.columns[-1]]._is_last_column = True
        self.data = data
        self._detail_row_height_fraction = 0.0
        self.max_table_height = max_table_height
        self.mid_x = mid_x
        self.top_y = top_y
        self._row_height_padding: float = 0.0
        self.fontsize = fontsize
        self.columns = columns
        self.cell_edge_linewidth = cell_edge_linewidth
        self.table_edge_linewidth = table_edge_linewidth
        self.table_edge_padding = table_edge_padding
        self._table_edge_color = table_edge_color
        self.max_col_width = max_col_width
        self.include_headers = include_headers
        self.equal_width_columns = equal_width_columns
        self.center_at_col = center_at_col
        self._table_edge_padding_fraction: Tuple[float, float, float, float] = (
            0.0,
            0.0,
            0.0,
            0.0,
        )  # L, R, T, B
        self.detail_tpad = detail_tpad
        self.detail_bpad = detail_bpad
        self.header_tpad = header_tpad
        self.header_bpad = header_bpad
        self._detail_tpad_fraction = 0.0
        self._detail_bpad_fraction = 0.0
        self._header_tpad_fraction = 0.0
        self._header_bpad_fraction = 0.0
        self._detail_vert_padding_fraction = 0.0
        self._header_vert_padding_fraction = 0.0
        self.use_full_axis_width = use_full_axis_width
        self._row_height_exceptions: dict[Hashable, float] = {}
        self._header_row_height_fraction = 0.0
        self._fixed_row_height = fixed_row_height

    def _calc_detail_vert_padding_fraction(self) -> None:
        """Recalculate combined vertical padding for detail rows."""
        self._detail_vert_padding_fraction = (
            self.detail_tpad_fraction + self.detail_bpad_fraction
        )

    def _calc_header_vert_padding_fraction(self) -> None:
        """Recalculate combined vertical padding for header rows."""
        self._header_vert_padding_fraction = (
            self.header_tpad_fraction + self.header_bpad_fraction
        )

    def get_row_height(
        self, index: int, is_first_row: bool, is_last_row: bool
    ) -> float:
        """Return the row height (as axis fraction), accounting for padding.

        Args:
            index: Row index; use -1 for header row.
            is_first_row: Whether this is the first rendered row.
            is_last_row: Whether this is the last rendered row.

        Returns:
            Row height including edge padding.
        """
        if self.fixed_row_height:
            row_height = self.detail_row_height_fraction
        else:
            if index == -1:
                row_height = self.header_row_height_fraction
            else:
                row_height = self._row_height_exceptions.get(
                    index, self.detail_row_height_fraction
                )

        if is_first_row:
            row_height += self._table_edge_padding_fraction[2]

        if is_last_row:
            row_height += self._table_edge_padding_fraction[3]

        return row_height


class TablePage:
    """Represents a single rendered page of a table."""

    @property
    def start_row_iloc(self) -> int:
        return self._start_row_iloc

    @property
    def end_row_iloc(self) -> int:
        return self._end_row_iloc

    @property
    def rect(self) -> Rectangle:
        return self._rect

    @rect.setter
    def rect(self, val: Rectangle) -> None:
        self._rect = val

    @property
    def scaled_rect(self) -> Rectangle:
        return self._scaled_rect

    def __init__(
        self,
        start_row_iloc: int,
        end_row_iloc: int,
        rect: Rectangle,  # Relative to axis
    ) -> None:
        self._start_row_iloc = start_row_iloc
        self._end_row_iloc = end_row_iloc
        self._rect = rect
        self._scaled_rect = rect

    def calc_scaled_rect(
        self, width_scale: float, height_scale: float, target_mid_x: float
    ) -> None:
        """Scale and reposition the page rectangle for a target axis.

        Args:
            width_scale: Horizontal scaling factor.
            height_scale: Vertical scaling factor.
            target_mid_x: Target axis midpoint (0-1) for centering.
        """
        orig_width = self.rect.get_width()
        if width_scale != 1.0:
            scaled_width = orig_width * width_scale
        else:
            scaled_width = orig_width

        self._scaled_rect.set_width(scaled_width)
        self._scaled_rect.set_x(max(0, target_mid_x - (scaled_width / 2.0)))

        if height_scale != 1.0:
            scaled_height = self.rect.get_height() * width_scale
            self._scaled_rect.set_height(scaled_height)
            self._scaled_rect.set_y(0.5 - (scaled_height / 2.0))


class TableLayout:
    """Computed layout metadata for rendering a table across pages."""

    @property
    def pages(self) -> List[TablePage]:
        return self._pages

    @property
    def total_width(self) -> float:
        return self._total_width

    @property
    def table(self) -> Table:
        return self._table

    @property
    def ax(self) -> matplotlib.axes.Axes:
        return self._ax

    @property
    def va_padding_fraction(self) -> float:
        return self._va_padding_fraction

    def __init__(
        self,
        pages: List[TablePage],
        total_width: float,
        table: Table,
        ax: matplotlib.axes.Axes,
        va_padding_fraction: float,
    ) -> None:
        self._pages = pages
        self._total_width = total_width
        self._table = table
        self._ax = ax
        self._va_padding_fraction = va_padding_fraction

    def scale_to_axis(self, ax: matplotlib.axes.Axes) -> Tuple[float, float]:
        """Scale column widths to match a different axis size.

        Args:
            ax: Target axis to scale into.

        Returns:
            (width_scale, height_scale) factors.
        """
        orig_axis_bounds = self.ax.get_window_extent()
        orig_axis_width = orig_axis_bounds.width
        scale_axis_bounds = ax.get_window_extent()
        scale_axis_width = scale_axis_bounds.width
        width_scale = orig_axis_width / scale_axis_width

        for _, tc in self.table.columns.items():
            tc.calc_scaled_width(scale=width_scale)

        orig_axis_height = orig_axis_bounds.height
        scale_axis_height = scale_axis_bounds.height
        height_scale = orig_axis_height / scale_axis_height
        return width_scale, height_scale

    def get_translated_mid_x(self, target_ax: matplotlib.axes.Axes) -> float:
        """Translate the table midpoint from the original axis to a target axis.

        Args:
            target_ax: Target axis to map into.

        Returns:
            Midpoint x coordinate in target axis fraction units.
        """
        fig = self.ax.get_figure()
        self.ax.apply_aspect()
        target_ax.apply_aspect()

        # Map original axis fraction (0.5) to Figure display pixels
        # self.ax is the original ax_params passed during dry_run
        display_pixels = self.ax.transAxes.transform((self.table.mid_x, 0))

        # Map display pixels to target axis fraction
        target_x, _ = target_ax.transAxes.inverted().transform(display_pixels)
        return target_x


def pts_to_fig_fraction(fig: Figure, pts: float, horizontal: bool = True) -> float:
    """Converts absolute points to figure-fraction units (0-1)."""
    dpi = fig.dpi
    # Points to inches
    inches = pts / dpi
    # Total figure size in inches
    fig_size_inches = fig.get_size_inches()
    total_inches = fig_size_inches[0] if horizontal else fig_size_inches[1]

    return (inches) / total_inches


def pts_fraction_to_ax_fraction(
    ax: matplotlib.axes.Axes, pts_fraction: float, horizontal: bool = True
) -> float:
    """Convert figure-fraction units to axis-fraction units.

    Args:
        ax: Target axis used to compute the axis bounding box size.
        pts_fraction: Figure-fraction value (0-1 of the full figure).
        horizontal: Whether to use width (True) or height (False) of the axis.

    Returns:
        Axis-fraction units that correspond to the same absolute distance.
    """
    bbox = ax.get_position()
    axis_dim = bbox.width if horizontal else bbox.height
    return pts_fraction / axis_dim


def ax_fraction_for_fig_pts(
    fig: Figure, ax: matplotlib.axes.Axes, pts: float, horizontal: bool = True
) -> float:
    """Convert points to axis-fraction units.

    Args:
        fig: Figure used to convert points to figure-fraction units.
        ax: Target axis used to convert figure fractions to axis fractions.
        pts: Absolute size in points.
        horizontal: Whether to use width (True) or height (False) of the axis.

    Returns:
        Axis-fraction units that represent the provided points.
    """
    fig_frac = pts_to_fig_fraction(fig=fig, pts=pts, horizontal=horizontal)
    return pts_fraction_to_ax_fraction(
        ax=ax, pts_fraction=fig_frac, horizontal=horizontal
    )


def _text_kwargs_from_style(style: TableColumnStyle, default_font_size: int) -> dict:
    text_props_args: dict[str, Any] = {"math_fontfamily": style.math_fontfamily}

    if style.alpha is not None:
        text_props_args["alpha"] = style.alpha

    if style.text_color is not None:
        text_props_args["color"] = style.text_color

    if style.fontfamily is not None:
        text_props_args["fontfamily"] = style.fontfamily

    if style.fontsize is not None:
        text_props_args["fontsize"] = style.fontsize
    else:
        text_props_args["fontsize"] = default_font_size

    if style.fontstyle is not None:
        text_props_args["fontstyle"] = style.fontstyle

    if style.fontweight is not None:
        text_props_args["fontweight"] = style.fontweight

    if style.fontstretch is not None:
        text_props_args["fontstretch"] = style.fontstretch

    if style.ha is not None:
        text_props_args["ha"] = style.ha

    return text_props_args


def _cell_kwargs_from_style(style: TableColumnStyle) -> dict:
    cell_props_args = {"facecolor": style.face_color}

    return cell_props_args


def _add_edge_segments(
    segments_by_style: dict[tuple[str, float], list[list[tuple[float, float]]]],
    left_x: float,
    top_y: float,
    right_x: float,
    bottom_y: float,
    edge_color: TableEdgeColor,
    linewidth: TableEdgeLinewidth,
) -> None:
    """Collects line segments grouped by (color, width) to minimize collection count."""

    edges = [
        (edge_color.top, linewidth.top, [(left_x, top_y), (right_x, top_y)]),
        (edge_color.left, linewidth.left, [(left_x, top_y), (left_x, bottom_y)]),
        (
            edge_color.bottom,
            linewidth.bottom,
            [(left_x, bottom_y), (right_x, bottom_y)],
        ),
        (edge_color.right, linewidth.right, [(right_x, top_y), (right_x, bottom_y)]),
    ]

    for color, width, coords in edges:
        if color != "none" and width > 0.0:
            key = (color, width)
            if key not in segments_by_style:
                segments_by_style[key] = []
            segments_by_style[key].append(coords)


def _calc_text_dim(
    text: Artist,
    ax: matplotlib.axes.Axes,
    renderer: "RendererBase",
    w_pad: float,
    h_pad: float,
) -> Tuple[float, float]:
    """Return text width and height in axis-fraction units.

    This helper is used to measure rendered text and apply padding when
    estimating cell sizes. It is primarily for internal sizing logic and
    is documented for maintainability.

    Args:
        text: The text artist to measure.
        ax: Axis the text is rendered in (for unit conversion).
        renderer: Active renderer used for accurate bounding boxes.
        w_pad: Horizontal padding to add (axis-fraction units).
        h_pad: Vertical padding to add (axis-fraction units).

    Returns:
        Tuple of (width, height) in axis-fraction units.
    """
    bbox = get_artist_bbox(text, transform_to=ax, renderer=renderer)
    w = bbox.width + w_pad
    h = bbox.height + h_pad
    return w, h


def _calc_metrics(
    fig: Figure,
    ax: matplotlib.axes.Axes,
    table: Table,
    padding_pts: float,
    renderer: RendererBase,
) -> None:
    """Compute layout metrics and cache them on the `Table`.

    This function measures text, padding, and line widths to derive:
    - header/detail row heights
    - column widths
    - per-row height exceptions
    - padding fractions in axis units

    It mutates `table` in-place and exists mainly to support the
    sizing pipeline before rendering.

    Args:
        fig: Figure used for points-to-fraction conversions.
        ax: Axis used for measuring text in axis-fraction units.
        table: Table to populate with computed metrics.
        padding_pts: Default padding in points to include in measurements.
        renderer: Renderer used for text size measurements.
    """
    top_fraction = 0.0
    bot_fraction = 0.0
    padding_fraction = 0.0
    h_pad = 0.0
    table._detail_row_height_fraction = 0.0
    temp_text = ax.text(0, 0, "", transform=ax.transAxes)
    col_names = table.data.columns

    def get_ax_fraction_for_pts(pts: float, horizontal: bool) -> float:
        return ax_fraction_for_fig_pts(fig=fig, ax=ax, pts=pts, horizontal=horizontal)

    # Calculate table tpad, bpad fractions
    table.header_tpad_fraction = get_ax_fraction_for_pts(
        pts=table.header_tpad, horizontal=False
    )
    table.header_bpad_fraction = get_ax_fraction_for_pts(
        pts=table.header_bpad, horizontal=False
    )
    table.detail_tpad_fraction = get_ax_fraction_for_pts(
        pts=table.detail_tpad, horizontal=False
    )
    table.detail_bpad_fraction = get_ax_fraction_for_pts(
        pts=table.detail_bpad, horizontal=False
    )

    # Calculate lpad, rpad, padding fractions
    for col in col_names:
        table_column: TableColumn = table.columns[col]
        table_column.lpad_fraction = get_ax_fraction_for_pts(
            pts=table_column.lpad, horizontal=True
        )
        table_column.rpad_fraction = get_ax_fraction_for_pts(
            pts=table_column.rpad, horizontal=True
        )
        padding_frac = get_ax_fraction_for_pts(pts=padding_pts, horizontal=False)

        if padding_frac > padding_fraction:
            padding_fraction = padding_frac

        for cs in table_column.unique_detail_sizing_styles:
            elw = table.cell_edge_linewidth
            lw = elw.top
            if cs.edge_color.top != "none" and lw > 0.0:
                frac = get_ax_fraction_for_pts(pts=lw, horizontal=True)

                if frac > top_fraction:
                    top_fraction = frac

            lw = elw.bottom
            if cs.edge_color.bottom != "none" and lw > 0.0:
                frac = get_ax_fraction_for_pts(pts=lw, horizontal=True)

                if frac > bot_fraction:
                    bot_fraction = frac

    h_pad = padding_fraction + top_fraction + bot_fraction

    # Determine default row height
    for col in col_names:
        table_column: TableColumn = table.columns[col]
        temp_text.set_text("Agj")
        for cs in table_column.unique_detail_sizing_styles:
            kwargs = _text_kwargs_from_style(style=cs, default_font_size=table.fontsize)
            temp_text.set(**kwargs)
            _, text_height_fraction = _calc_text_dim(
                text=temp_text, ax=ax, renderer=renderer, w_pad=0.0, h_pad=h_pad
            )
            text_height_fraction += table.detail_vert_padding_fraction

            if text_height_fraction > table._detail_row_height_fraction:
                table._detail_row_height_fraction = text_height_fraction

    # Determine row width/height for header
    if table.include_headers:
        for col in col_names:
            table_column: TableColumn = table.columns[col]
            header_style = (
                table_column.header_style
                if table_column.header_style is not None
                else table_column.detail_style
            )
            temp_text.set_text(col)
            kwargs = _text_kwargs_from_style(
                style=header_style, default_font_size=table.fontsize
            )
            temp_text.set(**kwargs)
            header_width, header_height = _calc_text_dim(
                text=temp_text,
                ax=ax,
                renderer=renderer,
                w_pad=table_column.lpad_fraction + table_column.rpad_fraction,
                h_pad=h_pad,
            )
            header_height += table.header_vert_padding_fraction

            if not table_column.is_fixed_width:
                table_column.width = header_width

            if header_height > table._header_row_height_fraction:
                table._header_row_height_fraction = header_height
    else:
        table._header_row_height_fraction = 0.0

    # Determine width, height for data
    is_first_row = True
    for row_idx, row_data in table.data.iterrows():
        max_h_for_this_row = table.detail_row_height_fraction

        for col_name in col_names:
            tc = table.columns[col_name]
            cell_text = row_data[col_name]

            # --- OPTIMIZATION CHECK ---
            # 1. Skip if width is consistent AND we've already measured row 0
            # 2. Skip if height is consistent AND text is too short to wrap
            # Note: We must still check if wrapping is possible even if height is 'consistent'
            skip_width = tc.has_consistent_width and not is_first_row

            # We can only skip height if it's consistent AND not wrapping.
            # If it might wrap, we MUST check it to populate exceptions.
            max_width_chars = (
                tc.max_width_chars if tc.max_width_chars is not None else 0
            )
            is_wrapping = (
                tc.max_width_chars is not None and len(cell_text) > tc.max_width_chars
            )
            skip_height = (
                tc.has_consistent_height and not is_wrapping and not is_first_row
            )

            if skip_width and skip_height:
                continue

            # --- MEASUREMENT PATH ---
            w_pad = tc.lpad_fraction + tc.rpad_fraction
            w = tc.width

            if tc.rotation is not None:
                temp_text.set_rotation(tc.rotation)

            if is_wrapping:
                temp_text.set_text(textwrap.fill(cell_text, width=max_width_chars))
            else:
                temp_text.set_text(cell_text)

            for cs in tc.unique_detail_sizing_styles:
                kwargs = _text_kwargs_from_style(
                    style=cs, default_font_size=table.fontsize
                )
                temp_text.set(**kwargs)
                text_width, text_height = _calc_text_dim(
                    text=temp_text,
                    ax=ax,
                    renderer=renderer,
                    w_pad=w_pad,
                    h_pad=h_pad,
                )
                text_height += table.detail_vert_padding_fraction

                # Update row height, if this cell is taller
                if text_height > max_h_for_this_row:
                    max_h_for_this_row = text_height

                # Update column width, only if we aren't skipping width checks
                if not skip_width:
                    if text_width > w:
                        w = text_width
                    if table.max_col_width is not None and w > table.max_col_width:
                        w = table.max_col_width
                        tc.clip = True

            tc.width = w

        is_first_row = False

        if max_h_for_this_row > table.detail_row_height_fraction:
            table._row_height_exceptions[row_idx] = max_h_for_this_row

    temp_text.remove()


def _get_col_style(
    tc: TableColumn,
    is_header_row: bool = False,
    is_first_row: bool = False,
    is_even_row: bool = False,
) -> TableColumnStyle:
    """Resolve the effective style for a column in the current row.

    Selection order depends on row type:
    - Header rows prefer `header_style` when available.
    - First detail rows prefer `first_row_style` when available.
    - Even detail rows prefer `even_row_style` when available.
    - Otherwise fall back to `detail_style`.

    Args:
        tc: Table column with styling configuration.
        is_header_row: Whether the row is a header row.
        is_first_row: Whether this is the first detail row.
        is_even_row: Whether this is an even-numbered detail row.

    Returns:
        The resolved `TableColumnStyle` to use for the cell.
    """
    if is_first_row:
        if tc.first_row_style is not None:
            style = tc.first_row_style
        else:
            style = tc.detail_style
    elif not is_header_row:
        if is_even_row and tc.even_row_style is not None:
            style = tc.even_row_style
        else:
            style = tc.detail_style
    else:
        if tc.header_style is not None:
            style = tc.header_style
        else:
            style = tc.detail_style

    return style


def _render_row(
    ax: matplotlib.axes.Axes,
    left_x: float,
    top_y: float,
    row_height: float,
    columns: dict[str, TableColumn],
    data: pd.Series,
    styles: dict[str, TableColumnStyle],
    default_font_size: int,
    edge_linewidth: TableEdgeLinewidth,
    va_padding_fraction: float,
    table_edge_padding_fraction: Tuple[float, float, float, float],
    cell_top_padding_fraction: float,
    cell_bottom_padding_fraction: float,
    segments_by_style: dict[tuple[str, float], list[list[tuple[float, float]]]],
    is_first_row: bool = False,
    is_last_row: bool = False,
) -> None:
    """Render a single table row into the provided axis.

    This draws background rectangles, places text, and collects edge
    line segments for later batching. It is designed as a low-level
    routine used by header/detail row helpers.

    Args:
        ax: Target axis for drawing.
        left_x: Left edge of the row in axis-fraction units.
        top_y: Top edge of the row in axis-fraction units.
        row_height: Height of the row in axis-fraction units.
        columns: Column definitions keyed by column name.
        data: Row data keyed by column name.
        styles: Style mapping keyed by column name.
        default_font_size: Fallback font size for text rendering.
        edge_linewidth: Linewidth definition for cell edges.
        va_padding_fraction: Vertical alignment offset in axis units.
        table_edge_padding_fraction: Table edge padding tuple
            (left, right, top, bottom) in axis units.
        cell_top_padding_fraction: Top cell padding in axis units.
        cell_bottom_padding_fraction: Bottom cell padding in axis units.
        segments_by_style: Collector for edge segments grouped by style.
        is_first_row: Whether this is the first row in the table.
        is_last_row: Whether this is the last row in the table.
    """
    col_left_x = left_x
    bottom_y = top_y - row_height
    mid_y = (top_y + bottom_y) / 2.0
    half_row_height = row_height / 2.0

    for col, tc in columns.items():
        table_left_edge_padding_fraction = (
            table_edge_padding_fraction[0] if tc._is_first_column else 0.0
        )
        table_right_edge_padding_fraction = (
            table_edge_padding_fraction[1] if tc._is_last_column else 0.0
        )
        table_top_edge_padding_fraction = (
            table_edge_padding_fraction[2] if is_first_row else 0.0
        )
        table_bottom_edge_padding_fraction = (
            table_edge_padding_fraction[3] if is_last_row else 0.0
        )
        style = styles[col]

        match style.va:
            case "top":
                text_y_pos = (
                    top_y
                    - va_padding_fraction
                    - half_row_height
                    - table_top_edge_padding_fraction
                    - cell_top_padding_fraction
                )
                va = "center"
            case "center":
                text_y_pos = mid_y
                va = "center"
            case _:  # bottom
                text_y_pos = (
                    bottom_y
                    + va_padding_fraction
                    + table_bottom_edge_padding_fraction
                    + cell_bottom_padding_fraction
                )
                va = "bottom"

        ha: Literal["left", "center", "right"] = "left"
        match style.ha:
            case "center":
                text_x_pos = (col_left_x + (col_left_x + tc.scaled_width)) / 2.0
                ha = "center"
            case "right":
                text_x_pos = (
                    col_left_x
                    + tc.scaled_width
                    - tc.rpad_fraction
                    - table_right_edge_padding_fraction
                )
                ha = "right"
            case _:  # left
                text_x_pos = (
                    col_left_x + tc.lpad_fraction + table_left_edge_padding_fraction
                )
                ha = "left"

        rect = Rectangle(
            (
                col_left_x,
                bottom_y,
            ),
            width=tc.scaled_width,
            height=row_height,
            **_cell_kwargs_from_style(style=style),
            transform=ax.transAxes,
            zorder=1,
        )
        ax.add_patch(rect)
        kwargs = _text_kwargs_from_style(
            style=style, default_font_size=default_font_size
        )
        del kwargs["ha"]
        text_obj = ax.text(
            x=text_x_pos,
            y=text_y_pos,
            s=data[col],
            transform=ax.transAxes,
            zorder=2,
            va=va,
            ha=ha,
            **kwargs,
        )

        if tc.clip:
            text_obj.set_clip_path(rect)

        _add_edge_segments(
            segments_by_style=segments_by_style,
            left_x=col_left_x - table_left_edge_padding_fraction,
            top_y=top_y + table_top_edge_padding_fraction,
            right_x=col_left_x + tc.scaled_width + table_right_edge_padding_fraction,
            bottom_y=bottom_y - table_bottom_edge_padding_fraction,
            edge_color=style.edge_color,
            linewidth=edge_linewidth,
        )

        col_left_x += tc.scaled_width


def _render_header_row(
    ax: matplotlib.axes.Axes,
    left_x: float,
    top_y: float,
    row_height: float,
    table: Table,
    default_font_size: int,
    va_padding_fraction: float,
    segments_by_style: dict[tuple[str, float], list[list[tuple[float, float]]]],
    is_first_row: bool = False,
    is_last_row: bool = False,
) -> None:
    """Render the header row if headers are enabled.

    This resolves header styles and delegates drawing to `_render_row`.
    It is documented primarily for internal reference.

    Args:
        ax: Target axis for drawing.
        left_x: Left edge of the row in axis-fraction units.
        top_y: Top edge of the row in axis-fraction units.
        row_height: Height of the row in axis-fraction units.
        table: Table containing header config and column styles.
        default_font_size: Fallback font size for text rendering.
        va_padding_fraction: Vertical alignment offset in axis units.
        segments_by_style: Collector for edge segments grouped by style.
        is_first_row: Whether this is the first row in the table.
        is_last_row: Whether this is the last row in the table.
    """
    if not table.include_headers:
        return

    styles: dict[str, TableColumnStyle] = {}

    for col in table.data.columns:
        tc = table.columns[col]
        styles[col] = _get_col_style(tc, is_header_row=True)

    _render_row(
        ax=ax,
        left_x=left_x,
        top_y=top_y,
        row_height=row_height,
        columns=table.columns,
        data=table.data.columns.to_series(),
        styles=styles,
        default_font_size=default_font_size,
        edge_linewidth=table.cell_edge_linewidth,
        va_padding_fraction=va_padding_fraction,
        table_edge_padding_fraction=table._table_edge_padding_fraction,
        cell_top_padding_fraction=table.header_tpad_fraction,
        cell_bottom_padding_fraction=table.header_bpad_fraction,
        segments_by_style=segments_by_style,
        is_first_row=is_first_row,
        is_last_row=is_last_row,
    )


def _render_detail_row(
    ax: matplotlib.axes.Axes,
    left_x: float,
    top_y: float,
    row_height: float,
    table: Table,
    iloc: int,
    default_font_size: int,
    va_padding_fraction: float,
    segments_by_style: dict[tuple[str, float], list[list[tuple[float, float]]]],
    is_even_row: bool,
    is_first_row: bool = False,
    is_last_row: bool = False,
) -> None:
    """Render a single detail (data) row.

    This resolves per-row styles (first/even/default) and delegates the
    actual drawing to `_render_row`.

    Args:
        ax: Target axis for drawing.
        left_x: Left edge of the row in axis-fraction units.
        top_y: Top edge of the row in axis-fraction units.
        row_height: Height of the row in axis-fraction units.
        table: Table containing data and column styles.
        iloc: Row index in the underlying DataFrame.
        default_font_size: Fallback font size for text rendering.
        va_padding_fraction: Vertical alignment offset in axis units.
        segments_by_style: Collector for edge segments grouped by style.
        is_even_row: Whether the row index is even (0-based).
        is_first_row: Whether this is the first row in the table.
        is_last_row: Whether this is the last row in the table.
    """
    styles: dict[str, TableColumnStyle] = {}

    for col in table.data.columns:
        tc = table.columns[col]
        styles[col] = _get_col_style(
            tc, is_first_row=(iloc == 0), is_even_row=is_even_row
        )

    _render_row(
        ax=ax,
        left_x=left_x,
        top_y=top_y,
        row_height=row_height,
        columns=table.columns,
        data=table.data.iloc[iloc],
        styles=styles,
        default_font_size=default_font_size,
        edge_linewidth=table.cell_edge_linewidth,
        va_padding_fraction=va_padding_fraction,
        table_edge_padding_fraction=table._table_edge_padding_fraction,
        cell_top_padding_fraction=table.detail_tpad_fraction,
        cell_bottom_padding_fraction=table.detail_bpad_fraction,
        segments_by_style=segments_by_style,
        is_first_row=is_first_row,
        is_last_row=is_last_row,
    )


def render_table(
    pdf_page: PDFDocument.Page,
    table: Table,
    ax: Optional[matplotlib.axes.Axes] = None,
    dry_run: bool = False,
    renderer: Optional[RendererBase] = None,
) -> TableLayout:
    """Render a table into a PDF page using matplotlib.

    Args:
        pdf_page: Target PDF page wrapper.
        table: Table definition to render.
        ax: Optional axis to render into (defaults to full-page axes).
        dry_run: If True, only computes layout without drawing.
        renderer: Optional renderer for text measurements.

    Returns:
        A `TableLayout` describing the rendered pages and layout.
    """
    fig = pdf_page.fig

    if ax is None:
        ax = fig.add_axes((0, 0, 1, 1))

    if renderer is None:
        canvas: Any = fig.canvas
        renderer = canvas.get_renderer()

    assert (
        renderer is not None
    ), "Renderer must be initialized before calling _calc_metrics"

    ax.axis("off")

    if len(table.data) == 0:
        ax.text(
            x=table.mid_x,
            y=table.top_y,
            s="No data to display",
            fontsize=table.fontsize,
            fontstyle="italic",
            ha="center",
        )
        table_page = TablePage(
            start_row_iloc=-1,
            end_row_iloc=-1,
            rect=Rectangle((0.0, table.top_y), 1.0, 1.0),
        )
        return TableLayout(
            pages=[table_page],
            total_width=1.0,
            table=table,
            ax=ax,
            va_padding_fraction=0.0,
        )

    def get_ax_fraction_for_pts(pts: float, horizontal: bool) -> float:
        return ax_fraction_for_fig_pts(fig=fig, ax=ax, pts=pts, horizontal=horizontal)

    va_padding_fraction = get_ax_fraction_for_pts(
        table._row_height_padding, horizontal=False
    )

    _calc_metrics(
        fig=fig,
        ax=ax,
        table=table,
        padding_pts=table._row_height_padding,
        renderer=renderer,
    )
    total_row_count = table.num_rows

    if table.equal_width_columns:
        max_col_width = max(c.width for c in table.columns.values())

        if max_col_width is not None:
            for c in table.columns.values():
                c.width = max_col_width

    total_w = sum(c.width for c in table.columns.values())

    for c in table.columns.values():
        if c.max_proportional_width is not None:
            if c.max_proportional_width != 1.0:
                width_adjustment = c.width - min(
                    c.width, total_w * c.max_proportional_width
                )
                c.width -= width_adjustment
                total_w += width_adjustment

    if table.use_full_axis_width:
        remaining_width = (
            get_artist_bbox(obj=ax, transform_to=ax, renderer=renderer).width - total_w
        )

        if remaining_width > 0.0:
            total_w += remaining_width
            cols_to_adjust = [
                c
                for c, tc in table.columns.items()
                if tc.include_in_column_expansion
                and (
                    tc.max_proportional_width is None
                    or (
                        tc.max_proportional_width is not None
                        and tc.max_proportional_width == 1.0
                    )
                )
            ]
            addl_width_per_column = remaining_width / len(cols_to_adjust)

            for c in cols_to_adjust:
                table.columns[c].width += addl_width_per_column

    total_w = sum(c.width for c in table.columns.values())

    if table.center_at_col is not None:
        left_w = 0.0
        col_list = table.data.columns.to_list()

        for col in col_list:
            if col == table.center_at_col:
                break

            left_w += table.columns[col].width
    else:
        left_w = total_w / 2.0

    right_w = total_w - left_w
    left_x = table.mid_x - left_w
    right_x = table.mid_x + right_w
    remaining_row_count = total_row_count
    y_pos = table.top_y
    row_iloc = 0

    table_left_padding_fraction = get_ax_fraction_for_pts(
        pts=table.table_edge_padding[0], horizontal=True
    )
    table_right_padding_fraction = get_ax_fraction_for_pts(
        pts=table.table_edge_padding[1], horizontal=True
    )
    table_top_padding_fraction = get_ax_fraction_for_pts(
        pts=table.table_edge_padding[2], horizontal=False
    )
    table_bottom_padding_fraction = get_ax_fraction_for_pts(
        pts=table.table_edge_padding[3], horizontal=False
    )

    table._table_edge_padding_fraction = (
        table_left_padding_fraction,
        table_right_padding_fraction,
        table_top_padding_fraction,
        table_bottom_padding_fraction,
    )

    table_pages: List[TablePage] = []
    max_table_height = table.max_table_height
    page_top_y = y_pos
    continuation_page_addl_height = pdf_page.continuation_page_top_y - page_top_y
    continuation_page_height = max_table_height + continuation_page_addl_height
    continuation_page_top_y = page_top_y + continuation_page_addl_height

    while remaining_row_count > 0:
        is_first_row = True
        is_last_row = remaining_row_count == 1
        max_available_height = max_table_height
        height_for_next_row = table.get_row_height(
            index=-1,
            is_first_row=is_first_row,
            is_last_row=is_last_row,
        )
        if table.include_headers:
            is_first_row = False
            y_pos -= height_for_next_row
        else:
            height_for_next_row = 0.0

        max_available_height -= height_for_next_row
        height_for_next_row = table.get_row_height(
            index=table.data.index[row_iloc],
            is_first_row=is_first_row,
            is_last_row=is_last_row,
        )
        start_row_iloc = row_iloc

        while (
            remaining_row_count > 0
            and (max_available_height - height_for_next_row) > 0.0
        ):
            row_iloc += 1
            y_pos -= height_for_next_row
            remaining_row_count -= 1
            max_available_height -= height_for_next_row

            if remaining_row_count == 0:
                break

            is_last_row = remaining_row_count == 1
            is_first_row = False
            height_for_next_row = table.get_row_height(
                index=table.data.index[row_iloc],
                is_first_row=is_first_row,
                is_last_row=is_last_row,
            )

            if max_available_height < height_for_next_row:
                break

        left_x = max(0.0, left_x - table._table_edge_padding_fraction[0])
        right_x = min(1.0, right_x + table._table_edge_padding_fraction[1])
        top_y = min(1.0, page_top_y + table._table_edge_padding_fraction[2])
        bottom_y = max(0.0, y_pos - table._table_edge_padding_fraction[3])
        rect = Rectangle((left_x, bottom_y), right_x - left_x, top_y - bottom_y)

        table_pages.append(
            TablePage(start_row_iloc=start_row_iloc, end_row_iloc=row_iloc, rect=rect)
        )
        max_table_height = continuation_page_height
        page_top_y = continuation_page_top_y

    table_layout = TableLayout(
        pages=table_pages,
        total_width=total_w,
        table=table,
        ax=ax,
        va_padding_fraction=va_padding_fraction,
    )

    if not dry_run:
        render_table_from_page_layout(pdf_page=pdf_page, table_layout=table_layout)

    return table_layout


def render_table_from_page_layout(
    pdf_page: PDFDocument.Page,
    table_layout: TableLayout,
    page_index: Optional[int] = None,
    using_axis: Optional[matplotlib.axes.Axes] = None,
    adjust_mid_x: bool = True,
) -> None:
    """Render a specific page from a precomputed table layout.

    Args:
        pdf_page: Target PDF page wrapper.
        table_layout: Layout metadata for the table.
        page_index: Optional page index to render (defaults to first page).
        using_axis: Optional axis to render into.
        adjust_mid_x: If True, center the table horizontally.
    """
    segments_by_style = {}  # Key: (color, width), Value: List of segments
    table = table_layout.table

    if using_axis is not None:
        ax = using_axis
        # Calculate scale and use translated center point
        width_scale, _ = table_layout.scale_to_axis(ax=using_axis)

        if adjust_mid_x:
            target_mid_x = table_layout.get_translated_mid_x(target_ax=using_axis)
        else:
            target_mid_x = table_layout.table.mid_x
    else:
        ax = table_layout.ax
        width_scale = 1.0
        target_mid_x = table.mid_x

    va_padding_fraction = table_layout.va_padding_fraction

    if page_index is None:
        start_page_index = 0
        end_page_index = len(table_layout.pages)
    else:
        start_page_index = page_index
        end_page_index = page_index + 1

    is_first_page = True

    def finish_page() -> None:
        for (color, width), segments in segments_by_style.items():
            lc = LineCollection(
                segments,
                colors=color,
                linewidths=width,
                transform=ax.transAxes,
                zorder=3,  # Ensure edges are above cell backgrounds
            )
            ax.add_collection(lc)

        segments_by_style.clear()

    for page in table_layout.pages[start_page_index:end_page_index]:
        if not is_first_page:
            finish_page()
            pdf_page = pdf_page.pdf_doc.create_continuation_page(page=pdf_page)
            ax_pos = ax.get_position()
            ax = pdf_page.fig.add_axes(ax_pos.bounds)
            ax.axis("off")

        is_first_page = False
        page.calc_scaled_rect(
            width_scale=width_scale,
            height_scale=1.0,
            target_mid_x=target_mid_x,
        )
        rect = page.scaled_rect
        is_first_row = True
        left_x, bottom_y = rect.xy
        right_x = left_x + rect.get_width()
        top_y = bottom_y + rect.get_height()
        y_pos = top_y
        is_even_row = False

        if table.include_headers:
            is_last_row = page.start_row_iloc == page.end_row_iloc
            row_height = table.get_row_height(
                index=-1,
                is_first_row=is_first_row,
                is_last_row=is_last_row,
            )
            _render_header_row(
                ax=ax,
                left_x=left_x,
                top_y=y_pos,
                row_height=row_height,
                table=table,
                default_font_size=table.fontsize,
                va_padding_fraction=va_padding_fraction,
                segments_by_style=segments_by_style,
                is_first_row=is_first_row,
                is_last_row=is_last_row,
            )
            y_pos -= row_height
            is_first_row = False

        for row_iloc in range(page.start_row_iloc, page.end_row_iloc):
            is_last_row = row_iloc == page.end_row_iloc

            row_height = table.get_row_height(
                index=row_iloc,
                is_first_row=is_first_row,
                is_last_row=is_last_row,
            )
            _render_detail_row(
                ax=ax,
                left_x=left_x,
                top_y=y_pos,
                row_height=row_height,
                table=table,
                iloc=row_iloc,
                default_font_size=table.fontsize,
                va_padding_fraction=va_padding_fraction,
                segments_by_style=segments_by_style,
                is_even_row=is_even_row,
                is_first_row=is_first_row,
                is_last_row=is_last_row,
            )
            y_pos -= row_height
            is_first_row = False
            is_even_row = not is_even_row

        table_left_edge = max(0.0, left_x - table._table_edge_padding_fraction[0])
        table_right_edge = min(1.0, right_x + table._table_edge_padding_fraction[1])
        table_top_edge = min(1.0, top_y + table._table_edge_padding_fraction[2])
        table_bottom_edge = max(0.0, y_pos - table._table_edge_padding_fraction[3])
        _add_edge_segments(
            segments_by_style=segments_by_style,
            left_x=table_left_edge,
            top_y=table_top_edge,
            right_x=table_right_edge,
            bottom_y=table_bottom_edge,
            edge_color=table.table_edge_color,
            linewidth=table.table_edge_linewidth,
        )

    finish_page()
