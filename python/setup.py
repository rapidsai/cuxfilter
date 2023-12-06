# Copyright (c) 2019-2023, NVIDIA CORPORATION.

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
