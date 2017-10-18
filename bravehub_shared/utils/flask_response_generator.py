"""Provides a smart decorator which can transform micro services responses to flask compatible
response. This comes handy for standardizing the way exceptions and error messages are propagated
to the end user."""

import json

from bravehub_shared.utils.dynamic_object import DynamicObject
from bravehub_shared.exceptions.bravehub_exceptions import BravehubPlatformException
from bravehub_shared.services.base_service import PLATFORM_DEBUG

class PaginatedResponse(DynamicObject):
  """Provides a simple model for describing paginated results to clients."""

  def __init__(self, items):
    super().__init__()
    self._items = items

    self.update({
      "items": self._items,
      "startRecord": None,
      "endRecord": None,
      "previous": None,
      "next": None,
      "limit": None
    })

class FlaskResponseGenerator(object):
  """This is a method decorator which transform the return value of a method to a serializable
  flask response.

  In addition it correctly handles exceptions raised from the service."""

  def __init__(self, app_attr="flask_app", is_debug=None):
    self._app_attr = app_attr
    self._is_debug = is_debug or PLATFORM_DEBUG

  @property
  def app_attr(self): # pylint: disable=missing-docstring
    return self._app_attr

  def handle(self, method): # pylint: disable=missing-docstring
    def handle_method(*args, **kwargs): # pylint: disable=missing-docstring
      fn_self = args[0]
      flask_app = getattr(fn_self, self._app_attr)

      platform_ex = None

      try:
        result = method(*args, **kwargs)
        headers = None
        status_code = None

        if isinstance(result, tuple):
          (result, status_code, headers) = result

        empty_body = not result
        body = None

        if isinstance(result, flask_app.response_class):
          return result

        if not isinstance(result, dict) and self._is_file_like(result):
          return flask_app.send_file(result, mimetype="application/octet-stream")

        if not empty_body:
          body = json.dumps(result)
          status_code = status_code or 200
        else:
          body = ""
          status_code = status_code or 204

        return flask_app.response_class(response=body,
                                        status=status_code,
                                        mimetype="application/json",
                                        headers=headers)
      except BravehubPlatformException as ex:
        platform_ex = ex
      except Exception as ex: # pylint: disable=broad-except
        if self._is_debug:
          raise ex

        # TODO(cosnita) Log the generic exception in the application log.
        platform_ex = BravehubPlatformException(ex)

      response = flask_app.response_class(response=json.dumps(platform_ex.body),
                                          status=platform_ex.status_code,
                                          mimetype="application/json",
                                          headers=platform_ex.headers)

      return response

    handle_method.__doc__ = method.__doc__

    return handle_method

  def __call__(self, method):
    return self.handle(method)

  def _is_file_like(self, result): # pylint: disable=no-self-use
    return result and (hasattr(result, "read") or hasattr(result, "write"))
