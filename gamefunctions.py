

#gamefunctions.py
#Adam Azam
#2025-september-27

import random

# Starting Inventory
inventory = [
    {"name": "sword", "type": "weapon", "maxDurability": 10, "currentDurability": 10},
    {"name": "buckler", "type": "shield", "maxDurability": 6, "currentDurability": 6},
    {"name": "rock", "type": "misc", "note": "defeats one monster instantly"}
]

def purchase_item(item_price: int, starting_money: int, quantity_to_purchase: int = 1):
    """Attempt to purchase items given a price, starting money, and quantity desired."""
    max_affordable = starting_money // item_price
    items_bought = min(max_affordable, quantity_to_purchase)
    remaining_money = starting_money - (items_bought * item_price)
    return items_bought, remaining_money

def new_random_monster():
    """Generate a random monster with randomized stats."""
    monsters = [
        {
            "name": "Gnome",
            "description": "A sly gnome dashes toward you!",
            "health_range": (20, 40),
            "power_range": (5, 10),
            "money_range": (10, 50)
        },
        {
            "name": "Imp",
            "description": "A fiery imp laughs menacingly!",
            "health_range": (10, 25),
            "power_range": (8, 15),
            "money_range": (20, 100)
        },
        {
            "name": "Ghoul",
            "description": "A ghoul crawls from the shadows!",
            "health_range": (60, 100),
            "power_range": (15, 25),
            "money_range": (50, 200)
        }
    ]

    m = random.choice(monsters)
    return {
        "name": m["name"],
        "description": m["description"],
        "health": random.randint(*m["health_range"]),
        "power": random.randint(*m["power_range"]),
        "money": random.randint(*m["money_range"])
    }

def print_welcome(name: str, width: int) -> None:
    message = f"Hello, {name}!"
    print(f"{message:^{width}}")

def print_shop_menu(item1Name: str, item1Price: float, item2Name: str, item2Price: float) -> None:
    border = "/" + "-" * 22 + "\\"
    print(border)
    print(f"| {item1Name:<12} ${item1Price:>7.2f} |")
    print(f"| {item2Name:<12} ${item2Price:>7.2f} |")
    print("\\" + "-" * 22 + "/")

def add_to_inventory(item: dict, inventory: list) -> None:
    """Add an item to the player's inventory."""
    inventory.append(item)
    print(f"{item['name']} has been added to your inventory!")

def show_inventory(inventory: list) -> None:
    """Display the player's current inventory."""
    if not inventory:
        print("Your inventory is empty.")
        return

    print("\nYour Inventory:")
    for i, item in enumerate(inventory, start=1):
        if item["type"] in ["weapon", "shield"]:
            print(f"{i}) {item['name']} ({item['type']}) - Durability: {item['currentDurability']}/{item['maxDurability']}")
        else:
            print(f"{i}) {item['name']} ({item['type']}) - {item.get('note','')}")

def equip_item(item_type: str, inventory: list):
    """Let the player choose and equip an item of a given type."""
    items = [item for item in inventory if item["type"] == item_type]

    if not items:
        print(f"No {item_type} available to equip.")
        return None

    print(f"\nChoose a {item_type} to equip:")
    for i, item in enumerate(items, start=1):
        print(f"{i}) {item['name']} (Durability: {item['currentDurability']}/{item['maxDurability']})")
    print("0) Cancel")

    while True:
        choice = input("> ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                print("You equipped nothing.")
                return None
            if 1 <= choice <= len(items):
                equipped = items[choice - 1]
                print(f"You equipped: {equipped['name']}")
                return equipped
        print("Invalid choice, try again.")

def use_special_item(inventory: list, monster_name: str) -> bool:
    """Use a special item like the rock to instantly defeat a monster."""
    for item in inventory:
        if item["name"].lower() == "rock":
            print(f"\nYou throw the rock! The {monster_name} is instantly defeated!")
            inventory.remove(item)
            print("The rock crumbles and is gone.")
            return True
    print("You have no special item!")
    return False