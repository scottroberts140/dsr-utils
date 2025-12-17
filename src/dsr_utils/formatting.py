from enum import Enum
import textwrap


class TextAlignment(Enum):
    """Enumeration for text alignment options in formatted output.

    Used for aligning text in tables, reports, and other formatted displays.

    Attributes:
        Unspecified: No alignment specified, uses default alignment.
        Left: Align text to the left margin.
        Center: Center text within available space.
        Right: Align text to the right margin.
    """
    Unspecified = 0,
    Left = 1,
    Center = 2,
    Right = 3,


def format_text(
        text: str,
        buffer_width: int,
        prefix: str,
        suffix: str,
        fill_buffer: bool = False,
        alignment: TextAlignment = TextAlignment.Left,
        include_start_lf: bool = False,
        include_end_lf: bool = False,
        insert_leading_space: bool = False
) -> str:
    """Format text with wrapping, alignment, and decorative borders for display.

    This utility function formats text within a specified width, adds prefix/suffix
    characters (typically border characters), handles text alignment, and optionally
    wraps long text across multiple lines. Commonly used for creating formatted
    console output with consistent visual styling.

    Args:
        text: The text content to format.
        buffer_width: Total width including prefix and suffix characters.
        prefix: String to prepend to each line (e.g., border character).
        suffix: String to append to each line (e.g., border character).
        fill_buffer: If True, repeats text to fill the entire buffer width.
            Useful for creating separator lines. Defaults to False.
        alignment: Text alignment within the buffer (Left, Center, or Right).
            Defaults to TextAlignment.Left.
        include_start_lf: If True, prepends a newline before the formatted text.
            Defaults to False.
        include_end_lf: If True, appends a newline after the formatted text.
            Defaults to False.
        insert_leading_space: If True, adds a space after the prefix on each line.
            Reduces usable buffer width by 1. Defaults to False.

    Returns:
        Formatted string with applied alignment, wrapping, and border characters.
        Multi-line text is separated by newline characters.

    Example:
        >>> # Simple bordered text
        >>> format_text(
        ...     text="Model Results",
        ...     buffer_width=50,
        ...     prefix="|",
        ...     suffix="|",
        ...     alignment=TextAlignment.Center
        ... )
        '|              Model Results               |'

        >>> # Create a separator line
        >>> format_text(
        ...     text="=",
        ...     buffer_width=50,
        ...     prefix="|",
        ...     suffix="|",
        ...     fill_buffer=True
        ... )
        '|================================================|'

        >>> # Long text with wrapping
        >>> format_text(
        ...     text="This is a very long text that will wrap",
        ...     buffer_width=30,
        ...     prefix="| ",
        ...     suffix=" |",
        ...     insert_leading_space=True
        ... )
        '|  This is a very long    |\\n|  text that will wrap   |'

    Note:
        The actual usable width for text is buffer_width minus the lengths of
        prefix and suffix (and minus 1 if insert_leading_space is True).
        Text wrapping uses Python's textwrap module for clean line breaks.
    """
    buffer_width -= (len(prefix) + len(suffix))
    text_alignment = '<'

    if alignment is TextAlignment.Center:
        text_alignment = '^'

    if alignment is TextAlignment.Right:
        text_alignment = '>'

    leading_space = ''

    if insert_leading_space:
        leading_space = ' '
        buffer_width -= 1

    if fill_buffer:
        repetitions = (buffer_width // len(text)) + 1
        repeated_text = text * repetitions
        text = repeated_text[:buffer_width]

    wrapped_lines = textwrap.wrap(text, buffer_width)

    # This code allows a blank line to be printed if text = ' ' and fill_buffer = True
    if len(wrapped_lines) == 0:
        wrapped_lines = [text]

    formatted_text = ''
    is_first_line = True
    new_line_text = ''

    for wl in wrapped_lines:
        aligned_text = f'{leading_space}{wl:{text_alignment}{buffer_width}}'
        formatted_text += f'{new_line_text}{prefix}{aligned_text}{suffix}'

        if is_first_line:
            is_first_line = False
            new_line_text = '\n'

    if include_start_lf:
        start_lf = '\n'
    else:
        start_lf = ''

    if include_end_lf:
        end_lf = '\n'
    else:
        end_lf = ''

    return f'{start_lf}{formatted_text}{end_lf}'
