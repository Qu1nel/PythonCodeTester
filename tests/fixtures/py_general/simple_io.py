name = input("Enter your name: ")
age = int(input("Enter your age: "))

print(f"Hello, {name}!")
print(f"You are {age} years old.")

if age >= 18:
    print("You are an adult.")
else:
    print("You are a minor.")