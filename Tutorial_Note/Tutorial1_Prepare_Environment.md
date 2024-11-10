# Environment Setup

This tutorial is based on Windows environment
You can set up your python environment via Python + venv or directly via Anaconda

## Install Python and set up virtual environment

### 1. Use WinPython + Venv

#### a. Download Python

We use python **3.12.7** in this tutorial.

download and install Python from the [official website](https://www.python.org/downloads/). Follow the installation instructions for your operating system.

After downloading the Python, open Command Prompt, then try

```sh
python --V
```

>Q&A:
>
>**1. python command cannot be found**:
>
> the python command needs to be in your system's PATH. Here’s how to check and add it:
>
> * Open the Start menu and search for "Environment Variables".
> * Click on "Edit the system environment variables".
> * In the System Properties window, click on "Environment Variables".
> * In the Environment Variables window, under "System variables", find the Path variable, and click "Edit".
> * Click "New" and add the path to your python installation, typically:
>
>   ```makefile
>   C:\Users\xxhow\AppData\Local\Programs\Python\Python312\Scripts\
>   C:\Users\xxhow\AppData\Local\Programs\Python\Python312\
>   ```
>
>   After adding pathes, close and reopen Command Prompt to retry.
>

#### b. Set up virtual environment by venv

set up the structure of project directory as following:

```plaintext
drf-subscription-app-tutorial/
├─ requirements.txt
```

Inside the `requirements.txt`, enter few basic libraries:

```plaintext
Django==5.0.0
django-cors-headers==4.2.0
djangorestframework==3.15.0
requests==2.32.3
```

>Q&A:
>
>**1. how to check library version**:
>
> The available library versions can be checked from [Python Package Index](https://pypi.org/)
>

Navigate to Your Project Directory and then create a Virtual Environment.
After virtual environment is created. Activate the Virtual Environment

```sh
cd .\drf-subscription-app-tutorial
python -m venv env
.\env\Scripts\activate
```

Then install basic libraries from requirements.txt

```sh
cd .\backend
pip install -r requirements.txt
pip list  # check installation
```

### 2. Use Anaconda

#### a. Install Anaconda

download and install Anaconda from the [official website](https://docs.anaconda.com/free/anaconda/install/). Follow the installation instructions for your operating system.

After downloading the Anaconda, open Command Prompt, then try

```sh
conda --version
```

>Q&A:
>
>**1. Conda command cannot be found**:
>
> the conda command needs to be in your system's PATH. Here’s how to check and add it:
>
> * Open the Start menu and search for "Environment Variables".
> * Click on "Edit the system environment variables".
> * In the System Properties window, click on "Environment Variables".
> * In the Environment Variables window, under "System variables", find the Path variable, and click "Edit".
> * Click "New" and add the path to your Anaconda installation, typically:
>
>   ```makefile
>   C:\Users\YourUsername\Anaconda3
>   C:\Users\YourUsername\Anaconda3\Scripts
>   C:\Users\YourUsername\Anaconda3\Library\bin
>   ```
>
> After adding pathes, close and reopen Command Prompt to retry.
>
> **2. Conda command can run in Windows' powershell but cannot run in VSCode's powershell**:
>
> Please check the top solution in this [article](https://stackoverflow.com/questions/54828713/working-with-anaconda-in-visual-studio-code)
>

### 2. Set up virtual environment by Anaconda

set up the structure of project directory as following:

```plaintext
drf-subscription-app-tutorial/
├─ requirements.txt
```

Inside the `requirements.txt`, enter few basic libraries:

```plaintext
Django==5.0.0
django-cors-headers==4.2.0
djangorestframework==3.15.0
requests==2.32.3
```

>Q&A:
>
>**1. how to check library version via conda**:
>
> ```sh
> conda search Django
>
> # Sometimes a specific version may be available in a different channel. You can specify the channel during the search:
> conda search -c conda-forge django-cors-headers
>
> # To get more details about a specific version
> conda search Django=4.2.0 --info
> ```
>

Then download package from new created virtual environment

```sh
cd .\drf-subscription-app-tutorial
conda create --name env python=3.11
conda activate env
conda install pip
cd .\drf-subscription-app-tutorial
pip install -r requirements.txt
```

## Set up Djnago project and start the server

create django package

```sh
cd .\drf-subscription-app-tutorial
django-admin startproject backend
cd backend
python manage.py runserver
```

## Bring the project to Github

### a. Move requirement.txt to `/backend` and create `.gitignore` in the project folder

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
│  ├─ backend/
│  ├─ manage.py
│  ├─ requirements.txt
├─ .gitignore
```

### b. Create a GitHub Repository

* Go to [GitHub](https://github.com) and log in to your account.
* Click on the "+" icon at the top right corner and select "New repository".
* Fill in the repository name, description (optional), and choose the repository to be public or private.
* Click on "Create repository".

### c. Initialize Git in the Django Project Directory

Open a terminal or command promp and navigate to your Django project directory

```sh
# Set your global Git user name and email
git config --global user.name "Hao"
git config --global user.email "hao@example.com"

# Navigate to your project directory
cd ../drf-subscription-app-tutorial

# Initialize a new Git repository
git init

# Add all files to the repository
git add .

# Commit the files
git commit -m "setup project"

# Add the remote repository
git remote add origin https://github.com/yourusername/your-repository-name.git

# Push the committed files to the GitHub repository
git branch -M main
git push -u origin main
```
