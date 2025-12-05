# wanderingMonster.py
# Wandering monsters module for the Adventure Game


from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional
import pygame
import os

pygame.init()

# ----- Global Image Variables -----
Gnome_img: pygame.Surface | None = None
Troll_img: pygame.Surface | None = None
Imp_img: pygame.Surface | None = None

MEDIA_FOLDER = "combat_media"
DEFAULT_TILE_SIZE = 32

# ----- Image Loading Functions -----
def load_monster_images(tile_size: int = DEFAULT_TILE_SIZE) -> None:
    """Load and scale monster images."""
    global Gnome_img, Troll_img, Imp_img
    try:
        Gnome_img = pygame.image.load(os.path.join(MEDIA_FOLDER, "DarkTroll.png")).convert_alpha()
        Troll_img = pygame.image.load(os.path.join(MEDIA_FOLDER, "Beast.png")).convert_alpha()
        Imp_img   = pygame.image.load(os.path.join(MEDIA_FOLDER, "Devil.png")).convert_alpha()

        # Scale images to tile size
        Gnome_img = pygame.transform.scale(Gnome_img, (tile_size, tile_size))
        Troll_img = pygame.transform.scale(Troll_img, (tile_size, tile_size))
        Imp_img   = pygame.transform.scale(Imp_img, (tile_size, tile_size))

        print("Monster images loaded successfully!")
    except FileNotFoundError:
        print("Monster images not found in 'combat_media' folder.")
        Gnome_img = Troll_img = Imp_img = None

# ----- Monster Stats -----
GridPos = Tuple[int, int]
TYPE_STATS: Dict[str, Dict[str, Tuple[int,int]]] = {
    "Gnome": {"health_range": (20,40), "power_range": (5,10), "money_range": (10,50)},
    "Imp":   {"health_range": (10,25), "power_range": (8,15), "money_range": (20,100)},
    "Troll": {"health_range": (30,50), "power_range": (10,18), "money_range": (30,80)},
}

# ----- Monster Dataclass -----
@dataclass
class Monster:
    name: str
    mtype: str
    pos: GridPos
    health: int
    power: int
    money: int
    alive: bool = True

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "mtype": self.mtype,
            "pos": list(self.pos),
            "health": self.health,
            "power": self.power,
            "money": self.money,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Monster":
        mtype = data.get("mtype", "Gnome")
        return cls(
            name=data.get("name", mtype),
            mtype=mtype,
            pos=tuple(data.get("pos", (0,0))),
            health=int(data.get("health", 20)),
            power=int(data.get("power", 5)),
            money=int(data.get("money", 10)),
            alive=bool(data.get("alive", True)),
        )

    @staticmethod
    def create_random(grid_size: int, town_pos: GridPos, avoid: Optional[set]=None) -> "Monster":
        avoid = avoid or set()
        mtype = random.choice(list(TYPE_STATS.keys()))
        stats = TYPE_STATS[mtype]
        health = random.randint(*stats["health_range"])
        power  = random.randint(*stats["power_range"])
        money  = random.randint(*stats["money_range"])
        while True:
            pos = (random.randint(0, grid_size-1), random.randint(0, grid_size-1))
            if pos != town_pos and pos not in avoid:
                break
        return Monster(name=mtype, mtype=mtype, pos=pos, health=health, power=power, money=money)

    def move(self, dx: int, dy: int, grid_size: int, town_pos: GridPos) -> bool:
        if not self.alive:
            return False
        new_pos = (self.pos[0]+dx, self.pos[1]+dy)
        x, y = new_pos
        if 0 <= x < grid_size and 0 <= y < grid_size and new_pos != town_pos:
            self.pos = new_pos
            return True
        return False

    def random_move(self, grid_size: int, town_pos: GridPos) -> bool:
        if not self.alive:
            return False
        directions = [(0,-1),(0,1),(-1,0),(1,0)]
        random.shuffle(directions)
        for dx, dy in directions:
            if self.move(dx, dy, grid_size, town_pos):
                return True
        return False

# ----- Utility Functions -----
def monsters_from_state(state_list: List[Dict]) -> List[Monster]:
    return [Monster.from_dict(d) for d in state_list]

def monsters_to_state(monsters: List[Monster]) -> List[Dict]:
    return [m.to_dict() for m in monsters]

def ensure_two_monsters(monsters: List[Monster], grid_size: int, town_pos: GridPos, player_pos: GridPos) -> List[Monster]:
    if monsters:
        return monsters
    avoid = {town_pos, player_pos}
    m1 = Monster.create_random(grid_size, town_pos, avoid=avoid)
    avoid.add(m1.pos)
    m2 = Monster.create_random(grid_size, town_pos, avoid=avoid)
    return [m1, m2]

def move_monsters_every_other(monsters: List[Monster], grid_size: int, town_pos: GridPos, player_move_count: int) -> None:
    if player_move_count % 2 == 0:
        for m in monsters:
            m.random_move(grid_size, town_pos)

def collision_index(monsters: List[Monster], player_pos: GridPos) -> Optional[int]:
    for i, m in enumerate(monsters):
        if m.pos == player_pos and m.alive:
            return i
    return None

# ----- Draw Monsters -----
def draw_monsters(surface: pygame.Surface, monsters: List[Monster], tile_size: int) -> None:
    for m in monsters:
        if not m.alive:
            continue
        mx, my = m.pos
        cx, cy = mx * tile_size, my * tile_size
        img: pygame.Surface | None = None
        if m.mtype == "Gnome":
            img = Gnome_img
        elif m.mtype == "Troll":
            img = Troll_img
        elif m.mtype == "Imp":
            img = Imp_img
        if img:
            rect = img.get_rect()
            rect.topleft = (cx, cy)
            surface.blit(img, rect)  # <- THIS LINE WAS MISSING BEFORE

