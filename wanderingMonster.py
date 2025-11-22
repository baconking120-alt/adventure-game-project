# wanderingMonster.py
# Wandering monsters module for the Adventure Game
# - Monster class with movement and serialization
# - Utilities for spawning, movement timing (every other player move), collisions, and respawn

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional

GridPos = Tuple[int, int]
Color = Tuple[int, int, int]

# Distinct colors per type (for clear visual differentiation on the grid)
TYPE_COLORS: Dict[str, Color] = {
    "Gnome": (255, 165, 0),    # orange
    "Imp":   (200, 0, 0),      # red
    "Ghoul": (160, 32, 240),   # purple
}

# Stat ranges per type (health, power, money)
TYPE_STATS: Dict[str, Dict[str, Tuple[int, int]]] = {
    "Gnome": {"health_range": (20, 40), "power_range": (5, 10),  "money_range": (10, 50)},
    "Imp":   {"health_range": (10, 25), "power_range": (8, 15),  "money_range": (20, 100)},
    "Ghoul": {"health_range": (60, 100),"power_range": (15, 25), "money_range": (50, 200)},
}

@dataclass
class Monster:
    """A wandering monster that moves on the grid and can be serialized to persist map state."""
    name: str
    mtype: str
    pos: GridPos
    color: Color
    health: int
    power: int
    money: int
    alive: bool = True

    # ----- Serialization -----
    def to_dict(self) -> Dict:
        """Convert to JSON-friendly dict (tuples -> lists)."""
        return {
            "name": self.name,
            "mtype": self.mtype,
            "pos": list(self.pos),
            "color": list(self.color),
            "health": self.health,
            "power": self.power,
            "money": self.money,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        """Build Monster from a saved dict."""
        mtype = data.get("mtype", "Gnome")
        return cls(
            name=data.get("name", mtype),
            mtype=mtype,
            pos=tuple(data.get("pos", (0, 0))),
            color=tuple(data.get("color", TYPE_COLORS.get(mtype, (200, 0, 0)))),
            health=int(data.get("health", 20)),
            power=int(data.get("power", 5)),
            money=int(data.get("money", 10)),
            alive=bool(data.get("alive", True)),
        )

    # ----- Random creation -----
    @staticmethod
    def create_random(grid_size: int, town_pos: GridPos, avoid: Optional[set] = None) -> "Monster":
        """Create a random monster of random type at a valid position (not in avoid set and not town)."""
        avoid = avoid or set()
        mtype = random.choice(list(TYPE_STATS.keys()))
        stats = TYPE_STATS[mtype]
        health = random.randint(*stats["health_range"])
        power  = random.randint(*stats["power_range"])
        money  = random.randint(*stats["money_range"])
        color  = TYPE_COLORS.get(mtype, (200, 0, 0))

        # Pick a valid position
        while True:
            pos = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
            if pos == town_pos or pos in avoid:
                continue
            break

        return Monster(name=mtype, mtype=mtype, pos=pos, color=color, health=health, power=power, money=money)

    # ----- Movement -----
    def _can_move_to(self, new_pos: GridPos, grid_size: int, town_pos: GridPos) -> bool:
        x, y = new_pos
        if x < 0 or x >= grid_size or y < 0 or y >= grid_size:
            return False
        if new_pos == town_pos:
            return False
        return True

    def move(self, dx: int, dy: int, grid_size: int, town_pos: GridPos) -> bool:
        """Attempt to move by (dx, dy). Returns True if moved. Monsters cannot enter town or leave the grid."""
        if not self.alive:
            return False
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)
        if self._can_move_to(new_pos, grid_size, town_pos):
            self.pos = new_pos
            return True
        return False

    def random_move(self, grid_size: int, town_pos: GridPos) -> bool:
        """Try up to four directions randomly; move if any is valid."""
        if not self.alive:
            return False
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            if self.move(dx, dy, grid_size, town_pos):
                return True
        return False

# ----- Compatibility helper (if any code still calls new_random_monster) -----
def new_random_monster(grid_size: int, town_pos: GridPos, avoid: Optional[set] = None) -> Dict:
    """Return a dict like your old new_random_monster(), but using Monster.create_random."""
    m = Monster.create_random(grid_size, town_pos, avoid)
    return {
        "name": m.name,
        "description": f"A {m.mtype} approaches!",
        "health": m.health,
        "power": m.power,
        "money": m.money,
        # color not used by old function, but available in Monster class
    }

# ----- Utility functions for game.py integration -----
def monsters_from_state(state_list: List[Dict]) -> List[Monster]:
    """Deserialize a list of monster dicts from map_state into Monster objects."""
    return [Monster.from_dict(d) for d in state_list]

def monsters_to_state(monsters: List[Monster]) -> List[Dict]:
    """Serialize Monster objects to dicts for saving in map_state."""
    return [m.to_dict() for m in monsters]

def ensure_two_monsters(monsters: List[Monster], grid_size: int, town_pos: GridPos, player_pos: GridPos) -> List[Monster]:
    """If there are no monsters, spawn two (not on town or player)."""
    if monsters:
        return monsters
    avoid = {town_pos, player_pos}
    m1 = Monster.create_random(grid_size, town_pos, avoid=avoid)
    avoid.add(m1.pos)
    m2 = Monster.create_random(grid_size, town_pos, avoid=avoid)
    return [m1, m2]

def move_monsters_every_other(monsters: List[Monster], grid_size: int, town_pos: GridPos, player_move_count: int) -> None:
    """Move all monsters once when player_move_count is even (every other player move)."""
    if player_move_count % 2 == 0:
        for m in monsters:
            m.random_move(grid_size, town_pos)

def collision_index(monsters: List[Monster], player_pos: GridPos) -> Optional[int]:
    """Return index of monster occupying the player's tile, or None if no collision."""
    for i, m in enumerate(monsters):
        if m.pos == player_pos and m.alive:
            return i
    return None

def respawn_if_cleared(monsters: List[Monster], grid_size: int, town_pos: GridPos, player_pos: GridPos) -> List[Monster]:
    """If no monsters remain, spawn two new ones."""
    alive_monsters = [m for m in monsters if m.alive]
    if alive_monsters:
        return monsters
    return ensure_two_monsters([], grid_size, town_pos, player_pos)

# Optional: a small helper to draw monsters (if you want to move drawing into this module)
def draw_monsters(surface, monsters: List[Monster], tile_size: int) -> None:
    """Draw each monster as a colored circle at its grid position."""
    import pygame  # local import to keep module lightweight if pygame isn't always used
    for m in monsters:
        mx, my = m.pos
        cx = mx * tile_size + tile_size // 2
        cy = my * tile_size + tile_size // 2
        pygame.draw.circle(surface, m.color, (cx, cy), tile_size // 3)
