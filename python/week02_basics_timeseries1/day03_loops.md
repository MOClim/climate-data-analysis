# Week 02 (Day 3): Python Basics

## ## Overview
This lesson introduces Python loops and iterative operations commonly used in climate and geoscience data analysis workflows.

## Learning Objectives
- Understand `for` loops
- Iterate through lists and arrays
- Apply loops to climate datasets
- Automate repetitive calculations

---

### Exercise 1: Modify the Namelist

This exercise introduces basic file operations and code editing within a Unix-like environment.

#### Step 1: Access the repository

Open the Week 02 directory in your local clone of the repository:
```bash
cd python/week02_basics_timeseries1
```

#### Step 2: Create a new file
```bash
cp w02_01_namelist.sample.py w02_01_namelist.py
ls
```

#### Step 3: Edit the code
```bash
vi w02_01_namelist.py
```
- Press i to enter insert mode
- Add a new fruit name to the list
- Press ESC, then type :wq and press Enter to save and exit

#### Step 4: Run the code
```bash
python w02_01_namelist.py
```

#### Example Output
apple cherry peach pear banana grape watermelon orange kiwi mango berry

---

### Next Step
Modify the script to print each fruit on a separate line.
This introduces the concept of a loop, which is fundamental for iterating over climate data arrays and time series.

### Extension: Loop Practice

Modify the loop in w02_02_loop.py (copied from w02_02_loop.sample.py):

```python
for i in range(5):
    print(i)
```

Change range(5) to range(10) and run again:
```bash
python w02_02_loop.py
```

---

### Exercise 2: Loop over Fruit Names

#### Step 1: Inspect the script
```bash
cp w02_03_multi-lines-loop.sample.py w02_03_multi-lines-loop.py
less w02_03_multi-lines-loop.py
```

#### Step 2: Run the script
```bash
python w02_03_multi-lines-loop.py
```

#### Output 
Example:
```bash
['apple', 'cherry', 'peach', 'pear', 'banana', 'grape', 'watermelon', 'orange', 'kiwi', 'mango']
10

Index-based loop
0 apple
1 cherry
2 peach
...
```

#### Concept: Index-based Loop

fruits = ["apple", "cherry", "peach", "pear", "banana"]

```python
for i in range(len(fruits)):
    print(i, fruits[i])
```
Uses an index to access elements
range(len(fruits)) → 0 to N−1

---

### Direct Loop (Recommended)

#### Step 1: Inspect another script
```bash
cp w02_04_multi-lines-loop2.sample.py w02_04_multi-lines-loop2.py
less w02_04_multi-lines-loop2.py
```

#### Step 2: Run the script
```bash
python w02_04_multi-lines-loop2.py
```

#### Concept: Direct iteration
```python
for fruit in fruits:
    print(fruit)
```
- Iterates directly over elements
- More readable and Pythonic

---

### Extension: Compare Two Loop Styles

Method	Description
Index-based loop	Access using position (i)
Direct loop	Access element directly

👉 Which one is more readable?

---

### Exercise 3: While Loop

###Concept
A while loop runs as long as a condition is true.

```python
i = 0
while i < 5:
   print(i) i += 1
```

- Starts from an initial condition
- Continues until the condition becomes false

#### Step 1: Create a new file
```bash
cp w02_04_multi-lines-loop2.py w02_05_whileloop.py
```

#### Step 2: Add the while loop
```python
i = 0
while i < len(fruits):
  print(i, fruits[i])
  i += 1
```

#### Step 3: Run
```bash
python w02_05_whileloop.py
```

---

### Better Practice: `enumerate()`

```python
for i, fruit in enumerate(fruits):
    print(i, fruit)
```
- More concise than index-based loops
- Provides both index and value simultaneously
- Improves readability and reduces indexing errors

Reference: w02_06_enumerate.solution.py
  
---

## Key Takeaways

- for loop → best for iterating over sequences
- while loop → best when using conditions

Loops are essential for processing time series and multidimensional climate data
