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
from gamefunctions import (
    inventory,
    show_inventory,
    add_to_inventory,
    equip_item,
    use_special_item,
    new_random_monster,
    print_welcome,
    purchase_item
)

SAVE_FILENAME = "savegame.json"

def get_valid_input(prompt: str, valid_options: list[str]) -> str:
    """Prompt the player until a valid input is entered."""
    while True:
        try:
            choice = input(prompt).strip()
        except EOFError:
            print("\nInput ended. Exiting game.")
            exit()
        if choice in valid_options:
            return choice
        print("Invalid choice. Try again.")

def fight_monster(health: int, gold: int) -> tuple[int, int]:
    """Handles a fight with a random monster."""
    monster = new_random_monster()
    monster_health = monster["health"]
    monster_power = monster["power"]

    print(f"\nA wild {monster['name']} appears!")
    print(monster["description"])

    while health > 0 and monster_health > 0:
        print(f"\nYour HP: {health} | {monster['name']} HP: {monster_health}")
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
            print(f"The {monster['name']} hits you for {dmg_to_player} damage!")
        elif choice == "2":
            print("You escaped safely!")
            return health, gold
        elif choice == "3":
            used = use_special_item(inventory, monster["name"])
            if used:
                monster_health = 0  # instant defeat

    if health <= 0:
        print("\nYou were defeated...")
    else:
        reward = monster["money"]
        gold += reward
        print(f"\nYou defeated the {monster['name']} and earned {reward} gold!")

    return health, gold

def shop_menu(gold: int) -> int:
    """Display a shop with multiple items and handle purchases."""
    items = [
        {"name": "Bread", "price": 20},
        {"name": "Cheese", "price": 15},
        {"name": "Juice", "price": 5},
        {"name": "Cake", "price": 12},
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
            except ValueError:
                print("Invalid input. Returning to shop menu.")
                continue

            purchased, remaining_gold = purchase_item(selected_item["price"], gold, quantity)
            gold = remaining_gold
            if purchased > 0:
                add_to_inventory({"name": selected_item["name"], "type": "consumable"}, inventory)
                print(f"Purchased {purchased} x {selected_item['name']}. You have ${gold} left.")
            else:
                print("You cannot afford this item.")

def save_game(health: int, gold: int, filename: str = SAVE_FILENAME):
    """Save the current game state to a JSON file."""
    save_data = {
        "health": health,
        "gold": gold,
        "inventory": inventory
    }
    with open(filename, "w") as f:
        json.dump(save_data, f, indent=4)
    print(f"Game saved to {filename}!")

def load_game(filename: str = SAVE_FILENAME) -> tuple[int, int]:
    """Load the game state from a JSON file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        # Clear current inventory and load saved inventory
        inventory.clear()
        inventory.extend(data["inventory"])
        print(f"Game loaded from {filename}!")
        return data["health"], data["gold"]
    except FileNotFoundError:
        print("No save file found. Starting new game.")
        return 30, 15  # default starting HP and gold

def main():
    """Main game loop with save/load, town options, inventory, and shop."""
    print("Welcome to the Adventure Game!")
    print("-------------------------------")
    print("1) New Game")
    print("2) Load Game")

    choice = get_valid_input("> ", ["1", "2"])

    if choice == "1":
        name = input("Enter your name, brave adventurer: ")
        health = 30
        gold = 15
    else:
        name = input("Enter your name for loading: ")
        health, gold = load_game()

    print_welcome(name, 40)

    while True:
        print(f"\nYou are in town. HP: {health} | Gold: {gold}")
        print("1) Leave town (Fight Monster)")
        print("2) Sleep (Restore HP for 5 Gold)")
        print("3) Inventory")
        print("4) Shop")
        print("5) Save & Quit")
        print("6) Quit without saving")

        choice = get_valid_input("> ", ["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            health, gold = fight_monster(health, gold)
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
            save_game(health, gold)
            print("Exiting game. Goodbye!")
            break
        elif choice == "6":
            print("Exiting game without saving. Goodbye!")
            break

if __name__ == "__main__":
    main()
