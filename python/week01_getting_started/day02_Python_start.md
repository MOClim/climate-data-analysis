# Week 1 Day2: Getting Python Started

## Goal

* Use shell commands
* Understand directory structure
* Launch vi for editing
* Run basic Python code

---

## Directory Structure

```id="x9k2pm"
climate-data-analysis/
    ├── data/
    ├── python/
    |      └── week01_getting_started/
    |             ├── README.md
    |             ├── solution/
    |             └── w01_01_hello.sample.py
    └── ncl/
```

**Important:**

* Data is stored in `data/` (one level above)
* This folder contains your notebook

---

Mac Users: Install iTerm

Mac users will use iTerm as the terminal application for this course.

Install iTerm2:

- Download from: https://iterm2.com
- Open the downloaded file
- Drag iTerm into the Applications folder
- Launch iTerm

Check:
```bash id="m3z7qa"
pwd 
ls
```

---
Windows Users: Use WSL (Windows Subsystem for Linux) for This Course

Windows users will use WSL (Ubuntu) as the main terminal environment.

First, open Windows PowerShell as Administrator and run:

```bash id="m3z7qa"
wsl --install
```

Restart your computer.

Then open Ubuntu from the Start menu and complete the setup.

From this point on, use the Ubuntu (WSL) terminal for all coursework.

Check:
```bash id="m3z7qa"
pwd 
ls
```

---

## Day 1: Terminal and Setup

### 1. Open Terminal

* Mac: iTerm
* Windows: WSL Terminal

---

### 2. Move to Documents

```bash id="m3z7qa"
cd ~/Documents
```

---

### 3. Clone Repository

```bash id="p8n4kt"
git clone [<repository_url>](https://github.com/MOClim/climate-data-analysis.git)
cd climate-data-analysis
ls
cd python
ls
cd week01_getting_started
```

---

### 4. Check Files

```bash id="v2q6zr"
ls
```

---

### 5. Check Branch

```bash id="v2q6zr"
git branch
```

You should see:

* student-2026

---

## Day 2: First Python Script

### 1. Open Terminal
- Mac: iTerm
- Windows: Ubuntu (WSL) terminal

---

### 2. Set Up the Course Environment

Before starting Python, we will create a **Conda environment** for this course.

A Conda environment keeps Python and the required packages together. The required packages are listed in the `environment.yml` file in the course repository.

#### Create the Environment — First Time Only

Make sure you are in the `climate-data-analysis` directory:
```bash
cd climate-data-analysis
ls
```

You should see `environment.yml`.

Create the course environment:
```bash
conda env create -f environment.yml
```
This process may take several minutes.

> **You only need to create the environment once.**

#### Activate the Environment

After the installation is complete, activate the environment:
```bash
conda activate climate-analysis
```
**You should see `(climate-analysis)` at the beginning of your Terminal prompt**:
```text
(climate-analysis) ...
```
This indicates that the course environment is active.

#### From the Next Class
You do **not** need to create the environment again. Each time you start working on this course, simply activate it:
```bash
conda activate climate-analysis
```

Now you are ready to start Python!

---

### Exercise ### 
### 1. Move to the Directory and Check Files
   
```bash id="r6k1vb"
cd ~/Documents/climate-data-analysis/python/week01_getting_started
ls
```

---

### 2. Check Repository

Update Repository
```bash id="r6k1vb"
git pull
```

Check Status
```bash id="r6k1vb"
git status
```

---
  
### 3. Create Your Script

Copy the original file to a new file using the `cp` command:

```bash id="z1w3xl"
cp w01_01_hello.sample.py w01_01_hello.py
```

---

### 4. Edit the Script (vi)

Open the file using vi:

```bash id="z1w3xl"
vi w01_01_hello.py
```

Basic commands:

- `i` → insert mode  
- `Esc` → exit  
- `:wq` → save and quit  

Example:

- Press `i`
- Edit the file
- Esc → :wq → Enter

---

### 5. Run code

```python id="u3p8dm"
python w01_01_hello.py
print("Hello, climate data analysis!")
```

---

### 6. Add Code

Inside the file, write:

print("Hello, my name is xxx.")
temperature = 20
print(temperature)

---
### 7. Run the Script

```python id="u3p8dm"
python w01_01_hello.py
```

Expected Output
```python id="u3p8dm"
Hello, climate data analysis!
Hello, my name is xxx.
20
```

---

## Check

You should be able to:
- Navigate directories
- Use vi to edit a file
- Run a Python script
