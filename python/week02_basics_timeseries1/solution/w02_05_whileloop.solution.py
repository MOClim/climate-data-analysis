# Create a list contains the fruit name.
fruits=["apple","cherry","peach","pear","banana","grape","watermelon","orange","kiwi","mango"]

# simple printout
print(fruits)

# The function len() returns the total count of elements within the iterable
print(len(fruits))
print("")

print("Index-based loop")
# Uses an index to access each element of the list by its position 
for i in range(len(fruits)):
  print(fruits[i])
print("")

# print using two types of loop
print("Direct Item Access Loop")
# Iterates directly over the elements of the list, making the code simpler and more readable
for fruit in fruits:
  print(fruit)
print(" ")

# print while loop
print("While Loop")
i = 0
while i < len(fruits):
  print(i, fruits[i])
  i += 1

