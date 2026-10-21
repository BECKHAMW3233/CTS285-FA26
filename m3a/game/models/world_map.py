import random
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Set
import logging
from database import Database

NODE_KINDS = ('start', 'village', 'town', 'dungeon', 'encounter', 'empty')
TERRAIN_TYPES = ('plains', 'forest', 'water', 'road')


@dataclass
class WorldNode:
    """
    A single location on the overworld map. 'kind' is what's there (a
    settlement, a dungeon, nothing); 'terrain' is what the ground looks
    like and, for water, whether you can walk on it at all. 'dungeon' and
    'encounter' nodes carry a tier that scales with distance from the start.
    """
    kind: str = 'empty'
    terrain: str = 'plains'
    tier: int = 1
    visited: bool = False
    cleared: bool = False
    scouted: bool = False
    doors: Dict[str, bool] = field(default_factory=lambda: {
        'north': False, 'south': False, 'east': False, 'west': False
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            'kind': self.kind,
            'terrain': self.terrain,
            'tier': self.tier,
            'visited': self.visited,
            'cleared': self.cleared,
            'scouted': self.scouted,
            'doors': self.doors,
        }


class WorldMap:
    """
    The overworld: a large, fully-open grid (walk any direction, no maze
    walls) dotted with villages, towns, dungeons, and random encounters,
    with water as the one real obstacle and forests/roads for texture.
    Entering a settlement opens the merchant/rest hub, entering a 'dungeon'
    node launches a Dungeon instance at that node's tier, and entering an
    'encounter' node triggers a random world encounter.
    """
    def __init__(self, size: int = 500, player_pos: tuple = None, nodes: list = None):
        self._size = size
        self._db = Database()

        if isinstance(player_pos, (list, tuple)):
            self._player_pos = (player_pos[0], player_pos[1])
        else:
            self._player_pos = (0, 0)

        if nodes:
            self._load_nodes(nodes)
        else:
            self._nodes = [[WorldNode() for _ in range(size)] for _ in range(size)]
            self._generate_world()

        logging.info(f"Generated world map of size {size}x{size} ({size * size} tiles)")

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------
    @property
    def size(self) -> int:
        return self._size

    @property
    def nodes(self) -> List[List[WorldNode]]:
        return self._nodes

    @property
    def player_pos(self) -> Tuple[int, int]:
        return self._player_pos

    def _load_nodes(self, nodes_data: List[List[Dict]]) -> None:
        self._nodes = []
        for row in nodes_data:
            node_row = []
            for node_data in row:
                node_row.append(WorldNode(
                    kind=node_data.get('kind', 'empty'),
                    terrain=node_data.get('terrain', 'plains'),
                    tier=node_data.get('tier', 1),
                    visited=node_data.get('visited', False),
                    cleared=node_data.get('cleared', False),
                    scouted=node_data.get('scouted', False),
                    doors=node_data.get('doors', {'north': False, 'south': False, 'east': False, 'west': False}),
                ))
            self._nodes.append(node_row)

    def _generate_world(self) -> None:
        """
        Connect the overworld as open ground, lay down water/forest terrain,
        scatter villages, towns, dungeons, and random encounters, then run
        roads between the settlements.
        """
        self._connect_open_grid()
        self._generate_terrain()
        self._nodes[0][0].kind = 'start'
        self._nodes[0][0].terrain = 'plains'
        self._nodes[0][0].visited = True

        max_tier = self._db.get_max_enemy_tier()
        open_nodes = [
            (x, y) for x in range(self._size) for y in range(self._size)
            if (x, y) != (0, 0) and self._nodes[y][x].terrain != 'water'
        ]
        random.shuffle(open_nodes)

        # Divisor scaled to map size, not a flat 3 - that was tuned for the
        # original 32x32 map, where tier 8 (max) kicked in at distance 21,
        # most of the way across. Left flat, it still maxes out at distance
        # 21 on a 500x500 map - under 5% of the way across - putting tier 8
        # enemies almost everywhere beyond a tiny bubble around spawn.
        # Scaling it with size preserves the original ~34%-of-the-map
        # distance-to-max-tier curve at any map size.
        distance_divisor = max(1, self._size * 3 // 32)

        def distance_tier(x: int, y: int) -> int:
            distance = abs(x - self._player_pos[0]) + abs(y - self._player_pos[1])
            return max(1, min(max_tier, 1 + distance // distance_divisor))

        # Scaled by tile AREA (size*size), not just the side length - a
        # 500x500 map has 244x the tiles a 32x32 one does, and counts need
        # to keep pace with that or the world gets sparser as it gets
        # bigger instead of just bigger. Ratios preserve the exact density
        # the original 32x32 map shipped with (8/5/10/32 per 1024 tiles).
        area = self._size * self._size
        num_villages = max(6, area * 8 // 1024)
        num_towns = max(4, area * 5 // 1024)
        num_dungeons = max(8, area * 10 // 1024)
        num_encounters = max(20, area * 32 // 1024)

        settlements = [(0, 0)]

        for _ in range(num_villages):
            if open_nodes:
                x, y = open_nodes.pop()
                self._nodes[y][x].kind = 'village'
                settlements.append((x, y))

        for _ in range(num_towns):
            if open_nodes:
                x, y = open_nodes.pop()
                self._nodes[y][x].kind = 'town'
                settlements.append((x, y))

        for _ in range(num_dungeons):
            if open_nodes:
                x, y = open_nodes.pop()
                self._nodes[y][x].kind = 'dungeon'
                self._nodes[y][x].tier = distance_tier(x, y)

        for _ in range(num_encounters):
            if open_nodes:
                x, y = open_nodes.pop()
                self._nodes[y][x].kind = 'encounter'
                self._nodes[y][x].tier = distance_tier(x, y)

        # Remaining open_nodes stay 'empty' - just open plains/forest.

        self._generate_roads(settlements)

    def _connect_open_grid(self) -> None:
        """
        An overworld is open country, not a corridor maze: connect every
        pair of adjacent tiles so the player can walk freely in any
        direction (water tiles are blocked separately, in move_player) -
        unlike Dungeon's single-path maze carve, which is deliberately a
        maze because dungeons are enclosed spaces.
        """
        deltas = [(0, 1, 'south', 'north'), (0, -1, 'north', 'south'),
                  (1, 0, 'east', 'west'), (-1, 0, 'west', 'east')]
        for y in range(self._size):
            for x in range(self._size):
                for dx, dy, dir1, dir2 in deltas:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < self._size and 0 <= new_y < self._size:
                        self._nodes[y][x].doors[dir1] = True
                        self._nodes[new_y][new_x].doors[dir2] = True

    def _grow_blob(self, seed: Tuple[int, int], target_size: int) -> Set[Tuple[int, int]]:
        """Random-walk a cluster of tiles outward from a seed point (cheap
        stand-in for noise-based terrain generation)."""
        blob = {seed}
        frontier = [seed]
        while len(blob) < target_size and frontier:
            cx, cy = frontier.pop(random.randrange(len(frontier)))
            neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if (0 <= nx < self._size and 0 <= ny < self._size and
                        (nx, ny) not in blob and (nx, ny) != (0, 0)):
                    blob.add((nx, ny))
                    frontier.append((nx, ny))
                    if len(blob) >= target_size:
                        break
        return blob

    def _generate_terrain(self) -> None:
        """Lay down a few lakes and forests as grown blobs; everything else
        stays open plains."""
        num_lakes = max(4, self._size // 7)
        num_forests = max(6, self._size // 5)

        for _ in range(num_lakes):
            seed = (random.randrange(self._size), random.randrange(self._size))
            if seed == (0, 0):
                continue
            for x, y in self._grow_blob(seed, random.randint(10, 35)):
                self._nodes[y][x].terrain = 'water'

        for _ in range(num_forests):
            seed = (random.randrange(self._size), random.randrange(self._size))
            if seed == (0, 0):
                continue
            for x, y in self._grow_blob(seed, random.randint(20, 60)):
                if self._nodes[y][x].terrain != 'water':
                    self._nodes[y][x].terrain = 'forest'

        self._ensure_land_connectivity()

    def _ensure_land_connectivity(self) -> None:
        """
        _connect_open_grid() makes every tile topologically adjacent, but
        water is a separate movement-time obstacle (checked in move_player)
        - nothing guarantees the lakes we just grew don't fully enclose the
        start tile. Flood-fill from (0, 0) treating water as a wall; if
        that leaves too much of the map unreachable, drain the water
        outside the reachable region back to plains instead of leaving the
        player potentially trapped at spawn.
        """
        reachable = set()
        frontier = deque([(0, 0)])
        reachable.add((0, 0))
        while frontier:
            x, y = frontier.popleft()
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if (0 <= nx < self._size and 0 <= ny < self._size and (nx, ny) not in reachable
                        and self._nodes[ny][nx].terrain != 'water'):
                    reachable.add((nx, ny))
                    frontier.append((nx, ny))

        total = self._size * self._size
        if len(reachable) >= total * 0.6:
            return

        logging.warning(
            f"World map generation trapped the start tile behind water "
            f"({len(reachable)}/{total} tiles reachable) - draining unreachable water to plains"
        )
        for y in range(self._size):
            for x in range(self._size):
                if (x, y) not in reachable and self._nodes[y][x].terrain == 'water':
                    self._nodes[y][x].terrain = 'plains'

    def _generate_roads(self, settlements: List[Tuple[int, int]]) -> None:
        """Run a road (avoiding water) from each settlement to its nearest
        neighboring settlement, so towns/villages read as connected."""
        for i, pos in enumerate(settlements):
            others = [p for j, p in enumerate(settlements) if j != i]
            if not others:
                continue
            nearest = min(others, key=lambda p: abs(p[0] - pos[0]) + abs(p[1] - pos[1]))
            for x, y in self._walkable_path(pos, nearest):
                if self._nodes[y][x].terrain != 'water':
                    self._nodes[y][x].terrain = 'road'

    def _walkable_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """BFS shortest path between two points, treating water as a wall."""
        visited = {start}
        queue = deque([(start, [start])])
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == target:
                return path
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if (0 <= nx < self._size and 0 <= ny < self._size and (nx, ny) not in visited
                        and self._nodes[ny][nx].terrain != 'water'):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return []

    def move_player(self, direction: str) -> bool:
        """
        Move the player one tile in the given direction, if a path exists
        and the destination isn't water.
        """
        current = self.get_current_node()
        if not current.doors[direction]:
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
            if self._nodes[new_y][new_x].terrain == 'water':
                return False
            self._player_pos = (new_x, new_y)
            self._nodes[new_y][new_x].visited = True
            logging.info(f"Player moved on world map to {self._player_pos}")
            return True
        return False

    def get_current_node(self) -> WorldNode:
        return self._nodes[self._player_pos[1]][self._player_pos[0]]

    def roll_encounter_is_fight(self) -> bool:
        """Random world encounters are a fight about half the time, otherwise a flavor event."""
        return random.random() < 0.5

    def scout_nearby(self, radius: int = 3) -> List[WorldNode]:
        """
        Reveal the tier of any not-yet-resolved encounter ('?') tiles within
        `radius` tiles of the player, without having to walk onto them.
        Returns the newly-scouted nodes (empty if there was nothing to find).
        """
        px, py = self._player_pos
        found = []
        for y in range(max(0, py - radius), min(self._size, py + radius + 1)):
            for x in range(max(0, px - radius), min(self._size, px + radius + 1)):
                node = self._nodes[y][x]
                if node.kind == 'encounter' and not node.cleared and not node.scouted:
                    node.scouted = True
                    found.append(node)
        return found

    def to_dict(self) -> Dict[str, Any]:
        return {
            'size': self._size,
            'player_pos': self._player_pos,
            'nodes': [[node.to_dict() for node in row] for row in self._nodes],
        }
