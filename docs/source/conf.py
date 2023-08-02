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


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/rapids_logo.png"
html_static_path = ["_static"]

# Removes sidebar
htmlhelp_basename = "cuxfilterdoc"

html_sidebars = {
  "user_guide/index": []
}

html_theme_options = {
    "external_links": [],
    "icon_links": [],
    "github_url": "https://github.com/rapidsai/cuxfilter",
    "twitter_url": "https://twitter.com/rapidsai",
    "show_toc_level": 1,
    "navbar_align": "right",
}


def setup(app):
    app.add_css_file("https://docs.rapids.ai/assets/css/custom.css")
    app.add_js_file("https://docs.rapids.ai/assets/js/custom.js", loading_method="defer")
