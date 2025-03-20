# Alternative Python Package and Project Managers

## Table of Content

- [Poetry](#poetry)
- [Anaconda](#anaconda)
- [venv](#venv)

## Poetry <a id="poetry"></a>

Refer to the documentation [here](https://python-poetry.org/docs/#installing-with-the-official-installer) (recommended) on how to install Poetry based on your operating system.

> [!IMPORTANT]
> For macOS users, if encountering issues with `poetry command not found`, add `export PATH="$HOME/.local/bin:$PATH"` in your `.zshrc` file in your home folder and run `source ~/.zshrc`.

First create a virtual environment by running the following commands:

```bash
poetry shell
```

> [!TIP]
> If you see the following error; `The currently activated Python version 3.11.7 is not supported by the project (^3.12). Trying to find and use a compatible version.`, run:
>
> ```zsh
> poetry env use 3.12.3  # Python version used in the project
> ```

To install the defined dependencies for your project, just run the `install` command. The `install` command reads the [`pyproject.toml`](../pyproject.toml) file from the current project, resolves the dependencies, and installs them.

```bash
poetry install
```

If there is a `poetry.lock` file in the current directory, it will use the exact versions from there instead of resolving them. This ensures that everyone using the library will get the same versions of the dependencies.

If there is no `poetry.lock` file, Poetry will create one after dependency resolution.

> [!TIP]
> It is best practice to commit the poetry.lock to version control for more reproducible builds. For more information, refer [here](https://python-poetry.org/docs/basic-usage/#:~:text=changes%20in%20dependencies.-,Committing%20your%20poetry.lock%20file%20to%20version%20control,-As%20an%20application).

## Anaconda <a id="anaconda"></a>

> [!IMPORTANT]
> If you're using the `conda` package manager, please confirm with the repository adminstrator that the [`requirements.txt`](../requirements.txt) is in sync with [`pyproject.toml`](../pyproject.toml).

You can download the Anaconda Distribution for your respective operating system [here](https://www.anaconda.com/docs/getting-started/anaconda/install). You may also find out how to get started with Anaconda [here](https://www.anaconda.com/docs/getting-started/getting-started). To verify your installation, you can head to the Command Line Interface (CLI) and run the following command:

```bash
conda list
```

You should see a list of packages installed in your active environment and their versions displayed. For more information on Anaconda, refer [here](https://www.anaconda.com/docs/main).

Once set up, create a virtual environment using `conda` and install dependencies:

```bash
# Create a virtual environment
conda create -n agents python=3.12 -y
conda activate agents

# Install dependencies
pip install -r requirements.txt
```

## venv <a id="venv"></a>

> [!IMPORTANT]
> If you're using Python's native virtual environment `venv`, please confirm with the repository adminstrator that the [`requirements.txt`](../requirements.txt) is in sync with [`pyproject.toml`](../pyproject.toml).

You can use Python's native virtual environment `venv` to set up the project

```bash
# Create a virtual environment
python3 -m venv .venv
```

You can then activate the environment and install the dependencies using the following commands:

For Linux or macOS users:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

For Windows users:

```powershell
# Activate virtual environment
./venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

> [!TIP]
> If you're using Python's native virtual environment `venv`, it is best practice to name your virtual environment `.venv`.
