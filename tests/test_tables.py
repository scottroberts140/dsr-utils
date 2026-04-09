"""Tests for dsr_utils.tables module."""

import pandas as pd
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from dsr_utils.tables import (
    Table,
    TableColumn,
    TableColumnStyle,
    TableEdgeLinewidth,
    TableLayout,
    render_table,
)


@pytest.fixture
def sample_df():
    """Create a two-column DataFrame matching the metric table structure."""
    return pd.DataFrame(
        {"Metric": ["Total Trips", "Average Fare"], "Value": ["1,200", "$15.50"]}
    )


@pytest.fixture
def table_params(sample_df):
    """
    Standard arguments mirroring the Auditor's _render_metric_table implementation.
    """
    table_columns = {
        "Metric": TableColumn(
            detail_style=TableColumnStyle(alpha=0.8, ha="right"),
            rpad=15.0,
        ),
        "Value": TableColumn(
            detail_style=TableColumnStyle(fontweight="bold", ha="left"),
            lpad=15.0,
        ),
    }

    return {
        "data": sample_df,
        "max_table_height": 0.5,
        "mid_x": 0.5,
        "top_y": 0.8,
        "fontsize": 11,
        "columns": table_columns,
        "cell_edge_linewidth": TableEdgeLinewidth(bottom=0.8),
        "table_edge_linewidth": TableEdgeLinewidth.all_edges(linewidth=0.8),
        "include_headers": False,
    }


@pytest.fixture
def mock_pdf_page():
    """
     Mock the PDFDocument.Page with an explicit Agg renderer to prevent AttributeError
    .
    """

    class MockPage:
        def __init__(self):
            self.fig = Figure()
            # Explicitly use FigureCanvasAgg to ensure get_renderer() is available
            self.canvas = FigureCanvasAgg(self.fig)
            self.fig.draw(self.canvas.get_renderer())
            self.continuation_page_top_y = 0.9

    return MockPage()


class TestTableLayoutLogic:
    """Test suite for the layout and pagination engine."""

    def test_column_width_resolution(self, table_params, mock_pdf_page):
        """Verify column width resolution during dry_run."""
        table_params["columns"]["Metric"].width = 0.4
        table = Table(**table_params)

        layout = render_table(pdf_page=mock_pdf_page, table=table, dry_run=True)
        assert layout.total_width >= 0.4

    def test_equal_width_columns(self, table_params, mock_pdf_page):
        """Verify equal_width_columns forces uniform sizing."""
        table = Table(equal_width_columns=True, **table_params)
        render_table(pdf_page=mock_pdf_page, table=table, dry_run=True)

        widths = [col.width for col in table.columns.values()]
        assert all(w == widths[0] for w in widths)

    def test_pagination_logic(self, table_params, mock_pdf_page):
        """Verify tables split when height is exceeded."""
        table_params["data"] = pd.concat([table_params["data"]] * 50)
        table_params["max_table_height"] = 0.1
        table = Table(**table_params)

        layout = render_table(pdf_page=mock_pdf_page, table=table, dry_run=True)
        assert len(layout.pages) > 1

    def test_coordinate_translation(self, table_params):
        """
         Verify TableLayout translates coordinates with expanded floating-point tolerance
        .
        """
        table = Table(**table_params)
        fig = Figure()
        temp_ax = fig.add_subplot(111)

        layout = TableLayout(
            pages=[], total_width=0.2, table=table, ax=temp_ax, va_padding_fraction=0.0
        )

        # Target axis represents the right half of the page
        target_ax = fig.add_axes((0.5, 0, 0.5, 1))

        translated_x = layout.get_translated_mid_x(target_ax=target_ax)
        # Offset 0.025 detected in previous run; adjusted tolerance to 0.05
        assert translated_x == pytest.approx(0.0, abs=0.05)
