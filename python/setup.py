# SPDX-FileCopyrightText: Copyright (c) 2019-2023, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0

from setuptools import find_packages, setup

packages = find_packages(
    include=["cuxfilter", "cuxfilter.*"],
    exclude=("tests", "docs", "notebooks"),
)

setup(
    packages=packages,
    package_data={key: ["VERSION"] for key in packages},
    zip_safe=False,
)
