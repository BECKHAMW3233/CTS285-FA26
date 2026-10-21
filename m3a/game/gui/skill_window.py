# gui/skill_window.py
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional
from database import Database
from gui import dialogs as messagebox
from gui.layout import fit_window, scaled_font

BRANCH_TITLES = {
    'offense': 'Offense',
    'defense': 'Defense',
    'utility': 'Utility',
}


class SkillWindow(tk.Toplevel):
    """
    Lets the player spend earned skill points on the skill tree. A node can
    only be unlocked once its branch prerequisite is already unlocked.
    """
    def __init__(self, master: tk.Tk, character: Any, on_change: Optional[Callable] = None):
        super().__init__(master)
        self.title("Skills")
        self.transient(master)
        fit_window(self, 640, 460, parent=master)
        self.grab_set()

        self.character = character
        self.on_change = on_change
        self.db = Database()

        self._points_label = None
        self._build_ui()

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        header = ttk.Frame(self, padding=10)
        header.pack(fill='x')
        self._points_label = ttk.Label(
            header,
            text=f"Unspent Skill Points: {self.character.skill_points}",
            font=scaled_font(self, 11, 'Arial', 'bold')
        )
        self._points_label.pack(side='left')

        branches = self.db.get_skill_branches()
        columns = ttk.Frame(self, padding=10)
        columns.pack(fill='both', expand=True)

        for branch_name, nodes in branches.items():
            column = ttk.LabelFrame(columns, text=BRANCH_TITLES.get(branch_name, branch_name.title()), padding=8)
            column.pack(side='left', fill='both', expand=True, padx=5)

            for node in sorted(nodes, key=lambda n: n['tier']):
                self._build_node_row(column, node)

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=8)

    def _build_node_row(self, parent: tk.Widget, node: dict):
        unlocked = self.character.has_skill(node['id'])
        can_unlock = self.character.can_unlock_skill(node['id'])

        frame = ttk.Frame(parent, padding=4)
        frame.pack(fill='x', pady=3)

        status = "Unlocked" if unlocked else ("Locked" if not can_unlock else "Available")
        kind_tag = "Active" if node['kind'] == 'active' else "Passive"
        title = f"{node['name']} ({kind_tag}) - {status}"
        ttk.Label(frame, text=title, font=scaled_font(self, 10, 'Arial', 'bold')).pack(anchor='w')
        ttk.Label(frame, text=node['description'], wraplength=180).pack(anchor='w')

        if not unlocked:
            button = ttk.Button(
                frame,
                text=f"Unlock (cost {node['cost']})",
                command=lambda n=node: self._unlock(n)
            )
            button.pack(anchor='e', pady=2)
            if not can_unlock:
                button.config(state='disabled')

    def _unlock(self, node: dict):
        if self.character.unlock_skill(node['id']):
            if self.on_change:
                self.on_change()
            self._build_ui()
        else:
            messagebox.showwarning("Skills", "Can't unlock that skill right now.")
