import os
import sys

from django import setup as django_setup
from django.conf import settings

# from django.conf import settings
# sys.path.insert(0, os.path.abspath('../../purchases/'))
# sys.path.insert(0, os.path.normpath('C:/Users/karl.wooster/repos/wsutc/SEAS-purchase-system/'))
sys.path.insert(
    0, os.path.abspath("../..")
)  # 'C:/Users/karl.wooster/repos/wsutc/SEAS-purchase-system/purchases/')
print("Path: {}".format(sys.path[0]))

os.environ["DJANGO_SETTINGS_MODULE"] = "web_project.settings"

django_setup()

# settings.configure()

# print(getattr(settings, "BASE_DIR"))

# settings_loc = 'web_project.settings'
# print("Settings Location: {}".format(settings_loc))

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_loc)

print(getattr(settings, "BASE_DIR"))

# print("Read Variable: {}".format(os.environ.get("DJANGO_SETTINGS_MODULE")))

# print("Setting: {}".format(FILTERVIEW_SHOW_ALL))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "SEAS Purchase System"
copyright = "2022, Karl Wooster"
author = "Karl Wooster"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
