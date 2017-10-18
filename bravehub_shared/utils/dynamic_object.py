"""Provides a very simple implementation which creates dynamic objects starting from a dictionary.
"""

class DynamicObject(dict):
  """Provides a simple wrapper which allows us to simulate an object based on the dictionary
  keys."""

  def __init__(self, data=None):
    super().__init__()
    self._data = data or {}
    self.update(self._data)

  def __getattr__(self, name):
    value = super(DynamicObject, self).get(name)

    if isinstance(value, dict):
      return DynamicObject(value)

    return value
