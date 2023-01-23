from setuptools import find_packages, setup
import versioneer

with open("README.md") as f:
    readme = f.read()

setup(
    name="cuxfilter",
    version=versioneer.get_version(),
    description="GPU accelerated cross filtering with cuDF",
    url="https://github.com/rapidsai/cuxfilter",
    author="NVIDIA Corporation",
    license="Apache 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(
        include=["cuxfilter", "cuxfilter.*"],
        exclude=("tests", "docs", "notebooks"),
    ),
    package_data=dict.fromkeys(
        find_packages(
            include=["cuxfilter.layouts.assets", "cuxfilter.themes.assets"]
        ),
        ["*.css", "*.html"],
    ),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
)
