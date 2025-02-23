# Environment Setup

This tutorial is based on Windows environment
You can set up your python environment via Python + venv or directly via Anaconda

## Install Python and set up virtual environment

### 1. Use WinPython + Venv + Pip

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
├─ app_backend
```

Navigate to Your Project Directory and then create a Virtual Environment.
After virtual environment is created. Activate the Virtual Environment

```sh
cd .\drf-subscription-app-tutorial\app_backend
python -m venv env
.\env\Scripts\activate
```

#### c. Set up Djnago project and start the server

create django package

```sh
pip install django==5.0.0
django-admin backend backend .
python manage.py migrate
python manage.py runserver
```

You can now see the Django server up and running at `http://localhost:8000/`

#### d. prepare basic libraries

In the next step, we need to prepare essential libraries for our Django project.

Create a `requirements.txt` under `app_backend` with following contents:

```plaintext
django-cors-headers==4.2.0
djangorestframework==3.15.0
requests==2.32.3
```

> **how to check library version**:
>
> The available library versions can be checked from [Python Package Index](https://pypi.org/)

Then install basic libraries from requirements.txt

```sh
pip install -r requirements.txt

 # check installation
pip list
```

The project structure after `django-admin startproject backend .` will be:

```plaintext
drf-subscription-app-tutorial/
├─ app_backend/
│  ├─ backend/
│  ├─ manage.py
│  ├─ requirements.txt
```

> For Unix-based systems, You can achieve above by:
>
> ```bash
> mkdir drf-subscription-app-tutorial && cd drf-subscription-app-tutorial
> mkdir app_backend && cd app_backend
> python3.12 -m venv env
> source env/bin/activate
> 
> pip install django==5.0.0
> django-admin backend backend .
> python manage.py migrate
> python manage.py runserver
> ```

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

#### b. Set up virtual environment by Anaconda

set up the structure of project directory as following:

```plaintext
drf-subscription-app-tutorial/
├─ app_backend
```

Navigate to Your Project Directory and then create a Virtual Environment.

```sh
cd .\drf-subscription-app-tutorial\app_backend
conda create --name env python=3.12
conda activate env
```

#### c. Set up Djnago project and start the server in Conda

create django package

```sh
conda install django=4.2.3
django-admin backend backend .
python manage.py migrate
python manage.py runserver
```

You can now see the Django server up and running at `http://localhost:8000/`

#### d. prepare basic libraries in Conda

For conda, it is better to install the required libraries from `conda` if the libraries are available in conda.

For packages that are not available in `conda`, you can then use `pip`

```bash
conda install djangorestframework=3.15.0
conda install django-cors-headers=4.2.0
conda install requests=2.32.3
```

To maintain the environment information, we need to export the conda env:

```bash
conda env export --from-history > environment.yml

# The environment can be recreated with:
conda env create -f environment.yml

# if package is not available in conda, you need to download via pip and maintain these pip libraries in environment.yml manually
```

`environment.yml` will look like this:

```yaml
name: myenv
channels:
  - defaultss
  - conda-forge
dependencies:
  - python=3.12
  - django=5.0.0
  - djangorestframework=3.15.0
  - django-cors-headers=4.2.0
  - requests=2.32.3
  - pip
  - pip:
    - some-package-only-on-pip==1.2.3
```

> We will use venv + pip solution in this tutorial
>
> The deployment in the later tutorial will also use requirements.txt to maintain the packages

## Bring the project to Github

### a. Create a GitHub Repository

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
