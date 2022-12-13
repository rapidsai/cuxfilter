# Contributing to cuxfilter

If you are interested in contributing to cuxfilter, your contributions will fall
into three categories:
1. You want to report a bug, feature request, or documentation issue
    - File an [issue](https://github.com/rapidsai/cuxfilter/issues/new/choose)
    describing what you encountered or what you want to see changed.
    - The RAPIDS team will evaluate the issues and triage them, scheduling
    them for a release. If you believe the issue needs priority attention
    comment on the issue to notify the team.
2. You want to propose a new Feature and implement it
    - Post about your intended feature, and we shall discuss the design and
    implementation.
    - Once we agree that the plan looks good, go ahead and implement it, using
    the [code contributions](#code-contributions) guide below.
3. You want to implement a feature or bug-fix for an outstanding issue
    - Follow the [code contributions](#code-contributions) guide below.
    - If you need more context on a particular issue, please ask and we shall
    provide.

## Code contributions

### Your first issue

1. Read the project's [README.md](https://github.com/rapidsai/cuxfilter/blob/main/README.md)
    to learn how to setup the development environment
2. Find an issue to work on. The best way is to look for the [good first issue](https://github.com/rapidsai/cuxfilter/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
    or [help wanted](https://github.com/rapidsai/cuxfilter/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) labels
3. Comment on the issue saying you are going to work on it
4. Code! Make sure to update unit tests!
5. When done, [create your pull request](https://github.com/rapidsai/cuxfilter/compare)
6. Verify that CI passes all [status checks](https://help.github.com/articles/about-status-checks/). Fix if needed
7. Wait for other developers to review your code and update code as needed
8. Once reviewed and approved, a RAPIDS developer will merge your pull request

Remember, if you are unsure about anything, don't hesitate to comment on issues
and ask for clarifications!

### Seasoned developers

Once you have gotten your feet wet and are more comfortable with the code, you
can look at the prioritized issues of our next release in our [project boards](https://github.com/rapidsai/cuxfilter/projects).

> **Pro Tip:** Always look at the release board with the highest number for
issues to work on. This is where RAPIDS developers also focus their efforts.

Look at the unassigned issues, and find an issue you are comfortable with
contributing to. Start with _Step 3_ from above, commenting on the issue to let
others know you are working on it. If you have any questions related to the
implementation of the issue, ask them in the issue instead of the PR.

## Attribution
Portions adopted from https://github.com/pytorch/pytorch/blob/master/CONTRIBUTING.md

## Setting up your build environment

The following instructions are for developers and contributors to cuxfilter OSS development. These instructions are tested on Linux Ubuntu 16.04 & 18.04. Use these instructions to build cuxfilter from source and contribute to its development.  Other operating systems may be compatible, but are not currently tested.

### Code Formatting

#### Python

cuxfilter uses [Black](https://black.readthedocs.io/en/stable/) and
[flake8](http://flake8.pycqa.org/en/latest/) to ensure a consistent code format
throughout the project. `Black` and `flake8` can be installed with
`conda` or `pip`:

```bash
conda install black flake8
```

```bash
pip install black flake8
```

These tools are used to auto-format the Python code in the repository.
Additionally, there is a CI check in place to enforce
that committed code follows our standards. You can use the tools to
automatically format your python code by running:

```bash
black python/cuxfilter
```

and then check the syntax of your Python by running:

```bash
flake8 python/cuxfilter
```

Additionally, many editors have plugins that will apply `Black` as
you edit files, as well as use `flake8` to report any style / syntax issues.

Optionally, you may wish to setup [pre-commit hooks](https://pre-commit.com/)
to automatically run `Black`, and `flake8` when you make a git commit.
This can be done by installing `pre-commit` via `conda` or `pip`:

```bash
conda install -c conda-forge pre_commit
```

```bash
pip install pre-commit
```

and then running:

```bash
pre-commit install
```

from the root of the cuxfilter repository. Now `Black` and `flake8` will be
run each time you commit changes.

## Script to build cuxfilter from source

### Build from Source

To install cuxfilter from source, ensure the dependencies are met and follow the steps below:

- Clone the repository and submodules
```bash
CUXFILTER_HOME=$(pwd)/cuxfilter
git clone https://github.com/rapidsai/cuxfilter.git $CUXFILTER_HOME
cd $CUXFILTER_HOME
```
- Create the conda development environment `cuxfilter_dev`:
```bash
# create the conda environment (assuming in base `cuxfilter` directory)
conda env create --name cuxfilter_dev --file conda/environments/all_cuda-115_arch-x86_64.yaml
# activate the environment
source activate cuxfilter_dev
```

- Build the `cuxfilter` python packages, in the `python` folder:
```bash
$ cd $CUXFILTER_HOME/python
$ python setup.py install
```

- To run tests (Optional):
```bash
$ cd $CUXFILTER_HOME/python/cuxfilter/tests
$ pytest
```

Done! You are ready to develop for the cuxfilter OSS project

### Adding support for new viz libraries

cuxfilter.py acts like a connector library and it is easy to add support for new libraries. The cuxfilter/charts/core directory has all the core chart classes which can be inherited and used to implement a few (viz related) functions and support dashboarding in cuxfilter directly.

You can see the examples to implement viz libraries in the bokeh and datashader directories. 

Current plan is to add support for the following libraries apart from bokeh and datashader:
1. deckgl

Open a feature request for requesting support for libraries other than the above mentioned ones.