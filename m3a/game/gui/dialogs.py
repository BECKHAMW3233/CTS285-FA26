"""
Drop-in replacement for tkinter.messagebox. On Windows, messagebox.* shells
out to the native OS message-box dialog, which Tk cannot theme or resize -
that's why the View > Zoom font scale never touched them. These rebuild the
same four calls (showinfo/showwarning/showerror/askyesno, same (title,
message) signature) as plain ttk Toplevels, so they inherit the zoomed
named fonts and can be sized like any other window.
"""
import tkinter as tk
from tkinter import ttk

from gui.layout import get_ui_scale


def _build_dialog(title: str, message: str, buttons: list):
    parent = tk._default_root
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.resizable(False, False)

    result = {'value': None}

    frame = ttk.Frame(dialog, padding=20)
    frame.pack(fill='both', expand=True)

    wraplength = round(400 * get_ui_scale(dialog))
    ttk.Label(frame, text=message, wraplength=wraplength, justify='left').pack(pady=(0, 15))

    button_row = ttk.Frame(frame)
    button_row.pack()

    def choose(value):
        result['value'] = value
        dialog.destroy()

    buttons_built = []
    for label, value in buttons:
        btn = ttk.Button(button_row, text=label, command=lambda v=value: choose(v), width=10)
        btn.pack(side='left', padx=5)
        buttons_built.append(btn)

    default_value = buttons[-1][1]
    dialog.protocol("WM_DELETE_WINDOW", lambda: choose(default_value))
    dialog.bind('<Return>', lambda e: choose(default_value))

    dialog.update_idletasks()
    _position_dialog(dialog, parent)

    dialog.grab_set()
    buttons_built[-1].focus_set()
    dialog.wait_window()
    return result['value']


def _position_dialog(dialog: tk.Toplevel, parent: tk.Misc):
    width = dialog.winfo_reqwidth()
    height = dialog.winfo_reqheight()
    screen_w = dialog.winfo_screenwidth()
    screen_h = dialog.winfo_screenheight()
    width = min(width, round(screen_w * 0.8))
    height = min(height, round(screen_h * 0.8))

    if parent is not None and parent.winfo_viewable():
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

    x = max(0, min(x, screen_w - width))
    y = max(0, min(y, screen_h - height))
    dialog.geometry(f"{width}x{height}+{x}+{y}")


def showinfo(title: str, message: str):
    _build_dialog(title, message, [("OK", True)])


def showwarning(title: str, message: str):
    _build_dialog(title, message, [("OK", True)])


def showerror(title: str, message: str):
    _build_dialog(title, message, [("OK", True)])


def askyesno(title: str, message: str) -> bool:
    return bool(_build_dialog(title, message, [("Yes", True), ("No", False)]))
