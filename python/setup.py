# Copyright (c) 2019-2023, NVIDIA CORPORATION.

from setuptools import find_packages, setup

setup(
    packages=find_packages(
        include=["cuxfilter", "cuxfilter.*"],
        exclude=("tests", "docs", "notebooks"),
    ),
    package_data={"cuxfilter.themes.assets": ["*.css", "*.html"]},
    zip_safe=False,
)
