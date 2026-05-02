# Week 1: Getting Started

## Goal

* Use shell commands
* Understand directory structure
* Launch Jupyter Notebook
* Run basic Python code

---

## Directory Structure

```id="x9k2pm"
climate-data-analysis/
    ├── data/
    └── week01_getting_started/
        ├── week01_intro.ipynb
        └── README.md
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
git clone -b student-2026 [<repository_url>](https://github.com/MOClim/climate-data-analysis.git)
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

### 2. Move to the Directory and Check Files
   
```bash id="r6k1vb"
cd ~/Documents/climate-data-analysis/python/week01_getting_started
ls
```

---

### 3. Check Branch

```bash id="r6k1vb"
git branch
```

You should see:

* student-2026

---
  
### 4. Create Your Script

Copy the original file to a new file using the `cp` command:

```bash id="z1w3xl"
cp w01_01_hello.sample.py w01_01_hello.py
```

---

### 5. Edit the Script (vi)

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
- Press `:wq`
- Press return

---

### 6. Run code

```python id="u3p8dm"
python w01_01_hello.py
print("Hello, climate data")
```

---

### 7. Add command lines

```python id="u3p8dm"
vi w01_01_hello.py
```

Example:

- Press `i`
- Add the file as follows:
- print ("Hello, my name is xxx.")
- Press `:wq`
- Press return

```python id="u3p8dm"
python w01_01_hello.py

Hello, climate data
Hello, my name is xxx.
```

Add the following commands.
```python id="t7n2qk"
temperature = 20
print(temperature)
```

---

## Check

* Navigate directories
* Open iTerm (Mac) or WSL (Windows) for editing a code
* Run a python script
