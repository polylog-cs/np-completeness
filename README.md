# NP-completeness

Video about NP-completeness, circuit SAT and "reversing time"

## Setup

The dependencies are managed via [Poetry](https://python-poetry.org/).
To install the project, first get Poetry via `pip install poetry`.
Next, run `poetry install` to install the dependencies.
Poetry uses a lockfile (`poetry.lock`) to keep track of the *exact* versions
of packages to be installed.

If you have a [virtualenv](https://virtualenv.pypa.io/en/latest/)
or [Conda env](https://docs.anaconda.com/miniconda/) activated,
Poetry will install the dependencies into this environment.
Otherwise, it will [create a new virtualenv for you](https://python-poetry.org/docs/configuration/#virtualenvsin-project).

You can then run commands in this environment by starting your command with `poetry run`,
e.g. `poetry run manim -pql anims.py Polylogo`.
If you don't want to prefix everything with `poetry run`, you can either
- run `poetry shell`, which creates a subshell with the environment activated
- identify the location of the virtualenv via `poetry run which python`.
  You should get a path like `$SOME_PATH/bin/python`.
  You can run `source $SOME_PATH/bin/activate` to activate the virtualenv,
  just [like you would normally](https://docs.python.org/3/library/venv.html#how-venvs-work).

## Pre-commit hooks

To install pre-commit hooks that check the code for correct formatting etc.:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook pre-push
```
