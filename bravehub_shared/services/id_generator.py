"""Provides the logic for generating unique identifiers which can be used as primary keys for our
resources."""

import uuid

class IdGeneratorService(object):
  """Provides a simple implementation which relies on uuid module from python."""

  def __init__(self, charset):
    self._charset = charset

  def generate(self): # pylint: disable=no-self-use
    """Generate a unique identifier represented as string."""

    return str(uuid.uuid4())

  def generate_bytes(self):
    """Generate a unique identifier represented as bytes."""

    return bytes(self.generate(), self._charset)

  def to_bytes(self, uid):
    """Convert the given id to bytes representation."""
    return bytes(uid, self._charset)

  def to_string(self, uid):
    """Convert the given bytes belonging to an id to a string representation."""
    return uid.decode(self._charset)
