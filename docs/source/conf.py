# Copyright (c) 2019-2023, NVIDIA CORPORATION.
import pydata_sphinx_theme

# -- Project information -----------------------------------------------------
project = "cuxfilter"
copyright = "2018-2023, NVIDIA Corporation"
author = "NVIDIA Corporation"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '23.08'
# The full version, including alpha/beta/rc tags
release = '23.08.00'

# Allow errors in all notebooks by setting this option
# https://nbsphinx.readthedocs.io/en/0.2.7/allow-errors.html
# 
nbsphinx_allow_errors = True


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_markdown_tables",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
    "nbsphinx",
    "recommonmark",
    "jupyter_sphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = {".rst": "restructuredtext"}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# Output file base name for HTML help builder. Default is 'pydoc'
#
htmlhelp_basename = "cuxfilterdoc"

# -- Options for HTML output -------------------------------------------------

# PyData Theme Options
# https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html
#
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ['css/custom.css'] # temp

html_theme_options = {
    "logo": {"text": project},
    "external_links": [
        {"name": "Ecosystem", "url": "https://rapids.ai/ecosystem"},
        {"name": "Learn More", "url": "https://rapids.ai/learn-more"},
        {"name": "News", "url": "https://rapids.ai/news"},
        {"name": "User Guides", "url": "https://rapids.ai/user-guides"},
        {"name": "API Docs", "url": "https://rapids.ai/api"},
        {"name": "Install", "url": "https://rapids.ai/install"}
    ],
    "header_links_before_dropdown": 2, # note: change based on number of top level directories
    "announcement": "https://raw.githubusercontent.com/rapidsai/sphinx-theme/main/_static/rapids-nav.html", # static
    "icon_links": [],
    "github_url": f"https://github.com/rapidsai/{project}",
    "twitter_url": "https://twitter.com/rapidsai",
    "show_toc_level": 2,
    "navbar_align": "left",
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher.html","navbar-icon-links.html"],
    "switcher": { 
        "version_match": version,
        "json_url": f"https://raw.githubusercontent.com/rapidsai/sphinx-theme/main/_static/versions/{project}-doc-versions.json"
    }
}


# NOTE TO DO:
# works well, but need to fix scroll behavior and z index