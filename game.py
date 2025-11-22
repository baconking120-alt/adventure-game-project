"""
Main game script that imports and uses functions from gamefunctions.py.

This script demonstrates basic interaction with the player and calls
each of the four required functions from the gamefunctions module.

Typical usage example:

    python game.py
"""


# game.py
# Main game loop

import random
import json
import pygame

from gamefunctions import (
    inventory,
    show_inventory,
    add_to_inventory,
    equip_item,
    use_special_item,
    print_welcome,
    purchase_item,
)

# Import the wandering monster system (matches your file name: wanderingMonster.py)
from wanderingMonster import (
    Monster,
    monsters_from_state,
    monsters_to_state,
    ensure_two_monsters,
    move_monsters_every_other,
    collision_index,
    respawn_if_cleared,
)

SAVE_FILENAME = "savegame.json"

# Map constants
GRID_SIZE = 10
TILE_SIZE = 32
WIDTH = GRID_SIZE * TILE_SIZE
HEIGHT = GRID_SIZE * TILE_SIZE

BG_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)
PLAYER_COLOR = (0, 150, 255)
TOWN_COLOR = (0, 200, 0)

DEFAULT_MAP_STATE = {
    "player_pos": (0, 0),
    "town_pos": (0, 0),
    "monsters": [],          # persistent monsters list (serialized as dicts)
    "visited_town": False,
}

# ---------------- INPUT HELPERS ----------------
def get_valid_input(prompt: str, valid_options: list[str]) -> str:
    while True:
        try:
            choice = input(prompt).strip()
        except EOFError:
            print("\nInput ended. Exiting game.")
            exit()
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting game.")
            exit()
        if choice in valid_options:
            return choice
        print("Invalid choice. Try again.")

# ---------------- SHOP ----------------
def shop_menu(gold: int) -> int:
    items = [
        {"name": "Bread", "price": 20},
        {"name": "Cheese", "price": 15},
        {"name": "Juice",  "price": 5},
        {"name": "Cake",   "price": 12},
        {"name": "Potion", "price": 25},
        {"name": "Elixir", "price": 40},
    ]

    while True:
        print(f"\nWelcome to the shop! You have ${gold}")
        print("Items available:")
        for i, item in enumerate(items, 1):
            print(f"{i}) {item['name']} - ${item['price']}")
        print(f"{len(items)+1}) Leave shop")

        choice = get_valid_input("> ", [str(i) for i in range(1, len(items)+2)])
        choice = int(choice)

        if choice == len(items)+1:
            print("Leaving shop...")
            return gold
        else:
            selected_item = items[choice-1]
            try:
                quantity = int(input(f"How many {selected_item['name']} do you want to buy? "))
            except KeyboardInterrupt:
                print("\nInterrupted. Returning to shop menu.")
                continue
            except ValueError:
                print("Invalid input. Returning to shop menu.")
                continue

            purchased, remaining_gold = purchase_item(selected_item["price"], gold, quantity)
            gold = remaining_gold
            if purchased > 0:
                # add one item entry per purchased unit (simple inventory)
                for _ in range(purchased):
                    add_to_inventory({"name": selected_item["name"], "type": "consumable"}, inventory)
                print(f"Purchased {purchased} x {selected_item['name']}. You have ${gold} left.")
            else:
                print("You cannot afford this item.")

# ---------------- SAVE / LOAD ----------------
def save_game(health: int, gold: int, map_state: dict, filename: str = SAVE_FILENAME):
    # ensure monsters are serialized to dicts
    mons = map_state.get("monsters", [])
    map_state["monsters"] = [m if isinstance(m, dict) else m.to_dict() for m in mons]
    save_data = {"health": health, "gold": gold, "inventory": inventory, "map_state": map_state}
    with open(filename, "w") as f:
        json.dump(save_data, f, indent=4)
    print(f"Game saved to {filename}!")

def load_game(filename: str = SAVE_FILENAME) -> tuple[int, int, dict]:
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        inventory.clear()
        inventory.extend(data.get("inventory", []))
        map_state = data.get("map_state", DEFAULT_MAP_STATE.copy())
        # ensure monsters is a list of dicts
        map_state["monsters"] = list(map_state.get("monsters", []))
        return data.get("health", 30), data.get("gold", 15), map_state
    except FileNotFoundError:
        print("No save file found. Starting new game.")
        return 30, 15, DEFAULT_MAP_STATE.copy()

# ---------------- COMBAT ----------------
def fight_monster_entity(monster: Monster, health: int, gold: int) -> tuple[int, int, bool]:
    """Fight a specific Monster. Returns (health, gold, defeated_flag)."""
    monster_health = int(monster.health)
    monster_power = int(monster.power)
    monster_name = monster.name
    monster_money = int(monster.money)

    print(f"\nA wild {monster_name} appears!")

    while health > 0 and monster_health > 0:
        print(f"\nYour HP: {health} | {monster_name} HP: {monster_health}")
        print("1) Attack")
        print("2) Run Away")
        print("3) Use Special Item")

        choice = get_valid_input("> ", ["1", "2", "3"])

        if choice == "1":
            dmg_to_monster = random.randint(5, 10)
            dmg_to_player = random.randint(0, monster_power)
            monster_health -= dmg_to_monster
            health -= dmg_to_player
            print(f"You strike for {dmg_to_monster} damage!")
            print(f"The {monster_name} hits you for {dmg_to_player} damage!")
        elif choice == "2":
            print("You escaped safely!")
            return health, gold, False
        elif choice == "3":
            used = use_special_item(inventory, monster_name)
            if used:
                monster_health = 0

    if health <= 0:
        print("\nYou were defeated...")
        return health, gold, False
    else:
        gold += monster_money
        print(f"\nYou defeated the {monster_name} and earned {monster_money} gold!")
        return health, gold, True

# ---------------- MAP LOOP ----------------
def start_map(map_state: dict) -> tuple[str, dict, int | None]:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Adventure Map")
    clock = pygame.time.Clock()

    player_x, player_y = map_state.get("player_pos", (0, 0))
    town_pos = tuple(map_state.get("town_pos", (0, 0)))
    visited_town = bool(map_state.get("visited_town", False))

    # Build monster objects from saved dicts
    saved_monsters = map_state.get("monsters", [])
    monsters = monsters_from_state(saved_monsters)

    # Spawn two monsters if none present
    monsters = ensure_two_monsters(monsters, GRID_SIZE, town_pos, (player_x, player_y))

    running = True
    action = None
    encounter_index: int | None = None
    move_count = 0  # track player moves

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                action = "quit_pygame"
                running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP: dy = -1
                elif event.key == pygame.K_DOWN: dy = 1
                elif event.key == pygame.K_LEFT: dx = -1
                elif event.key == pygame.K_RIGHT: dx = 1
                elif event.key == pygame.K_ESCAPE:
                    # Quick return to town
                    action = "town"
                    running = False

                if dx or dy:
                    # Player move
                    player_x = max(0, min(GRID_SIZE - 1, player_x + dx))
                    player_y = max(0, min(GRID_SIZE - 1, player_y + dy))
                    move_count += 1

                    if (player_x, player_y) != town_pos:
                        visited_town = True

                    # Monster moves every other player move
                    move_monsters_every_other(monsters, GRID_SIZE, town_pos, move_count)

                    # Check collision (player on any monster)
                    enc_idx = collision_index(monsters, (player_x, player_y))
                    if enc_idx is not None:
                        action = "monster"
                        encounter_index = enc_idx
                        running = False

                    # Return to town if stepping onto town after leaving
                    if (player_x, player_y) == town_pos and visited_town and action is None:
                        action = "town"
                        running = False

        # Draw grid
        screen.fill(BG_COLOR)
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, GRID_COLOR, (i * TILE_SIZE, 0), (i * TILE_SIZE, HEIGHT))
            pygame.draw.line(screen, GRID_COLOR, (0, i * TILE_SIZE), (WIDTH, i * TILE_SIZE))

        # Town
        cx, cy = town_pos[0]*TILE_SIZE+TILE_SIZE//2, town_pos[1]*TILE_SIZE+TILE_SIZE//2
        pygame.draw.circle(screen, TOWN_COLOR, (cx, cy), TILE_SIZE//3)

        # Monsters (distinct colors)
        for m in monsters:
            mx, my = m.pos
            cx, cy = mx*TILE_SIZE+TILE_SIZE//2, my*TILE_SIZE+TILE_SIZE//2
            pygame.draw.circle(screen, m.color, (cx, cy), TILE_SIZE//3)

        # Player
        rect = pygame.Rect(player_x*TILE_SIZE, player_y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, PLAYER_COLOR, rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    updated_state = {
        "player_pos": (player_x, player_y),
        "town_pos": town_pos,
        "visited_town": visited_town,
        # Persist monsters as dicts
        "monsters": monsters_to_state(monsters),
    }
    return action, updated_state, encounter_index

# ---------------- MAIN LOOP ----------------
def main():
    print("Welcome to the Adventure Game!")
    print("-------------------------------")
    print("1) New Game")
    print("2) Load Game")

    choice = get_valid_input("> ", ["1", "2"])

    if choice == "1":
        name = input("Enter your name, brave adventurer: ")
        health = 30
        gold = 15
        map_state = DEFAULT_MAP_STATE.copy()
    else:
        name = input("Enter your name for loading: ")
        health, gold, map_state = load_game()

    print_welcome(name, 40)

    while True:
        print(f"\nYou are in town. HP: {health} | Gold: {gold}")
        print("1) Leave town (Explore Map)")
        print("2) Sleep (Restore HP for 5 Gold)")
        print("3) Inventory")
        print("4) Shop")
        print("5) Save & Quit")
        print("6) Quit without saving")

        choice = get_valid_input("> ", ["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            # Enter map; handle transitions
            while True:
                action, map_state, encounter_index = start_map(map_state)

                if action == "quit_pygame":
                    print("Game closed abruptly. Exiting without saving.")
                    return
                elif action == "town":
                    break
                elif action == "monster":
                    # Fight the specific encountered monster
                    mons_dicts = map_state.get("monsters", [])
                    mons = monsters_from_state(mons_dicts)
                    if encounter_index is not None and 0 <= encounter_index < len(mons):
                        m = mons[encounter_index]
                        health, gold, defeated = fight_monster_entity(m, health, gold)
                        if health <= 0:
                            print("You died. Game over.")
                            return
                        if defeated:
                            # Remove defeated monster
                            mons.pop(encounter_index)
                            # If none left, spawn two new immediately (persisted)
                            if not mons:
                                avoid_town = tuple(map_state["town_pos"])
                                player_pos = tuple(map_state["player_pos"])
                                mons = ensure_two_monsters([], GRID_SIZE, avoid_town, player_pos)
                            map_state["monsters"] = monsters_to_state(mons)
                    continue

        elif choice == "2":
            if gold >= 5:
                gold -= 5
                health = 30
                print("You rest at the inn and restore your health.")
            else:
                print("Not enough gold to rest.")
        elif choice == "3":
            while True:
                show_inventory(inventory)
                print("\nInventory Menu:")
                print("1) Equip Weapon")
                print("2) Equip Shield")
                print("3) Return to Town")

                inv_choice = get_valid_input("> ", ["1", "2", "3"])
                if inv_choice == "1":
                    equip_item("weapon", inventory)
                elif inv_choice == "2":
                    equip_item("shield", inventory)
                elif inv_choice == "3":
                    break
        elif choice == "4":
            gold = shop_menu(gold)
        elif choice == "5":
            save_game(health, gold, map_state)
            print("Exiting game. Goodbye!")
            break
        elif choice == "6":
            print("Exiting game without saving. Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting game.")
