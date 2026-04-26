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

## Day 1: Terminal and Setup

### 1. Open Terminal

* Mac: Terminal / iTerm
* Windows: PowerShell

---

### 2. Move to Documents

```bash id="m3z7qa"
cd ~/Documents
```

---

### 3. Clone Repository

```bash id="p8n4kt"
git clone <repository_url>
cd climate-data-analysis/week01_getting_started
```

---

### 4. Check Files

```bash id="v2q6zr"
ls
```

---

### 5. Start Jupyter

```bash id="z1w3xl"
jupyter notebook
```

Open:

```id="j4zxiz"
week01_intro.ipynb
```

Run all cells (`Shift + Enter`)

---

## Day 2: First Python

```bash id="r6k1vb"
cd ~/Documents/climate-data-analysis/week01_getting_started
jupyter notebook
```

---

### Run code

```python id="u3p8dm"
print("Hello, climate data")
```

```python id="t7n2qk"
temperature = 20
print(temperature)
```

---

## Key Concept

Data is stored outside this folder.

```python id="aomenz"
"../data/filename.csv"
```

---

## Workflow

Directory → Notebook → Code → Data

---

## Check

* Navigate directories
* Open notebook
* Run code
