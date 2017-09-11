"""Provides the foundation for working with specific exceptions belonging to the platform.
We can extend the range of exceptions by simply subclassing exceptions from this module."""

from bravehub_shared.exceptions.error_codes import ErrorCodes

class BravehubPlatformException(Exception):
  """This is the top most exception for describing error cases from the platform. All other
  exceptions will subclass this."""

  def __init__(self, message=None, inner_ex=None, headers=None):
    super(BravehubPlatformException, self).__init__(message)
    self._inner_ex = inner_ex
    self._headers = headers or {}

  @staticmethod
  def from_exception(ex):
    """Provides a simple mechanism from casting an exception to a bravehub platform exception."""

    return BravehubPlatformException(inner_ex=ex)

  @property
  def inner_ex(self):
    """Obtains the inner exception (if any available). Inner exception is available only if this
    exception instance wrapped another exception during exception bubbling."""

    return self._inner_ex

  @property
  def status_code(self):
    """Provides the http status code which will be reported to the client."""

    return 500

  @property
  def body(self):
    """Provides the body object sent to the client as a http response."""

    return self._from_error_code(ErrorCodes.RESOURCE_GENERIC_ERROR)

  @property
  def headers(self):
    """Provides the headers which must be returned to the end user."""

    return self._headers

  def _from_error_code(self, error_code): # pylint: disable=no-self-use
    return {
      "errorId": error_code.id,
      "errorCode": error_code.code,
      "errorDescription": error_code.description
    }

class BravehubNotImplementedException(BravehubPlatformException):
  """Provides a specific exception which tells end user a certain action is not currently
  implemented."""
  @property
  def status_code(self):
    return 501

  @property
  def body(self):
    return self._from_error_code(ErrorCodes.RESOURCE_NOT_IMPLEMENTED_ERROR)

class BravehubNotFoundException(BravehubPlatformException):
  """Provides a specific exception which tells end user a certain resource does not exist."""
  @property
  def status_code(self):
    return 404

  @property
  def body(self):
    return self._from_error_code(ErrorCodes.RESOURCE_NOT_FOUND)

class BravehubDuplicateEntryException(BravehubPlatformException):
  """Provides a specific exception which tells end user that a resource already exists."""
  def __init__(self, message=None, inner_ex=None, additional_data=None, headers=None):
    super(BravehubDuplicateEntryException, self).__init__(message, inner_ex, headers)
    self._body = self._from_error_code(ErrorCodes.RESOURCE_DUPLICATE_ENTRY)
    self._body.update(additional_data)

  @property
  def status_code(self):
    return 409

  @property
  def body(self):
    return self._body
