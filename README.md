# Climate Data Analysis

Course materials for climate data analysis using Python.

## Getting Started

If `conda` or `git` is not installed, **see "Environment Setup" below first**.

Open terminal:
- Mac → Terminal or iTerm
- Windows → Windows Subsystem for Linux (WSL) 

### For Windows Users
```bash
cd /mnt/c/Users/<username>/Documents
```

### For Mac Users
```bash
cd /Users/<username>/Documents
```
'cd' is the unix command to change the current directory.

For both Windows and Mac Users, create a directory name `course`.
```bash
mkdir course
```
'mkdir' is the command to create a new directory.
```bash
cd course
```

Clone this repository and set up the Python environment:
```bash
git clone https://github.com/MOClim/climate-data-analysis.git
```
```bash
cd climate-data-analysis
```
```bash
conda env create -f environment.yml
```
```bash
conda activate climate-analysis
```

If the installation is completed successfully, run the following commands:
```bash
ls
pwd
```
'ls' is a command used to list files and directories in the current directory.
'pwd' is a command used to display the path of the current directory.

---
### Directory Structure

After completing the setup, your course directory should have the following structure:

```text
Documents
└── course
    └── climate-data-analysis
        ├── environment.yml
        ├── python
        └── ...
```

The `climate-data-analysis` directory is your local copy of the course repository.

---
## Course Structure
The course consists of weekly hands-on sessions using Python and script-based workflows.

At the beginning of each class, open your terminal:

- **Mac:** Open Terminal or iTerm and use the default **zsh** shell.
- **Windows:** Open **WSL (Ubuntu)** and use the **Bash** shell.

Then go to the course repository and update your local repository:

```bash
cd climate-data-analysis
git pull origin main
```
This ensures that you are working with the latest course materials.

The course consists of weekly hands-on sessions using Python.

