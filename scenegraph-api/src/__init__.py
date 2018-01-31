"""Provides global information about scenegraph api."""
from src.ioc import ScenegraphApiContainer

API_VERSION = "{0}.{1}".format(
  ScenegraphApiContainer.api_meta.version["major"],
  ScenegraphApiContainer.api_meta.version["minor"])
