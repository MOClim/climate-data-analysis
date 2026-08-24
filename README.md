# Climate Data Analysis

Course materials for climate data analysis using Python and NCL.

## Getting Started

If `conda` is not installed, see "Environment Setup" below first.

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

At the beginning of every class, open the terminal and start a Bash shell:

`bash`

Then go to the course repository and update your local repository:
```bash
cd climate-data-analysis
git pull origin main
```
This ensures that you are working with the latest course materials.

The course consists of weekly hands-on sessions using Python, followed by script-based workflows and NCL.

---
---
# One-time setup

## 1. Environment Setup (Miniconda)

If you do not have `conda` installed yet, follow the steps below.

---
### For Windows users

#### Install Windows Subsystem for Linux (WSL) (Windows)

Install WSL:

1. Click Windows Software on the bottom menu bar
2. Type Ubuntu and choose Ubuntu App (with orange icon)
3. Click Download icon and Open

---

#### Install Miniconda (Windows)

1. Type WSL from the Search (on the bottom menu)
2. Open WSL
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

---

### For Mac users

#### Install iTerm2 (Mac)

The default macOS Terminal is sufficient, but iTerm2 provides a better interface.

Install iTerm2:

1. Download from: https://iterm2.com
2. Open the downloaded file
4. Drag iTerm into the Applications folder
5. Launch iTerm

---

#### Install Miniconda (Mac)

Download Miniconda from:

https://docs.anaconda.com/free/miniconda/

Choose the correct version:

- Mac (Apple Silicon: M1/M2/M3/M4/M5) → Apple Silicon
- Mac (Intel) → Intel x86
- Windows → 64-bit
  
---

### 2. PATH setting
PATH is a list of directories where the operating system looks for executable programs when you type a command in the terminal.

For example, when you type:

conda

the shell searches the directories listed in PATH to find the conda program. If the Miniconda directory is not included in PATH, the terminal may return an error such as:

conda: command not found

Adding the Miniconda bin directory to PATH allows you to run conda from any directory in the terminal.

Open terminal:
- Mac → Terminal or iTerm
- Windows → Windows Subsystem for Linux (WSL) 

Check the default shell
```bash
echo $SHELL
```

Windows:
```bash
/bin/bash
```

On a typical modern Mac, you should see:
```bash
/bin/zsh
```
and then add Path for .zshrc for Mac.
```bash
bash
nano ~/.zshrc
```

Check this file:
```bash
less ~/.zshrc
```
You should see:
Windows
```bash
export PATH="/root/miniconda3/bin:$PATH"
```

Mac
```bash
export PATH="/opt/miniconda3/bin:/bin:/usr/bin:/usr/local/bin:$PATH"
```
Press the **Space** key to scroll down and q to exit.

If you want to edit this file, and open it in nano (text editor):
```bash
nano ~/.zshrc
```
Three operations to save and exit the file:
```bash
Edit text

Ctrl + O     Save
Enter        Confirm filename
Ctrl + X     Exit
```

### 3. Initialize Conda
Run:
```bash
conda init
```
Restart your terminal.

---

### 4. Verify Installation

```bash
conda --version
```
