# SPDX-FileCopyrightText: 2024 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""Configuration file for sphinx documentation."""

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sphinx_rtd_theme

project = "circfirm"
copyright = "2024, Alec Delaney"
author = "Alec Delaney"
version = release = "0.0.0+auto.0"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_tabs.tabs",
    "sphinxcontrib.jquery",
]

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    "CircuitPython": ("https://docs.circuitpython.org/en/latest/", None),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), "."]
