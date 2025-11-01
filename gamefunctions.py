

#gamefunctions.py
#Adam Azam
#2025-september-27
import random
inventory = [
    {"name": "sword", "type": "weapon", "maxDurability": 10, "currentDurability": 40},
    {"name": "buckler", "type": "shield", "maxDurability": 6, "currentDurability": 20},
    {"name": "rock", "type": "misc", "note": "defeats scissors"}
    ]

def purchase_item(item_price: int, starting_money: int, quantity_to_purchase: int = 1):
    """
    Attempt to purchase items given a price, starting money, and quantity desired.

    parameters:
        item_price (int): price of a single item.
        starting_money (int): amount of money the buyer has.
        quantity_to_purchase (int): number of items to try to buy (default = 1).

    returns:
        tuple: (number of items purchased, money remaining)
    """
# maximum number affordable with given money
    max_affordable = starting_money // item_price

    # actual number bought is limited by both affordability and desired quantity
    items_bought = min(max_affordable, quantity_to_purchase)

    # calculate leftover money
    remaining_money = starting_money - (items_bought * item_price)

    return items_bought, remaining_money


def new_random_monster():
    """
    Create a random monster with randomized stats.

    returns:
        dict: monster information containing:
            - name (str)
            - description (str)
            - health (int)
            - power (int)
            - money (int)
    """
    monsters = [
        {
            "name": "Gnome",
            "description": "A mischievous gnome with a crooked hat and a sly grin. "
                           "It darts toward you with surprising speed.",
            "health_range": (20, 40),
            "power_range": (5, 10),
            "money_range": (10, 50)
        },
        {
            "name": "Imp",
            "description": "A fiery little imp with glowing red eyes. "
                           "It cackles as it hurls sparks in your direction.",
            "health_range": (10, 25),
            "power_range": (8, 15),
            "money_range": (20, 100)
        },
        {
            "name": "Ghoul",
            "description": "A ghoul rises from the shadows, its claws dripping with dark ooze. "
                           "Its presence alone chills your bones.",
            "health_range": (60, 100),
            "power_range": (15, 25),
            "money_range": (50, 200)
        }
    ]

    # pick a random monster type
    monster_template = random.choice(monsters)

    # generate randomized stats within that monster's range
    monster = {
        "name": monster_template["name"],
        "description": monster_template["description"],
        "health": random.randint(*monster_template["health_range"]),
        "power": random.randint(*monster_template["power_range"]),
        "money": random.randint(*monster_template["money_range"])
    }

    return monster

def print_welcome(name: str, width: int) -> None:
    message = f"Hello, {name}!"
    print(f"{message:^{width}}")
def print_shop_menu(item1Name: str, item1Price: float, item2Name: str, item2Price: float) -> None:
    border = "/" + "-" * 22 + "\\"
    print(border)
    print(f"| {item1Name:<12} ${item1Price:>7.2f} |")
    print(f"| {item2Name:<12} ${item2Price:>7.2f} |")
    print("/" + "-" * 22 + "\\")

def add_to_inventory(item: dict, inventory: list) -> None:
    #adding to inventory
    inventory.append(item)
    print(f"{item} has been added into your inventory!")

def show_inventory(inventory: list) -> None:
    if not inventory:
        print("your inventory is vacant.")
    else:
        print("\nYour inventory:")
        number = 1
        for item in inventory:
            if item["type"] in ["weapon", "shield"]:
                print(f"{number}) {item['name']} ({item['type']}) - Durability: {item['currentDurability']}/{item['maxDurability']}")
            else:
                print(f"{number}) {item['name']} ({item['type']}) - Note: {item.get('note', '')}")
            number += 1

def equip_item(item_type: str, inventory: list) -> dict | None:
    items_type = []
    for item in inventory:
        if item["type"] == item_type:
            items_type. append(item)
    if not items_type:
        print(f"No items of type '{item_type}' available to equip.")
        return None
    print(f"\nItems available to equip ({item_type}):")
    number = 1
    for item in items_type:
        print(f"{number}) {item['name']} (Durability: {item.get('currentDurability', 'N/A')})")
        number += 1
    print("0) None")
    while True:
        choice = input("Choose an item to equip: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= len(items_type):
                if choice == 0:
                    print("No item equipped.")
                    return None
                equipped = items_type[choice - 1]
                print(f"You equipped: {equipped['name']}")
                return equipped
        print("Invalid choice. Try again.")

def use_special_item(inventory: list, monster_name: str) -> bool:
    for item in inventory:
        if item["name"].lower() == "rock":
            print(f"\nYou throw your {item['name']} at the {monster_name}!")
            print(f"The {monster_name} is instantly defeated!")
            inventory.remove(item)
            print(f"{item['name']} has been removed from your inventory.")
            return True

    print("You have no special item to use!")
    return False

                     
if __name__ == "__main__":
    # -------------------------------
    # Test calls for purchase_item()
    # -------------------------------

    print("=== Testing purchase_item ===")

    # Case 1: Can afford all 3
    num_purchased, leftover = purchase_item(123, 1000, 3)
    print(f"Purchased: {num_purchased}, Leftover money: {leftover}")

    # Case 2: Cannot afford all 3, only buys 1
    num_purchased, leftover = purchase_item(123, 201, 3)
    print(f"Purchased: {num_purchased}, Leftover money: {leftover}")

    # Case 3: Using default quantity_to_purchase (should buy only 1)
    num_purchased, leftover = purchase_item(341, 2112)
    print(f"Purchased: {num_purchased}, Leftover money: {leftover}")

    print("\n=== Testing new_random_monster ===")

    # Call 3 times to demonstrate randomness
    for i in range(3):
        monster = new_random_monster()
        print(f"Monster {i+1}: {monster['name']}")
        print(f"Description: {monster['description']}")
        print(f"Health: {monster['health']}, Power: {monster['power']}, Money: {monster['money']}")
        print()
    
    print_welcome("Diego", 24)
    print_welcome("Wade", 34)
    print_shop_menu("Bread", 20, "cheese", 15)
    print_shop_menu("juice", 5.23, "cake", 12.33)


