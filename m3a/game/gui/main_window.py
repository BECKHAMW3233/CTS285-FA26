import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import Any, Optional, Dict, Callable
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, XP_BY_LEVEL, dungeon_recommended_level
from gui import dialogs as messagebox
from gui.layout import fit_window, scaled_font
import logging

BASE_FONT_SIZE = 10
MIN_UI_SCALE = 0.8
MAX_UI_SCALE = 1.6
UI_SCALE_STEP = 0.1
REFERENCE_SCREEN_WIDTH = 1920  # screens at/below this get the normal 1.0 baseline

TERRAIN_COLORS = {
    'plains': '#3c5a2e',
    'forest': '#1d3d1a',
    'water': '#1a4a7a',
    'road': '#8a7049',
}

NODE_COLORS = {
    'start': '#2e7d32',
    'village': '#6d4c21',
    'town': '#b8860b',
    'dungeon': '#4a148c',
    'encounter': '#8c4a14',
}

NODE_GLYPHS = {
    'start': 'H',
    'village': 'V',
    'town': 'T',
    'dungeon': 'D',
    'encounter': '?',
}

# (sidebar label, Character.get_equipment_display() key) for every equip slot
EQUIPMENT_SLOT_LABELS = [
    ('Melee', 'melee_weapon'),
    ('Ranged', 'ranged_weapon'),
    ('Head', 'head'),
    ('Chest', 'chest'),
    ('Hands', 'hands'),
    ('Legs', 'legs'),
    ('Shield', 'shield'),
    ('Ring L', 'ring_left'),
    ('Ring R', 'ring_right'),
    ('Necklace', 'necklace'),
]

# Paper-doll body diagram: a silhouette (drawn once) with a labeled box per
# slot positioned near the body part it represents - the standard D&D/CRPG
# equipment-screen layout (head/neck/chest/hands/legs flanked or overlaid on
# a figure, weapons and shield to the sides). Boxes are display-only (no
# unequip action exists yet); the full item names stay in the text list
# below the diagram. Format: (slot_label, equipment key, x1, y1, x2, y2).
# Canvas is 260x360. The silhouette occupies x:[65,195], y:[16,340], so the
# flanking columns (x:3-61 and x:199-257) never overlap it, verified by hand.
BODY_DIAGRAM_SIZE = (260, 360)
BODY_DIAGRAM_SLOTS = [
    ('Head', 'head', 3, 16, 61, 44),
    ('Necklace', 'necklace', 3, 52, 61, 80),
    ('Shield', 'shield', 3, 88, 61, 116),
    ('Ring L', 'ring_left', 3, 124, 61, 152),
    ('Melee', 'melee_weapon', 199, 16, 257, 44),
    ('Ranged', 'ranged_weapon', 199, 52, 257, 80),
    ('Ring R', 'ring_right', 199, 88, 257, 116),
    ('Chest', 'chest', 98, 110, 162, 145),
    ('Hands', 'hands', 98, 175, 162, 205),
    ('Legs', 'legs', 98, 250, 162, 310),
]


class GameWindow(tk.Tk):
    """
    The main game window class.
    """
    def __init__(self):
        """
        Initialize the game window.
        """
        super().__init__()
        self.title(WINDOW_TITLE)
        self.configure(bg='black')
        self._current_frame: Optional[GameFrame] = None
        self._player = None
        self.ui_scale = self._detect_initial_scale()
        self._apply_font_scale()
        fit_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        self._setup_styles()
        self._setup_menu_bar()

    def _detect_initial_scale(self) -> float:
        """
        Start the UI sized for this screen's actual resolution instead of
        always launching at 1.0 and leaving a high-resolution display with
        tiny, hard-to-read text until the user manually zooms in. Never
        starts BELOW 1.0 - a screen at or under the 1920px reference width
        just gets the normal baseline size, not a shrunken one.
        """
        auto_scale = max(1.0, self.winfo_screenwidth() / REFERENCE_SCREEN_WIDTH)
        return round(min(MAX_UI_SCALE, auto_scale), 2)

    def _setup_styles(self):
        """
        Set up the styles for the game window.
        """
        style = ttk.Style()
        style.configure('Game.TFrame', background='black')
        style.configure('Game.TLabel', background='black', foreground='white')
        style.configure('Game.TButton', padding=5)
        style.configure('Equipment.TLabel', background='dark blue', foreground='white', padding=5)
        style.configure('Merchant.TFrame', background='brown')

    def _setup_menu_bar(self):
        """
        Build the persistent menu bar (present from the start screen onward,
        not just once a game is running).
        """
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Game (Ctrl+N)", command=lambda: self.event_generate("<<NewGame>>"))
        file_menu.add_command(label="Load Game (Ctrl+L)", command=lambda: self.event_generate("<<LoadGame>>"))
        file_menu.add_command(label="Save Game (Ctrl+S)", command=lambda: self.event_generate("<<SaveGame>>"),
                               state='disabled')
        self._save_menu_index = file_menu.index('end')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.event_generate("<<QuitGame>>"))
        self._file_menu = file_menu

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In (Ctrl++)", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out (Ctrl+-)", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom (Ctrl+0)", command=self.reset_zoom)

        self.bind('<Control-plus>', lambda e: self.zoom_in())
        self.bind('<Control-equal>', lambda e: self.zoom_in())
        self.bind('<Control-minus>', lambda e: self.zoom_out())
        self.bind('<Control-0>', lambda e: self.reset_zoom())

        # Mirrors the sidebar action buttons - same virtual events, just also
        # reachable from the menu bar instead of only as on-screen buttons.
        actions_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Actions", menu=actions_menu)
        self._actions_menu_index = menu_bar.index('end')
        actions_menu.add_command(label="Save (Ctrl+S)", command=lambda: self.event_generate("<<SaveGame>>"))
        actions_menu.add_command(label="Inventory (I)", command=lambda: self.event_generate("<<ToggleInventory>>"))
        actions_menu.add_command(label="Interact (E)", command=lambda: self.event_generate("<<Interact>>"))
        actions_menu.add_command(label="Skills (K)", command=lambda: self.event_generate("<<ToggleSkills>>"))
        actions_menu.add_command(label="Camp (C)", command=lambda: self.event_generate("<<Camp>>"))
        actions_menu.add_command(label="Scout (R)", command=lambda: self.event_generate("<<Scout>>"))
        self._menu_bar = menu_bar
        menu_bar.entryconfigure(self._actions_menu_index, state='disabled')

    def set_game_active(self, active: bool):
        """
        Enable/disable the Save Game and Actions menu entries - there's
        nothing to save or act on before a character exists.
        """
        self._file_menu.entryconfigure(self._save_menu_index, state='normal' if active else 'disabled')
        self._menu_bar.entryconfigure(self._actions_menu_index, state='normal' if active else 'disabled')

    # ------------------------------------------------------------------
    # UI scale (zoom)
    # ------------------------------------------------------------------
    def zoom_in(self):
        self._set_ui_scale(self.ui_scale + UI_SCALE_STEP)

    def zoom_out(self):
        self._set_ui_scale(self.ui_scale - UI_SCALE_STEP)

    def reset_zoom(self):
        self._set_ui_scale(1.0)

    def _set_ui_scale(self, scale: float):
        scale = round(min(MAX_UI_SCALE, max(MIN_UI_SCALE, scale)), 2)
        if scale == self.ui_scale:
            return
        self.ui_scale = scale
        self._apply_font_scale()

    def _apply_font_scale(self):
        # Tk's named fonts are shared by every widget that hasn't overridden
        # its own font, so resizing them here rescales ttk labels/buttons,
        # menus, and dialog text everywhere at once, with no per-widget work.
        size = max(6, round(BASE_FONT_SIZE * self.ui_scale))
        for font_name in ('TkDefaultFont', 'TkTextFont', 'TkHeadingFont', 'TkMenuFont', 'TkFixedFont'):
            try:
                tkfont.nametofont(font_name).configure(size=size)
            except tk.TclError:
                pass

    def clear_menu(self):
        """
        Clear the current menu frame.
        """
        if self._current_frame:
            self._current_frame.destroy()

    def setup_start_screen(self):
        """
        Show the title/start screen - New Game / Load Game now live in the
        File menu instead of as always-visible buttons here.
        """
        self.clear_menu()
        frame = ttk.Frame(self, style='Game.TFrame')
        frame.pack(expand=True, fill='both')
        center = ttk.Frame(frame, style='Game.TFrame')
        center.place(relx=0.5, rely=0.5, anchor='center')
        ttk.Label(center, text=WINDOW_TITLE, style='Game.TLabel',
                  font=scaled_font(self, 24, 'Arial', 'bold')).pack(pady=(0, 10))
        ttk.Label(center, text="Use the File menu to start or load a game.",
                  style='Game.TLabel').pack()
        self._current_frame = frame

    def setup_game_ui(self):
        """
        Set up the game user interface.
        """
        self.clear_menu()
        self._current_frame = GameFrame(self)
        self._current_frame.pack(expand=True, fill='both')
        self.set_game_active(True)

    def rebind_movement_keys(self):
        """
        Re-focus the window after closing inventory/merchant windows so WASD
        keeps working (the bindings themselves are never removed).
        """
        self.focus_force()

    def show_pause_menu(self):
        """
        Show the pause menu.
        """
        pause_window = tk.Toplevel(self)
        pause_window.title("Pause Menu")
        pause_window.transient(self)
        fit_window(pause_window, 220, 270, parent=self)
        pause_window.grab_set()
        pause_window.focus_set()

        def on_closing():
            pause_window.grab_release()
            self.focus_force()
            pause_window.destroy()

        pause_window.protocol("WM_DELETE_WINDOW", on_closing)

        ttk.Button(pause_window, text="Resume", command=on_closing).pack(pady=5)
        ttk.Button(pause_window, text="Save Game",
                   command=lambda: [self.event_generate("<<SaveGame>>"), on_closing()]).pack(pady=5)
        ttk.Button(pause_window, text="Load Game",
                   command=lambda: [self.event_generate("<<LoadGame>>"), on_closing()]).pack(pady=5)
        ttk.Button(pause_window, text="Quit",
                   command=lambda: [self.event_generate("<<QuitGame>>"), on_closing()]).pack(pady=5)

    def update_game_view(self, dungeon: Any, player: Any):
        """
        Update the dungeon-instance view.
        """
        if isinstance(self._current_frame, GameFrame):
            self._current_frame.update_game_view(dungeon, player)

    def update_world_view(self, world_map: Any, player: Any):
        """
        Update the overworld-map view.
        """
        if isinstance(self._current_frame, GameFrame):
            self._current_frame.update_world_view(world_map, player)

    def update_stats_view(self, player: Any):
        """
        Update the stats view.
        """
        self._player = player
        if isinstance(self._current_frame, GameFrame):
            self._current_frame.update_stats_view(player)

    def show_inventory_ui(self, player: Any):
        """
        Show the inventory user interface.
        """
        if isinstance(self._current_frame, GameFrame):
            self._current_frame.show_inventory_ui(player)
            self.rebind_movement_keys()

    def show_merchant_ui(self, player: Any, merchant: Any, on_close: Optional[Callable] = None,
                         quest_board: Any = None):
        """
        Show the merchant user interface.

        Args:
            player: The player character.
            merchant: The merchant.
            on_close: Optional callback invoked once the merchant window closes
                      (e.g. to mark an in-dungeon merchant room as visited).
            quest_board: Optional settlement QuestBoard - adds a Quests tab
                         alongside the merchant's goods when provided.
        """
        if isinstance(self._current_frame, GameFrame):
            self._current_frame.show_merchant_ui(player, merchant, on_close, quest_board)
            self.rebind_movement_keys()


class GameFrame(ttk.Frame):
    """
    The main game frame class.
    """
    def __init__(self, master: tk.Tk):
        """
        Initialize the game frame.
        """
        super().__init__(master, style='Game.TFrame')
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """
        Set up the user interface for the game frame. Both splits (game
        view / sidebar, and the sidebar's own three columns) are draggable
        tk.PanedWindow sashes rather than fixed-width frames, so the player
        can resize e.g. the inventory column by hand instead of being stuck
        with whatever width the layout happened to give it.
        """
        content = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg='black',
                                  sashwidth=6, sashrelief='raised', bd=0)
        content.pack(expand=True, fill='both')

        self._game_view = ttk.Frame(content, style='Game.TFrame')
        content.add(self._game_view, minsize=400, stretch='always')

        self._sidebar = ttk.Frame(content, style='Game.TFrame')
        content.add(self._sidebar, minsize=460, width=740, stretch='never')

        sidebar_pane = tk.PanedWindow(self._sidebar, orient=tk.HORIZONTAL, bg='black',
                                       sashwidth=6, sashrelief='raised', bd=0)
        sidebar_pane.pack(expand=True, fill='both')

        # Three columns instead of two - the body-diagram equipment display
        # is tall enough on its own that Character Stats/Ability Scores no
        # longer fit below it in the same column without being pushed off
        # the bottom of the window.
        self._sidebar_equipment = ttk.Frame(sidebar_pane, style='Game.TFrame')
        sidebar_pane.add(self._sidebar_equipment, minsize=260, width=280, stretch='never')
        self._sidebar_stats = ttk.Frame(sidebar_pane, style='Game.TFrame')
        sidebar_pane.add(self._sidebar_stats, minsize=180, width=220, stretch='never')
        self._sidebar_right = ttk.Frame(sidebar_pane, style='Game.TFrame')
        sidebar_pane.add(self._sidebar_right, minsize=220, width=240, stretch='always')

        self._setup_equipment_display()
        self._setup_stats_view()
        self._setup_inventory_view()
        self._setup_action_buttons()

    def _setup_equipment_display(self):
        """
        Set up the equipment display in the sidebar: a body-diagram canvas
        on top (visual, at-a-glance - which slots are filled), the existing
        text list below (the actual readable detail for each slot).
        """
        self._equipment_frame = ttk.LabelFrame(self._sidebar_equipment, text="Equipment", style='Game.TFrame')
        self._equipment_frame.pack(fill='x', padx=5, pady=5)

        width, height = BODY_DIAGRAM_SIZE
        self._body_diagram = tk.Canvas(self._equipment_frame, width=width, height=height,
                                        bg='black', highlightthickness=0)
        self._body_diagram.pack(pady=(4, 8))
        self._draw_body_silhouette(self._body_diagram)
        self._body_diagram_boxes = {}
        for label, key, x1, y1, x2, y2 in BODY_DIAGRAM_SLOTS:
            rect_id = self._body_diagram.create_rectangle(x1, y1, x2, y2, fill='#1a1a2e', outline='#888', width=2)
            text_id = self._body_diagram.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=label,
                                                       fill='white', font=('Arial', 9, 'bold'))
            self._body_diagram_boxes[key] = (rect_id, text_id)

        self._equipment_labels = {}
        for label, _key in EQUIPMENT_SLOT_LABELS:
            self._equipment_labels[label] = ttk.Label(
                self._equipment_frame,
                style='Equipment.TLabel',
                text=f"{label}: None"
            )
            self._equipment_labels[label].pack(fill='x', pady=1)

    def _draw_body_silhouette(self, canvas: tk.Canvas):
        """A simple humanoid outline - head/neck/torso/arms/legs - drawn
        once behind the slot boxes, centered in the 260px-wide canvas."""
        fill, outline = '#2a2a3a', '#555'
        canvas.create_oval(134, 16, 186, 72, fill=fill, outline=outline, width=2)   # head
        canvas.create_rectangle(148, 72, 172, 86, fill=fill, outline=outline, width=2)  # neck
        canvas.create_rectangle(120, 86, 200, 254, fill=fill, outline=outline, width=2)  # torso
        canvas.create_rectangle(82, 94, 120, 244, fill=fill, outline=outline, width=2)   # left arm
        canvas.create_rectangle(200, 94, 238, 244, fill=fill, outline=outline, width=2)  # right arm
        canvas.create_rectangle(124, 254, 158, 340, fill=fill, outline=outline, width=2)  # left leg
        canvas.create_rectangle(162, 254, 196, 340, fill=fill, outline=outline, width=2)  # right leg

    def _setup_stats_view(self):
        """
        Set up the stats view in the sidebar.
        """
        self._stats_frame = ttk.LabelFrame(self._sidebar_stats, text="Character Stats", style='Game.TFrame')
        self._stats_frame.pack(fill='x', padx=5, pady=5)

        self._stats_labels = {}
        for stat in ['Name', 'Title', 'Level', 'Health', 'Attack', 'Defense', 'XP', 'Money', 'Skill Points']:
            self._stats_labels[stat] = ttk.Label(self._stats_frame, style='Game.TLabel')
            self._stats_labels[stat].pack(anchor='w', padx=5)

        self._ability_frame = ttk.LabelFrame(self._sidebar_stats, text="Ability Scores", style='Game.TFrame')
        self._ability_frame.pack(fill='x', padx=5, pady=5)
        self._ability_labels = {}
        for ability in ('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'):
            self._ability_labels[ability] = ttk.Label(self._ability_frame, style='Game.TLabel')
            self._ability_labels[ability].pack(anchor='w', padx=5)

    def _update_ability_display(self, player: Any):
        for ability, label in self._ability_labels.items():
            score = player.ability_scores.get(ability, 10)
            mod = player.ability_modifier(ability)
            sign = '+' if mod >= 0 else ''
            label.config(text=f"{ability[:3].upper()}: {score} ({sign}{mod})")

    def _next_level_xp(self, player: Any) -> str:
        if player.level >= len(XP_BY_LEVEL):
            return "max level"
        return str(XP_BY_LEVEL[player.level])

    def _setup_inventory_view(self):
        """
        Set up the inventory view in the sidebar.
        """
        self._inventory_frame = ttk.LabelFrame(self._sidebar_right, text="Inventory", style='Game.TFrame')
        self._inventory_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self._inventory_list = tk.Listbox(
            self._inventory_frame,
            bg='black',
            fg='white',
            selectmode=tk.SINGLE,
            height=8
        )
        self._inventory_list.pack(fill='both', expand=True)

    def _setup_action_buttons(self):
        """
        Set up the action buttons in the sidebar.
        """
        button_frame = ttk.Frame(self._sidebar_right, style='Game.TFrame')
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Save (Ctrl+S)",
                   command=lambda: self.event_generate("<<SaveGame>>")).pack(fill='x', padx=5, pady=2)
        ttk.Button(button_frame, text="Inventory (I)",
                   command=lambda: self.event_generate("<<ToggleInventory>>")).pack(fill='x', padx=5, pady=2)
        ttk.Button(button_frame, text="Interact (E)",
                   command=lambda: self.event_generate("<<Interact>>")).pack(fill='x', padx=5, pady=2)
        ttk.Button(button_frame, text="Skills (K)",
                   command=lambda: self.event_generate("<<ToggleSkills>>")).pack(fill='x', padx=5, pady=2)
        ttk.Button(button_frame, text="Camp (C)",
                   command=lambda: self.event_generate("<<Camp>>")).pack(fill='x', padx=5, pady=2)
        ttk.Button(button_frame, text="Scout (R)",
                   command=lambda: self.event_generate("<<Scout>>")).pack(fill='x', padx=5, pady=2)

    def _bind_events(self):
        """
        Bind events for the game frame.
        """
        self._inventory_list.bind('<Double-Button-1>', self._handle_inventory_click)
        self._inventory_list.bind('<Button-3>', self._handle_inventory_click)

    # ------------------------------------------------------------------
    # Dungeon-instance view
    # ------------------------------------------------------------------
    def update_game_view(self, dungeon: Any, player: Any):
        """
        Update the dungeon-instance view.
        """
        for widget in self._game_view.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self._game_view, bg='black', width=800, height=800)
        canvas.pack(expand=True)

        room_size = 80
        player_x, player_y = dungeon.player_pos
        offset_x = 400 - player_x * room_size
        offset_y = 400 - player_y * room_size

        view = getattr(dungeon, 'view_range', 4)
        for y in range(max(0, player_y - view), min(dungeon.size, player_y + view + 1)):
            for x in range(max(0, player_x - view), min(dungeon.size, player_x + view + 1)):
                if dungeon.rooms[y][x].is_visible:
                    self._draw_room(canvas, x, y, dungeon.rooms[y][x], room_size, offset_x, offset_y)

        self._draw_token(canvas, player_x, player_y, room_size, offset_x, offset_y, 'green')

    def _draw_room(self, canvas: tk.Canvas, x: int, y: int, room: Any, size: int, offset_x: int, offset_y: int):
        """
        Draw a single room on the game canvas.
        """
        x1 = x * size + offset_x
        y1 = y * size + offset_y
        x2 = x1 + size
        y2 = y1 + size

        canvas.create_rectangle(x1, y1, x2, y2, fill='gray20', outline='white', width=2)

        wall_width = 8
        if not room.doors['north']:
            canvas.create_line(x1, y1, x2, y1, fill='white', width=wall_width)
        else:
            canvas.create_rectangle(x1 + size // 3, y1 - 2, x2 - size // 3, y1 + 2, fill='brown', outline='white')

        if not room.doors['south']:
            canvas.create_line(x1, y2, x2, y2, fill='white', width=wall_width)
        else:
            canvas.create_rectangle(x1 + size // 3, y2 - 2, x2 - size // 3, y2 + 2, fill='brown', outline='white')

        if not room.doors['east']:
            canvas.create_line(x2, y1, x2, y2, fill='white', width=wall_width)
        else:
            canvas.create_rectangle(x2 - 2, y1 + size // 3, x2 + 2, y2 - size // 3, fill='brown', outline='white')

        if not room.doors['west']:
            canvas.create_line(x1, y1, x1, y2, fill='white', width=wall_width)
        else:
            canvas.create_rectangle(x1 - 2, y1 + size // 3, x1 + 2, y2 - size // 3, fill='brown', outline='white')

        center_x = x1 + size // 2
        center_y = y1 + size // 2
        glyph_font = ('Arial', 16, 'bold')

        if room.enemies and not room.is_cleared:
            canvas.create_text(center_x, center_y - 10, text='E', fill='red', font=glyph_font)
        if room.has_treasure and not room.treasure_looted:
            canvas.create_text(center_x, center_y, text='T', fill='yellow', font=glyph_font)
        if room.has_merchant and not room.merchant_visited:
            canvas.create_text(center_x, center_y, text='M', fill='green', font=glyph_font)
        if room.is_cleared:
            canvas.create_text(center_x + 15, center_y - 15, text='✓', fill='green', font=glyph_font)
        if room.is_end_room:
            if room.is_locked:
                glyph, color = 'V', 'orange'
            elif room.boss_defeated:
                glyph, color = 'V', 'green'
            else:
                glyph, color = 'B', 'red'
            canvas.create_text(center_x, center_y + 15, text=glyph, fill=color, font=glyph_font)
        if x == 0 and y == 0:
            canvas.create_text(center_x, y2 - 10, text='EXIT', fill='cyan', font=('Arial', 9, 'bold'))

    # ------------------------------------------------------------------
    # World-map view
    # ------------------------------------------------------------------
    def update_world_view(self, world_map: Any, player: Any):
        """
        Update the overworld-map view.
        """
        for widget in self._game_view.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self._game_view, bg='#101410', width=800, height=800)
        canvas.pack(expand=True)

        node_size = 50
        view_range = 7
        player_x, player_y = world_map.player_pos
        offset_x = 400 - player_x * node_size
        offset_y = 400 - player_y * node_size

        for y in range(max(0, player_y - view_range), min(world_map.size, player_y + view_range + 1)):
            for x in range(max(0, player_x - view_range), min(world_map.size, player_x + view_range + 1)):
                node = world_map.nodes[y][x]
                self._draw_node(canvas, x, y, node, node_size, offset_x, offset_y)

        self._draw_token(canvas, player_x, player_y, node_size, offset_x, offset_y, 'white')

    def _draw_node(self, canvas: tk.Canvas, x: int, y: int, node: Any, size: int, offset_x: int, offset_y: int):
        """
        Draw a single overworld tile: terrain as the ground color, then a
        settlement/dungeon/encounter marker on top if the tile has one.
        Every tile connects to its neighbors now (open world, not a maze),
        so door lines are no longer meaningful and aren't drawn here.
        """
        x1 = x * size + offset_x
        y1 = y * size + offset_y
        x2 = x1 + size
        y2 = y1 + size
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        terrain_fill = TERRAIN_COLORS.get(node.terrain, TERRAIN_COLORS['plains'])
        canvas.create_rectangle(x1, y1, x2, y2, fill=terrain_fill, outline='#222222')

        if node.kind == 'empty':
            return

        fill = NODE_COLORS.get(node.kind, 'gray40')
        if node.kind == 'dungeon' and node.cleared:
            fill = '#2e7d32'
        radius = 24
        canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                            fill=fill, outline='white', width=2)

        glyph = NODE_GLYPHS.get(node.kind, '')
        if glyph:
            canvas.create_text(center_x, center_y, text=glyph, fill='white', font=('Arial', 14, 'bold'))
        if node.kind == 'dungeon':
            label = 'Cleared' if node.cleared else f"Tier {node.tier} (Lv {dungeon_recommended_level(node.tier)}+)"
            canvas.create_text(center_x, center_y + radius + 12, text=label, fill='white', font=('Arial', 9))
        elif node.kind == 'encounter' and node.cleared:
            canvas.create_text(center_x, center_y + radius + 12, text='Explored', fill='gray70', font=('Arial', 9))
        elif node.kind == 'encounter' and node.scouted:
            canvas.create_text(center_x, center_y + radius + 12, text=f"Tier {node.tier}", fill='#ffcc66',
                                font=('Arial', 9))

    def _draw_token(self, canvas: tk.Canvas, x: int, y: int, size: int, offset_x: int, offset_y: int, color: str):
        """
        Draw the player's position token.
        """
        screen_x = x * size + offset_x + size // 2
        screen_y = y * size + offset_y + size // 2
        radius = 8
        canvas.create_oval(
            screen_x - radius, screen_y - radius,
            screen_x + radius, screen_y + radius,
            fill=color, outline='black', width=2
        )

    # ------------------------------------------------------------------
    # Stats / equipment / inventory sidebar
    # ------------------------------------------------------------------
    def update_stats_view(self, player: Any):
        """
        Update the stats view.
        """
        self._stats_labels['Name'].config(text=f"Name: {player.name}")
        self._stats_labels['Title'].config(text=f"Class: {player.title}")
        self._stats_labels['Level'].config(text=f"Level: {player.level}")
        self._stats_labels['Health'].config(text=f"Health: {player.current_health}/{player.max_health}")
        self._stats_labels['Attack'].config(text=f"Attack bonus: +{player.calculate_total_attack()}")
        self._stats_labels['Defense'].config(text=f"AC: {player.calculate_ac()}")
        self._stats_labels['XP'].config(text=f"XP: {player.xp} (next: {self._next_level_xp(player)})")
        self._stats_labels['Money'].config(text=f"Money: {player.money} copper")
        self._stats_labels['Skill Points'].config(text=f"Skill Points: {player.skill_points}")
        self._update_ability_display(player)

        self._update_equipment_display(player)
        self._update_inventory_list(player)

    def _update_equipment_display(self, player: Any):
        """
        Update the equipment display.
        """
        equipment_info = player.get_equipment_display()

        for label, key in EQUIPMENT_SLOT_LABELS:
            self._equipment_labels[label].config(text=f"{label}: {equipment_info[key]}")

        for _label, key, *_coords in BODY_DIAGRAM_SLOTS:
            rect_id, _text_id = self._body_diagram_boxes[key]
            filled = equipment_info[key] != "None"
            self._body_diagram.itemconfig(
                rect_id,
                fill='#4a3a1a' if filled else '#1a1a2e',
                outline='#d4af37' if filled else '#888'
            )

    def _update_inventory_list(self, player: Any):
        """
        Update the inventory list.
        """
        self._inventory_list.delete(0, tk.END)
        for item in player.inventory:
            display_text = item['name']
            if item['type'] == 'consumable' and item.get('effect', '').startswith('heal_'):
                display_text += f" (Heal: {item['effect'][len('heal_'):]})"
            self._inventory_list.insert(tk.END, display_text)

    def show_inventory_ui(self, player: Any):
        """
        Show the inventory user interface.
        """
        inventory_window = tk.Toplevel(self)
        inventory_window.title("Inventory")
        inventory_window.transient(self)
        fit_window(inventory_window, 600, 450, parent=self.master)
        inventory_window.grab_set()

        def on_closing():
            inventory_window.grab_release()
            self.master.focus_force()
            inventory_window.destroy()

        inventory_window.protocol("WM_DELETE_WINDOW", on_closing)

        equipment_frame = ttk.LabelFrame(inventory_window, text="Equipment", padding=10)
        equipment_frame.pack(fill='x', padx=5, pady=5)

        equipment_info = player.get_equipment_display()
        for label, key in EQUIPMENT_SLOT_LABELS:
            ttk.Label(equipment_frame, text=f"{label}: {equipment_info[key]}").pack(anchor='w')

        inventory_frame = ttk.LabelFrame(inventory_window, text="Items", padding=10)
        inventory_frame.pack(fill='both', expand=True, padx=5, pady=5)

        canvas = tk.Canvas(inventory_frame)
        scrollbar = ttk.Scrollbar(inventory_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for item in player.inventory:
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill='x', padx=5, pady=2)

            info_text = self._describe_item(item)
            ttk.Label(item_frame, text=info_text).pack(side='left')

            if item['type'] in ('weapon', 'ranged', 'armor', 'shield', 'ring', 'necklace'):
                ttk.Button(
                    item_frame,
                    text="Equip",
                    command=lambda i=item: self._equip_item(player, i, inventory_window)
                ).pack(side='right')
            elif item['type'] == 'consumable':
                ttk.Button(
                    item_frame,
                    text="Use",
                    command=lambda i=item: self._use_item(player, i, inventory_window)
                ).pack(side='right')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(inventory_window, text="Close", command=on_closing).pack(pady=10)

    def _describe_item(self, item: Dict) -> str:
        info_text = item['name']
        if item['type'] in ('weapon', 'ranged'):
            info_text += f" ({item['damage_dice']} {item.get('damage_type', '')})"
        elif item['type'] == 'armor':
            info_text += f" ({item.get('slot', 'chest').capitalize()}, AC {item['base_ac']})"
        elif item['type'] == 'shield':
            info_text += f" (+{item['base_ac']} AC)"
        elif item['type'] in ('ring', 'necklace') and item.get('ability_bonus'):
            bonuses = ", ".join(f"+{v} {k[:3].upper()}" for k, v in item['ability_bonus'].items())
            info_text += f" ({bonuses})"
        elif item['type'] == 'consumable' and item.get('effect', '').startswith('heal_'):
            info_text += f" (Heals {item['effect'][len('heal_'):]})"
        return info_text

    def _build_quest_tab(self, notebook: ttk.Notebook, player: Any, merchant: Any, quest_board: Any,
                          merchant_window: tk.Toplevel, on_close: Optional[Callable]):
        """Quest board tab: each quest is a short D&D-flavored errand,
        resolved immediately as a single ability check against a DC."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Quests")

        ttk.Label(
            frame, text=f"{player.name} - Level {player.level}",
            font=scaled_font(self, 11, 'Arial', 'bold')
        ).pack(anchor='w', padx=5, pady=(5, 0))

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for quest in quest_board.quests:
            quest_frame = ttk.LabelFrame(scrollable_frame, text=quest['title'], padding=8)
            quest_frame.pack(fill='x', padx=5, pady=4)

            ttk.Label(quest_frame, text=quest['description'], wraplength=380, justify='left').pack(anchor='w')
            ttk.Label(
                quest_frame,
                text=f"{quest['ability'].capitalize()} check, DC {quest['dc']} - "
                     f"Reward: {quest['reward_copper']} copper, {quest['reward_xp']} XP"
            ).pack(anchor='w', pady=(4, 6))

            completed = quest_board.is_completed(quest)
            attempt_button = ttk.Button(
                quest_frame,
                text="Already Attempted" if completed else "Attempt",
                command=lambda q=quest: self._handle_quest_attempt(
                    player, merchant, quest_board, q, merchant_window, on_close)
            )
            attempt_button.pack(anchor='e')
            if completed:
                attempt_button.config(state='disabled')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _handle_quest_attempt(self, player: Any, merchant: Any, quest_board: Any, quest: Dict,
                              merchant_window: tk.Toplevel, on_close: Optional[Callable]):
        result = quest_board.attempt(player, quest)
        self.update_stats_view(player)

        merchant_window.grab_release()
        self.master.focus_force()
        merchant_window.destroy()
        self.show_merchant_ui(player, merchant, on_close, quest_board)

        outcome = "Success!" if result['success'] else "Failure."
        detail = (
            f"Roll: {result['roll']} + {result['modifier']} = {result['total']} vs DC {quest['dc']}\n\n"
            f"{result['text']}"
        )
        if result['success']:
            detail += f"\n\nReward: {result['copper']} copper, {result['xp']} XP"
        messagebox.showinfo(f"{quest['title']} - {outcome}", detail)

    def show_merchant_ui(self, player: Any, merchant: Any, on_close: Optional[Callable] = None,
                         quest_board: Any = None):
        """
        Show the merchant user interface, with a Quests tab alongside the
        goods tabs when a settlement QuestBoard is provided.
        """
        merchant_window = tk.Toplevel(self)
        merchant_window.title("Merchant")
        merchant_window.transient(self)
        fit_window(merchant_window, 800, 600, parent=self.master)
        merchant_window.grab_set()

        def on_closing():
            merchant_window.grab_release()
            self.master.focus_force()
            if on_close:
                on_close()
            merchant_window.destroy()

        merchant_window.protocol("WM_DELETE_WINDOW", on_closing)

        container = ttk.Frame(merchant_window)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        goods_label = "Merchant's Goods & Quests" if quest_board else "Merchant's Goods"
        merchant_frame = ttk.LabelFrame(container, text=goods_label, padding=10)
        merchant_frame.pack(side='left', fill='both', expand=True)

        item_notebook = ttk.Notebook(merchant_frame)
        item_notebook.pack(fill='both', expand=True)

        if quest_board:
            self._build_quest_tab(item_notebook, player, merchant, quest_board, merchant_window, on_close)

        item_types = merchant.get_available_types()

        for item_type in item_types:
            frame = ttk.Frame(item_notebook)
            item_notebook.add(frame, text=item_type.capitalize())

            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            items = merchant.get_inventory_by_type(item_type)
            for item in items:
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill='x', pady=2)

                info_text = self._describe_item(item)
                ttk.Label(item_frame, text=info_text).pack(side='left')
                ttk.Label(item_frame, text=f"{item['price_copper']} copper").pack(side='left', padx=10)

                buy_button = ttk.Button(
                    item_frame,
                    text="Buy",
                    command=lambda i=item: self._handle_buy(player, merchant, i, merchant_window, on_close,
                                                            quest_board)
                )
                buy_button.pack(side='right')

                if player.money < item['price_copper']:
                    buy_button.config(state='disabled')

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        player_frame = ttk.LabelFrame(container, text="Your Inventory", padding=10)
        player_frame.pack(side='right', fill='both', expand=True)

        money_frame = ttk.Frame(player_frame)
        money_frame.pack(fill='x', pady=5)
        ttk.Label(money_frame, text="Your Money:", font=scaled_font(self, 10, 'Arial', 'bold')).pack(side='left')
        ttk.Label(money_frame, text=f"{player.money} copper").pack(side='left', padx=5)

        canvas = tk.Canvas(player_frame)
        scrollbar = ttk.Scrollbar(player_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for item in player.inventory:
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill='x', pady=2)

            sell_value = merchant.get_item_value(item)
            ttk.Label(item_frame, text=f"{item['name']} (Sell: {sell_value} copper)").pack(side='left')

            ttk.Button(
                item_frame,
                text="Sell",
                command=lambda i=item: self._handle_sell(player, merchant, i, merchant_window, on_close,
                                                         quest_board)
            ).pack(side='right')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(merchant_window, text="Close", command=on_closing).pack(pady=10)

    def _handle_inventory_click(self, event):
        """
        Handle inventory click event.
        """
        selection = self._inventory_list.curselection()
        if not selection:
            return

        index = selection[0]
        item_name = self._inventory_list.get(index)

        popup = tk.Menu(self, tearoff=0)

        selected_item = None
        player = self.master._player
        for item in player.inventory:
            if item['name'] == item_name.split(' (')[0]:
                selected_item = item
                break

        if selected_item:
            if selected_item['type'] == 'consumable':
                popup.add_command(
                    label="Use",
                    command=lambda: self._use_item(player, selected_item, None)
                )
            elif selected_item['type'] in ('weapon', 'ranged', 'armor', 'shield', 'ring', 'necklace'):
                popup.add_command(
                    label="Equip",
                    command=lambda: self._equip_item(player, selected_item, None)
                )

            popup.tk_popup(event.x_root, event.y_root)
            popup.grab_release()

    def _equip_item(self, player: Any, item: Dict, window: Optional[tk.Toplevel]):
        """
        Handle equipping items.
        """
        if player.equip_item(item):
            self.update_stats_view(player)
            if window:
                window.grab_release()
                self.master.focus_force()
                window.destroy()
                self.show_inventory_ui(player)

    def _use_item(self, player: Any, item: Dict, window: Optional[tk.Toplevel]):
        """
        Handle using items.
        """
        if item['type'] == 'consumable' and player.use_healing_potion(item):
            self.update_stats_view(player)
            if window:
                window.grab_release()
                self.master.focus_force()
                window.destroy()
                self.show_inventory_ui(player)

    def _handle_buy(self, player: Any, merchant: Any, item: Dict, window: tk.Toplevel,
                     on_close: Optional[Callable], quest_board: Any = None):
        """
        Handle buying items from the merchant.
        """
        if player.money < item['price_copper']:
            messagebox.showwarning("Cannot Buy", "You don't have enough money!")
            return

        if merchant.buy_item(player, item['name']):
            self.update_stats_view(player)
            window.grab_release()
            self.master.focus_force()
            window.destroy()
            self.show_merchant_ui(player, merchant, on_close, quest_board)
            messagebox.showinfo("Purchase Successful", f"You bought {item['name']}!")
        else:
            messagebox.showerror("Error", "Failed to complete purchase!")

    def _handle_sell(self, player: Any, merchant: Any, item: Dict, window: tk.Toplevel,
                      on_close: Optional[Callable], quest_board: Any = None):
        """
        Handle selling items to the merchant.
        """
        sell_confirmation = messagebox.askyesno(
            "Confirm Sale",
            f"Are you sure you want to sell {item['name']} for {merchant.get_item_value(item)} copper?"
        )
        if not sell_confirmation:
            return

        if merchant.sell_item(player, item):
            self.update_stats_view(player)
            window.grab_release()
            self.master.focus_force()
            window.destroy()
            self.show_merchant_ui(player, merchant, on_close, quest_board)
            messagebox.showinfo("Sale Successful", f"You sold {item['name']}!")
        else:
            messagebox.showerror("Error", "Failed to complete sale!")
