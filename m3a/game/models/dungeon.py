import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
import logging
from database import Database
from models.enemy import Enemy
from config import ENEMY_SPAWN_CHANCE, VISIBLE_RANGE


@dataclass
class Room:
    """
    Represents a single room in the dungeon.
    """
    enemies: List[Enemy] = field(default_factory=list)
    items: List[Dict] = field(default_factory=list)
    is_cleared: bool = False
    is_visible: bool = False
    has_merchant: bool = False
    merchant_visited: bool = False
    has_treasure: bool = False
    treasure_looted: bool = False
    is_end_room: bool = False
    is_locked: bool = False
    boss_defeated: bool = False
    doors: Dict[str, bool] = field(default_factory=lambda: {
        'north': False, 'south': False, 'east': False, 'west': False
    })

    def has_enemy(self) -> bool:
        """
        Check if the room has any enemies.

        Returns:
            True if the room has enemies, False otherwise.
        """
        return len(self.enemies) > 0

    def get_enemy(self) -> Optional[Enemy]:
        """
        Get the first enemy in the room.

        Returns:
            The first enemy in the room, or None if no enemies.
        """
        return self.enemies[0] if self.enemies else None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the room to a dictionary for saving.

        Returns:
            The room data as a dictionary.
        """
        return {
            'enemies': [enemy.to_dict() for enemy in self.enemies],
            'items': self.items,
            'is_cleared': self.is_cleared,
            'is_visible': self.is_visible,
            'has_merchant': self.has_merchant,
            'merchant_visited': self.merchant_visited,
            'has_treasure': self.has_treasure,
            'treasure_looted': self.treasure_looted,
            'is_end_room': self.is_end_room,
            'is_locked': self.is_locked,
            'boss_defeated': self.boss_defeated,
            'doors': self.doors
        }


class Dungeon:
    """
    Represents a dungeon. The farthest room from the entrance is a locked vault
    guarded by that tier's boss - find Thieves' Tools to get in.
    """
    def __init__(self, tier: int, size: int = 10, player_pos: tuple = None, rooms: list = None):
        """
        Initialize the dungeon.

        Args:
            tier: The dungeon tier.
            size: The size of the dungeon.
            player_pos: The initial player position.
            rooms: The list of rooms in the dungeon.
        """
        self._tier = tier
        self._size = size
        self._db = Database()
        self.view_range = VISIBLE_RANGE

        if isinstance(player_pos, (list, tuple)):
            self._player_pos = (player_pos[0], player_pos[1])
        else:
            self._player_pos = (0, 0)

        if rooms:
            self._load_rooms(rooms)
        else:
            self._rooms = [[Room() for _ in range(size)] for _ in range(size)]
            self._generate_dungeon()

        logging.info(f"Generated tier {tier} dungeon of size {size}x{size}")

    # ------------------------------------------------------------------
    # Public accessors (the GUI reads these directly)
    # ------------------------------------------------------------------
    @property
    def tier(self) -> int:
        return self._tier

    @property
    def size(self) -> int:
        return self._size

    @property
    def rooms(self) -> List[List[Room]]:
        return self._rooms

    @property
    def player_pos(self) -> Tuple[int, int]:
        return self._player_pos

    def _load_rooms(self, rooms_data: List[List[Dict]]) -> None:
        """
        Load rooms from saved data.

        Args:
            rooms_data: The saved room data.
        """
        self._rooms = []
        for row in rooms_data:
            room_row = []
            for room_data in row:
                enemies = []
                for enemy_data in room_data.get('enemies', []):
                    if isinstance(enemy_data, dict):
                        try:
                            enemy = Enemy(**enemy_data)
                            enemies.append(enemy)
                        except Exception as e:
                            logging.error(f"Error creating enemy: {str(e)}")
                            continue

                room = Room(
                    enemies=enemies,
                    items=room_data.get('items', []),
                    is_cleared=room_data.get('is_cleared', False),
                    is_visible=room_data.get('is_visible', False),
                    has_merchant=room_data.get('has_merchant', False),
                    merchant_visited=room_data.get('merchant_visited', False),
                    has_treasure=room_data.get('has_treasure', False),
                    treasure_looted=room_data.get('treasure_looted', False),
                    is_end_room=room_data.get('is_end_room', False),
                    is_locked=room_data.get('is_locked', False),
                    boss_defeated=room_data.get('boss_defeated', False),
                    doors=room_data.get('doors', {'north': False, 'south': False, 'east': False, 'west': False})
                )
                room_row.append(room)
            self._rooms.append(room_row)

    def _generate_dungeon(self) -> None:
        """
        Generate the complete dungeon with rooms, enemies, treasure, a merchant,
        and a locked vault guarded by the tier boss.
        """
        self._generate_maze()
        self._populate_rooms()
        self._place_treasure_rooms()
        self._place_merchant()
        self._place_vault_room()
        self._rooms[0][0].is_visible = True
        self._update_visibility()

    def _generate_maze(self) -> None:
        """
        Generate the maze layout of the dungeon.
        """
        def carve_path(x: int, y: int, visited: set):
            visited.add((x, y))
            directions = [(0, 1, 'south', 'north'), (0, -1, 'north', 'south'),
                          (1, 0, 'east', 'west'), (-1, 0, 'west', 'east')]
            random.shuffle(directions)

            for dx, dy, dir1, dir2 in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self._size and 0 <= new_y < self._size and
                        (new_x, new_y) not in visited):
                    self._rooms[y][x].doors[dir1] = True
                    self._rooms[new_y][new_x].doors[dir2] = True
                    carve_path(new_x, new_y, visited)

        carve_path(0, 0, set())

    def _populate_rooms(self) -> None:
        """
        Populate rooms with enemies.
        """
        enemies = self._db.get_all_enemies_by_tier(self._tier)

        if not enemies:
            logging.error(f"No enemies found for tier {self._tier}")
            return

        for y in range(self._size):
            for x in range(self._size):
                if random.random() < ENEMY_SPAWN_CHANCE and (x, y) != (0, 0):
                    enemy = Enemy.get_random_enemy(self._tier)
                    self._rooms[y][x].enemies.append(enemy)

    def _place_treasure_rooms(self) -> None:
        """
        Place treasure rooms in the dungeon.
        """
        num_treasures = random.randint(1, self._tier)

        empty_rooms = [
            (x, y) for x in range(self._size) for y in range(self._size)
            if (x, y) != (0, 0) and not self._rooms[y][x].enemies
        ]

        if empty_rooms:
            for _ in range(num_treasures):
                if not empty_rooms:
                    break
                x, y = empty_rooms.pop(random.randrange(len(empty_rooms)))
                self._rooms[y][x].has_treasure = True
                logging.info(f"Placed treasure room at ({x}, {y})")

    def _place_merchant(self) -> None:
        """
        Place a merchant in the dungeon.
        """
        empty_rooms = [
            (x, y) for x in range(self._size) for y in range(self._size)
            if (x, y) != (0, 0) and not self._rooms[y][x].enemies and not self._rooms[y][x].has_treasure
        ]

        if empty_rooms:
            x, y = random.choice(empty_rooms)
            self._rooms[y][x].has_merchant = True
            logging.info(f"Placed merchant at ({x}, {y})")

    def _place_vault_room(self) -> None:
        """
        Place the locked vault (end room) in the farthest room from the entrance.
        It starts locked and enemy-free; the boss spawns only once it's unlocked.
        """
        farthest_room = None
        max_distance = 0

        for y in range(self._size):
            for x in range(self._size):
                distance = abs(x - self._player_pos[0]) + abs(y - self._player_pos[1])
                if distance > max_distance:
                    max_distance = distance
                    farthest_room = (x, y)

        if farthest_room:
            x, y = farthest_room
            room = self._rooms[y][x]
            room.is_end_room = True
            room.is_locked = True
            room.enemies = []  # the boss only appears once the vault is unlocked
            room.has_treasure = False
            room.has_merchant = False
            logging.info(f"Placed locked vault at ({x}, {y})")

    def get_treasure_loot(self) -> List[Tuple[str, Any]]:
        """
        Generate treasure room loot.

        Returns:
            A list of (drop_type, value) tuples: one ('copper', amount), then
            zero or more ('item', item_name) tuples - the same shape every
            caller (main.py, story.py) expects from enemy drops too.
        """
        loot: List[Tuple[str, Any]] = []

        # 800/tier (not the original 100/tier) so a dedicated treasure room
        # actually beats a single kill's copper - at the old rate, fixing
        # enemies.json's copper drops (see 4.1.1) left treasure rooms paying
        # *less* than one average kill at every dungeon tier.
        base_money = 800 * self._tier
        bonus_money = random.randint(0, base_money)
        loot.append(('copper', base_money + bonus_money))

        num_items = random.randint(2, 3 + self._tier)

        max_tier = min(self._tier + 2, self._db.get_max_item_tier())
        items = self._db.get_all_items_by_tier(max_tier)

        if items:
            selected = random.sample(items, k=min(num_items, len(items)))
            loot.extend(('item', item['name']) for item in selected)

        return loot

    def try_unlock_vault(self, player: Any) -> bool:
        """
        Spend a set of Thieves' Tools from the player's inventory to unlock
        the vault room, if the player is standing in it and it's still locked.

        Returns:
            True if the vault was unlocked just now, False otherwise.
        """
        room = self.get_current_room()
        if not (room.is_end_room and room.is_locked):
            return False
        if not player.consume_item_named("Thieves' Tools"):
            return False
        room.is_locked = False
        logging.info("Vault unlocked with Thieves' Tools.")
        return True

    def get_vault_boss(self) -> Enemy:
        """
        Spawn the boss guarding this dungeon tier's vault.
        """
        return Enemy.get_boss(self._tier)

    def move_player(self, direction: str) -> bool:
        """
        Move player in the specified direction.

        Args:
            direction: The direction to move.

        Returns:
            True if the move was successful, False otherwise.
        """
        current_room = self.get_current_room()
        if not current_room.doors[direction]:
            return False

        dx, dy = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }[direction]

        new_x = self._player_pos[0] + dx
        new_y = self._player_pos[1] + dy

        if 0 <= new_x < self._size and 0 <= new_y < self._size:
            self._player_pos = (new_x, new_y)
            self._update_visibility()
            logging.info(f"Player moved to position {self._player_pos}")
            return True
        return False

    def move_player_random_adjacent(self) -> bool:
        """
        Move player to a random adjacent room.

        Returns:
            True if the move was successful, False otherwise.
        """
        current_room = self.get_current_room()
        available_directions = [d for d, has_door in current_room.doors.items() if has_door]

        if not available_directions:
            return False

        direction = random.choice(available_directions)
        return self.move_player(direction)

    def _update_visibility(self) -> None:
        """
        Update room visibility around the player.
        """
        x, y = self._player_pos
        for dy in range(-self.view_range, self.view_range + 1):
            for dx in range(-self.view_range, self.view_range + 1):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self._size and 0 <= new_y < self._size:
                    self._rooms[new_y][new_x].is_visible = True

    def get_current_room(self) -> Room:
        """
        Get the room the player is currently in.

        Returns:
            The current room.
        """
        return self._rooms[self._player_pos[1]][self._player_pos[0]]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dungeon to a dictionary for saving.

        Returns:
            The dungeon data as a dictionary.
        """
        return {
            'tier': self._tier,
            'size': self._size,
            'player_pos': self._player_pos,
            'rooms': [[room.to_dict() for room in row] for row in self._rooms]
        }
