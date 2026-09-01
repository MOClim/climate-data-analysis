# One-time setup

1. Environment Setup (Miniconda)
2. PATH setting
3. Initialize Conda
4. Verify Installation
5. Install Git
6. Create the Course Virtual Environment

---

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

#### Install Miniconda on WSL (Windows)

1. Type WSL from the Search (on the bottom menu)
2. Open WSL
3. Check your CPU architecture
   
```bash
uname -m
```
- x86_64 → Intel/AMD architecture
- aarch64 → ARM architecture

4. Download the Minoconda package

For x86_64 users:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```
For aarch64 users:
```bash
wget wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
```

5. Install Miniconda

For x86_64 users:
```bash
sh Miniconda3-latest-Linux-x86_64.sh
```
For aarch64 users:
```bash
sh Miniconda3-latest-Linux-x86_64.sh
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

#### Install Miniconda (Mac)

Download Miniconda from:

https://docs.anaconda.com/free/miniconda/

Maybe direct link of the download page:
https://www.anaconda.com/download/success

Choose the correct version of *Miniconda*:
- Mac (Apple Silicon: M1/M2/M3/M4/M5) → Apple Silicon
- Mac (Intel) → Intel x86
- Windows → 64-bit
  
---

## 2. PATH setting

**PATH** is a list of directories where the operating system looks for executable programs 
when you type a command in the terminal.

For example, when you type:
```bash
conda --version
```
the shell searches the directories listed in PATH to find the conda program. 

If the Miniconda directory is not included in PATH, the terminal may return an error such as:
```bash
conda: command not found
```
Adding the Miniconda bin directory to PATH allows you to run `conda` from any directory in the terminal.

Open terminal:
- Windows → Windows Subsystem for Linux (WSL) 
- Mac → Terminal or iTerm

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
Check this file:
Windows:
```bash
less ~/.bashrc
```
Mac:
```bash
less ~/.zshrc
```
Press the **Space** key to scroll down and q to exit.

Add Path for `.bashrc` or `.zshrc`. Open the shell script in nano (text editor)
Windows:
```bash
nano ~/.bashrc
```
Add this command to the file.
```bash
export PATH="$HOME/miniconda3/bin:$PATH"
```

Mac:
```bash
nano ~/.zshrc
```
Add this command to the file.
```bash
export PATH="/opt/miniconda3/bin:$PATH"
```

Three operations to save and exit the file:
```bash
Edit text

Ctrl + O     Save
Enter        Confirm filename
Ctrl + X     Exit
```

Windows:
```bash
source ~/.bashrc
```
Mac:
```bash
source ~/.zshrc
```

---

## 3. Initialize Conda
Run:
```bash
conda init
```
Restart your terminal.

---

## 4. Verify Installation

```bash
conda --version
```

---

## 5. Install Git

**Git** is used to download and update the course materials from GitHub.

First, check whether Git is already installed. 
- For Windows users, open Windows Subsystem for Linux (WSL)
- For Mac users, open iTerm
```bash
git --version
```

If a Git version is displayed, you can skip the installation steps below.

### Windows (WSL)

Open WSL and run:

```bash
sudo apt update
sudo apt install git
```

### Mac
First, install Homebrew. Open Terminal or iTerm and run:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
After installation, follow the Next steps displayed in the Terminal to add Homebrew to your PATH.

Then install Git:
```bash
# Install Git
brew install git
```

### All students
After installation, verify Git:
```bash
# Check Git
git --version
```
---
## 6. Create the Course Virtual Environment

This course uses a Conda virtual environment to keep the Python version and required packages consistent.

First, go to the course directory:

**Windows**
```bash
cd /mnt/c/Users/<username>/Documents/course
```
**Mac**
```bash
cd ~/Documents/course
```

Clone the course repository:
```bash
git clone https://github.com/MOClim/climate-data-analysis.git
```

Move into the repository:
```bash
cd climate-data-analysis
```

Create the course environment using `environment.yml`:
```bash
conda env create -f environment.yml
```

Activate the environment:
```bash
conda activate climate-analysis
```

After activation, you should see:
```bash
(climate-analysis)
```
at the beginning of your terminal prompt.

Verify Python:
```bash
python --version
```

Note: You only need to create the environment once.
For future classes, activate it with:
```bash
conda activate climate-analysis
```
