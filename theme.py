"""
Theme configuration and utilities for the Stock Analysis Dashboard.

Provides consistent color palettes, Plotly templates, and styling helpers
with support for light/dark mode detection.
"""

import streamlit as st
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ColorPalette:
    """Color palette for consistent theming."""

    # Primary brand colors
    primary: str = "#6366F1"      # Indigo
    primary_light: str = "#818CF8"
    primary_dark: str = "#4F46E5"

    # Semantic colors
    positive: str = "#10B981"     # Emerald green
    positive_light: str = "#34D399"
    positive_dark: str = "#059669"

    negative: str = "#EF4444"     # Red
    negative_light: str = "#F87171"
    negative_dark: str = "#DC2626"

    warning: str = "#F59E0B"      # Amber
    warning_light: str = "#FBBF24"

    neutral: str = "#6B7280"      # Gray
    neutral_light: str = "#9CA3AF"
    neutral_dark: str = "#4B5563"

    # Chart colors (ordered for multi-series)
    chart_1: str = "#6366F1"      # Indigo
    chart_2: str = "#10B981"      # Emerald
    chart_3: str = "#F59E0B"      # Amber
    chart_4: str = "#EC4899"      # Pink
    chart_5: str = "#8B5CF6"      # Violet
    chart_6: str = "#06B6D4"      # Cyan

    # Background/surface colors (light mode)
    background: str = "#FFFFFF"
    surface: str = "#F8FAFC"
    surface_elevated: str = "#F1F5F9"

    # Text colors
    text_primary: str = "#1E293B"
    text_secondary: str = "#64748B"
    text_muted: str = "#94A3B8"

    # Border colors
    border: str = "#E2E8F0"
    border_light: str = "#F1F5F9"

    @property
    def chart_palette(self) -> list[str]:
        """Get ordered list of chart colors."""
        return [
            self.chart_1, self.chart_2, self.chart_3,
            self.chart_4, self.chart_5, self.chart_6,
        ]

    @property
    def gradient_colorscale(self) -> list[list]:
        """Colorscale for gradient charts (negative to positive)."""
        return [
            [0.0, self.negative],
            [0.35, self.negative_light],
            [0.5, self.warning_light],
            [0.65, self.positive_light],
            [1.0, self.positive],
        ]


@dataclass(frozen=True)
class DarkColorPalette(ColorPalette):
    """Dark mode color palette overrides."""

    # Background/surface colors (dark mode)
    background: str = "#0F172A"      # Slate 900
    surface: str = "#1E293B"         # Slate 800
    surface_elevated: str = "#334155"  # Slate 700

    # Text colors (dark mode)
    text_primary: str = "#F8FAFC"
    text_secondary: str = "#CBD5E1"
    text_muted: str = "#94A3B8"

    # Border colors (dark mode)
    border: str = "#334155"
    border_light: str = "#475569"


# Singleton palette instances
LIGHT_PALETTE = ColorPalette()
DARK_PALETTE = DarkColorPalette()


def detect_dark_mode() -> bool:
    """
    Detect if Streamlit is in dark mode.

    Note: Streamlit doesn't expose theme directly, so we check query params
    or use a session state preference. Falls back to light mode.
    """
    # Check session state for user preference
    if "theme_mode" in st.session_state:
        return st.session_state.theme_mode == "dark"

    # Default to light mode
    return False


def get_palette() -> ColorPalette:
    """Get the appropriate color palette based on current theme."""
    if detect_dark_mode():
        return DARK_PALETTE
    return LIGHT_PALETTE


def get_plotly_template() -> str:
    """Get Plotly template name based on current theme."""
    return "plotly_dark" if detect_dark_mode() else "plotly_white"


def get_plotly_layout_defaults() -> dict:
    """
    Get default Plotly layout settings for consistent styling.

    Returns:
        Dict of layout parameters to pass to fig.update_layout()
    """
    palette = get_palette()
    is_dark = detect_dark_mode()

    return {
        "template": get_plotly_template(),
        "paper_bgcolor": "rgba(0,0,0,0)",  # Transparent to inherit Streamlit bg
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Inter, system-ui, sans-serif",
            "color": palette.text_primary,
        },
        "title": {
            "font": {"size": 16, "color": palette.text_primary},
            "x": 0,
            "xanchor": "left",
        },
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"size": 11, "color": palette.text_secondary},
        },
        "xaxis": {
            "gridcolor": palette.border if not is_dark else palette.border_light,
            "linecolor": palette.border,
            "tickfont": {"color": palette.text_secondary},
            "title": {"font": {"color": palette.text_secondary}},
        },
        "yaxis": {
            "gridcolor": palette.border if not is_dark else palette.border_light,
            "linecolor": palette.border,
            "tickfont": {"color": palette.text_secondary},
            "title": {"font": {"color": palette.text_secondary}},
        },
        "hoverlabel": {
            "bgcolor": palette.surface_elevated,
            "font": {"color": palette.text_primary, "size": 12},
            "bordercolor": palette.border,
        },
        "margin": {"l": 60, "r": 40, "t": 50, "b": 50},
    }


def apply_chart_theme(fig) -> None:
    """
    Apply consistent theme styling to a Plotly figure in-place.

    Args:
        fig: Plotly Figure object
    """
    fig.update_layout(**get_plotly_layout_defaults())


def get_gradient_colorscale() -> list[list]:
    """Get the gradient colorscale for price/drawdown charts."""
    return get_palette().gradient_colorscale


def style_metric_card(value: str, delta: Optional[str] = None, is_positive: Optional[bool] = None) -> str:
    """
    Generate styled HTML for a metric card.

    Args:
        value: The main metric value
        delta: Optional delta/change value
        is_positive: Whether the delta is positive (for coloring)

    Returns:
        HTML string for the styled metric
    """
    palette = get_palette()

    delta_html = ""
    if delta is not None:
        color = palette.positive if is_positive else palette.negative if is_positive is False else palette.neutral
        delta_html = f'<span style="color: {color}; font-size: 0.9em;">{delta}</span>'

    return f"""
    <div style="
        background: {palette.surface};
        border: 1px solid {palette.border};
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    ">
        <div style="font-size: 1.5em; font-weight: 600; color: {palette.text_primary};">{value}</div>
        {delta_html}
    </div>
    """


def inject_custom_css() -> None:
    """Inject custom CSS for enhanced styling."""
    palette = get_palette()
    is_dark = detect_dark_mode()

    css = f"""
    <style>
        /* Smooth transitions */
        .stApp {{
            transition: background-color 0.3s ease;
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background: {palette.surface};
            border: 1px solid {palette.border};
            border-radius: 8px;
            padding: 12px 16px;
        }}

        [data-testid="stMetricValue"] {{
            font-weight: 600;
        }}

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: {palette.surface};
            border-radius: 6px;
            border: 1px solid {palette.border};
            padding: 8px 16px;
        }}

        .stTabs [aria-selected="true"] {{
            background: {palette.primary};
            border-color: {palette.primary};
            color: white;
        }}

        /* Expander styling */
        .streamlit-expanderHeader {{
            background: {palette.surface};
            border-radius: 6px;
        }}

        /* Dividers */
        hr {{
            border-color: {palette.border};
            opacity: 0.5;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {palette.surface};
        }}

        /* DataFrames */
        .stDataFrame {{
            border: 1px solid {palette.border};
            border-radius: 8px;
        }}

        /* Info/Warning boxes */
        .stAlert {{
            border-radius: 8px;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}

        /* Slider */
        .stSlider > div > div {{
            background: {palette.primary};
        }}

        /* Quote banner styling */
        .quote-banner {{
            background: linear-gradient(135deg, {palette.surface} 0%, {palette.surface_elevated} 100%);
            border: 1px solid {palette.border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        /* Card container */
        .metric-card {{
            background: {palette.surface};
            border: 1px solid {palette.border};
            border-radius: 10px;
            padding: 16px;
            transition: box-shadow 0.2s ease;
        }}

        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def create_theme_toggle() -> None:
    """Create a theme toggle in the sidebar."""
    current_mode = "dark" if detect_dark_mode() else "light"

    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("Theme")
    with col2:
        if st.button("🌙" if current_mode == "light" else "☀️", key="theme_toggle"):
            st.session_state.theme_mode = "dark" if current_mode == "light" else "light"
            st.rerun()


# Color utility functions for charts
def rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def get_volume_colors(pct_changes: list[float]) -> list[str]:
    """Get volume bar colors based on price changes."""
    palette = get_palette()
    return [
        rgba(palette.positive, 0.6) if c >= 0 else rgba(palette.negative, 0.6)
        for c in pct_changes
    ]


def get_profit_loss_color(value: float) -> str:
    """Get color for profit/loss value."""
    palette = get_palette()
    if value > 0:
        return palette.positive
    elif value < 0:
        return palette.negative
    return palette.neutral
