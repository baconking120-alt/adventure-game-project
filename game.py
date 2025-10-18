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