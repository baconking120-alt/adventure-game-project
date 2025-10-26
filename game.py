"""
Main game script that imports and uses functions from gamefunctions.py.

This script demonstrates basic interaction with the player and calls
each of the four required functions from the gamefunctions module.

Typical usage example:

    python game.py
"""

import gamefunctions

def main():
    # Welcome the player
    player_name = input("Enter your name, brave adventurer: ")
    gamefunctions.print_welcome(player_name, 40)

    # Show shop menu
    print("\nWelcome to the shop! Here's what's available:")
    gamefunctions.print_shop_menu("Potion", 25.50, "Elixir", 40.75)

    # Try purchasing an item
    print("\nLet's try buying some items.")
    money = int(input("How much money do you have? "))
    item_price = int(input("Enter the price of the item you want to buy: "))
    quantity = int(input("How many would you like to buy? "))

    purchased, remaining = gamefunctions.purchase_item(item_price, money, quantity)
    print(f"You purchased {purchased} item(s). You have ${remaining} left.")

    # Generate a random monster
    print("\nA wild monster appears!")
    monster = gamefunctions.new_random_monster()
    print(f"Name: {monster['name']}")
    print(f"Description: {monster['description']}")
    print(f"Health: {monster['health']}, Power: {monster['power']}, Money: {monster['money']}")

if __name__ == "__main__":
    main()
"""Game functions module for a python adventure game
it will show you a loop that will perform different actions and bring up a print menu that will 
show a list of available options
"""
import random
import gamefunctions
def get_valid_input(promt: str, valid_options: list[str]) -> str:
    """Promt the player until he or she gets a valid input option
""" 
    choice = input(promt).strip()
    while choice not in valid_options:
        print("Invalid choice, please try again.")
        choice = input(promt).strip()
    return choice
def fight_monster(health: int, gold: int) -> tuple[int, int]:
    """shows players stats and fight with monster
    """
    monster = gamefunctions.new_random_monster()
    monster_health = monster["health"]
    monster_power = monster["power"]
    print(f"\nA wild {monster['name']} appears!")
    print(monster["description"])
    while health > 0 and monster_health > 0:
        print(f"\nYour HP: {health} | {monster['name']} HP: {monster_health}")
        print("1) Attack")
        print("2) Run Away")
        choice = get_valid_input("> ", ["1", "2"])

        if choice == "1":
            dmg_to_monster = random.randint(5, 10)
            dmg_to_player = random.randint(0, monster_power)
            monster_health -= dmg_to_monster
            health -= dmg_to_player
            print(f"You strike for {dmg_to_monster} damage!")
            print(f"The {monster['name']} hits you for {dmg_to_player}!")
        elif choice == "2":
            print("You escaped safely!")
            return health, gold
        if health <= 0:
            print("\nYou were defeated...")
        elif monster_health <= 0:
            reward = monster["money"]
            gold += reward
            print(f"\nYou defeated the {monster['name']} and earned {reward} gold!")
    return health, gold
def main():
    """Main game loop."""
    name = input("Enter your name, brave adventurer: ")
    health = 30
    gold = 10

    gamefunctions.print_welcome(name, 40)
    while True:
        print(f"\nYou are in town.")
        print(f"Current HP: {health}, Current Gold: {gold}")
        print("\nWhat would you like to do?")
        print("1) Leave town (Fight Monster)")
        print("2) Sleep (Restore HP for 5 Gold)")
        print("3) Quit")
        choice = get_valid_input("> ", ["1", "2", "3"])
        if choice == "1":
            health, gold = fight_monster(health, gold)
        elif choice == "2":
            if gold >= 5:
                gold -= 5
                health = 30
                print("You rest at the inn and restore your health.")
            else:
                print("You don't have enough gold to rest.")
        elif choice == "3":
            print("Farewell, adventurer!")
            break
        if health <= 0:
            print("You have fallen in battle. Game Over!")
            break
if __name__ == "__main__":
    main()