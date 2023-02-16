# Copyright (c) 2019-2023, NVIDIA CORPORATION.
import sphinx_rtd_theme

# -- Project information -----------------------------------------------------
project = "cuxfilter"
copyright = "2019, NVIDIA"
author = "NVIDIA"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "23.04"
# The full version, including alpha/beta/rc tags
release = "23.04.00"

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

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


htmlhelp_basename = "cuxfilterdoc"


def setup(app):
    app.add_css_file("https://docs.rapids.ai/assets/css/custom.css")
    app.add_js_file(
        "https://docs.rapids.ai/assets/js/custom.js", loading_method="defer"
    )
