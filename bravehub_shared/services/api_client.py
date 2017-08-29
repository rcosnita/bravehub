"""This module provides the generic api client implementation for bravehub core micro services."""

class ApiClient(object):
  """The generic class for the api client."""

  def __init__(self, api_name, cluster_suffix):
    self._api_name = api_name
    self._cluster_suffix = cluster_suffix

  @property
  def api_name(self): # pylint: disable=missing-docstring
    return self._api_name

  @property
  def cluster_suffix(self): # pylint: disable=missing-docstring
    return self._cluster_suffix

  def __str__(self):
    return "Api name: {0}---->Cluster suffix: {1}".format(self.api_name, self.cluster_suffix)
