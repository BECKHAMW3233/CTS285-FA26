"""Shared helpers for sizing/positioning windows and scaling fonts, so every
Toplevel in the app (not just the main window) responds to screen size and
the View > Zoom setting instead of using a fixed pixel geometry."""
import tkinter as tk


def get_ui_scale(widget: tk.Misc) -> float:
    """The current zoom level, read off the root GameWindow from any widget."""
    return getattr(widget.nametowidget('.'), 'ui_scale', 1.0)


def scaled_font(widget: tk.Misc, size: int, family: str = 'Arial', *style: str) -> tuple:
    return (family, round(size * get_ui_scale(widget)), *style)


def fit_window(window: tk.Misc, base_width: int, base_height: int, parent: tk.Misc = None):
    """
    Size a Toplevel relative to a base design size and the current zoom
    level, clamped to 90% of the screen, and center it over `parent` (or
    the screen if there's no parent) - replaces a fixed .geometry("WxH")
    that didn't adapt to the zoom setting or to screens smaller/larger
    than the original design size.
    """
    scale = get_ui_scale(window)
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    width = min(round(base_width * scale), round(screen_w * 0.9))
    height = min(round(base_height * scale), round(screen_h * 0.9))

    if parent is not None:
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

    x = max(0, min(x, screen_w - width))
    y = max(0, min(y, screen_h - height))
    window.geometry(f"{width}x{height}+{x}+{y}")
