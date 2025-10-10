# madlib.py
# Adam Azam
# 9/6/25

# This program implements the word game Mad Libs.
# The user is prompted for a list of words that are
# substituted for blanks in a story.
print()
print("Welcome! You are about to play a fantastic word game.")
print("I will ask you for nouns, verbs, adjectives, and adverbs.")
print("Using those words, I will create an unexpected story for you!")

noun1 = input("Tell me a noun (plural), and click enter: ")
adj1 = input("Tell me an adjective, and click enter: ")
noun2 = input("Tell me a noun (plural), and click enter: ")
noun3 = input("Tell me another noun, and click enter: ")
adj2 = input("Tell me another adjective, and click enter: ")
print()
print(f"{noun1} are {adj1}")
print(f"{noun2} are blue")
print(f"{noun3} is {adj2}")
print("And so are you!")
