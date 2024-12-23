# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath("source/"))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath('../'))

project = 'twol'
copyright = '2020-2023, Kimmo Koskenniemi'
author = 'Kimmo Koskenniemi'
release = '0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = ['sphinxcontrib.bibtex']
# extensions = []

extensions = [
    'sphinx.ext.autodoc',
    "sphinx_autodoc_typehints",
#    'sphinx.ext.doctest',
#    'sphinx.ext.intersphinx',
#    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.graphviz',
#    'notfound.extension',
]
templates_path = ['_templates']

source_suffix = '.rst'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_build/_static']

graphviz_output_format = "png"

# -- Options for LaTeX/PDF output -----------------------------------------
#
latex_engine = 'xelatex'
latex_show_urls = 'footnote'

# -- Options for typehints ------------------------------------------------

always_document_param_types = True
#typehints_use_signature = True

