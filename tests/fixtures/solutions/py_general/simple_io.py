import sys

name = input("Name: ")
print(f"Hello, {name}!")
print("Error message", file=sys.stderr)
