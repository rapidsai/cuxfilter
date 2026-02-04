# SPDX-FileCopyrightText: Copyright (c) 2023-2026, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

import importlib.resources

__version__ = (
    importlib.resources.files(__package__)
    .joinpath("VERSION")
    .read_text()
    .strip()
)

__rapids_branch__ = (
    importlib.resources.files(__package__)
    .joinpath("RAPIDS_BRANCH")
    .read_text()
    .strip()
)

try:
    __git_commit__ = (
        importlib.resources.files(__package__)
        .joinpath("GIT_COMMIT")
        .read_text()
        .strip()
    )
except FileNotFoundError:
    __git_commit__ = ""

__all__ = ["__git_commit__", "__rapids_branch__", "__version__"]
