"""Provides all the error codes currently available in the bravehub platform. Each microservice
developer will add new error codes as needed."""
from enum import Enum

from bravehub_shared.utils.dynamic_object import DynamicObject

class ErrorCodes(Enum): # pylint: disable=too-few-public-methods
  """Error codes available in the platform. Each specific error code has a descriptor which provides
  additional details to the end user."""

  RESOURCE_GENERIC_ERROR = DynamicObject({
    "id": "RESOURCE.0",
    "code": "RESOURCE.GENERIC_ERROR",
    "description": "Something unexpected occurred on the server."
  })

  RESOURCE_NOT_FOUND = DynamicObject({
    "id": "RESOURCE.1",
    "code": "RESOURCE.NOTFOUND",
    "description": "The requested resource does not exist."
  })

  RESOURCE_DUPLICATE_ENTRY = DynamicObject({
    "id": "RESOURCE.2",
    "code": "RESOURCE.DUPLICATED",
    "description": "The current resource is duplicated. See Location header for more information."
  })

  RESOURCE_NOT_IMPLEMENTED_ERROR = DynamicObject({
    "id": "RESOURCE.9999",
    "code": "RESOURCE.NOT_IMPLEMENTED",
    "description": "The current operation is not implemented."
  })
