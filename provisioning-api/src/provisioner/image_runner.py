"""Provides the class for running a specific image on the current infrastructure."""

from abc import ABC, abstractmethod

from bravehub_shared.utils.hbase_connection_manager import HbaseConnectionManager
from bravehub_shared.utils.row_locker import OptimisticLocker

class ImageRunnerContext(object):
  """Provides a model for passing all required attributes for running a service."""

  def __init__(self, image_tag, public_ports):
    self._image_tag = image_tag
    self._public_ports = public_ports

  @property
  def image_tag(self):  # pylint: disable=missing-docstring
    return self._image_tag

  @property
  def public_ports(self):  # pylint: disable=missing-docstring
    return self._public_ports

class ImageRunner(ABC):
  """Provides the contract which must be implemented by each image runner. Depending on the
  orchestrator we want to use we are going to use a specific runner."""

  def __init__(self, hbase_conn_pool, default_charset, metaports_mapping_service):
    self._hbase_conn_pool = hbase_conn_pool
    self._default_charset = default_charset
    self._metaports_mapping_service = metaports_mapping_service

  @property
  def conn_pool(self):  # pylint: disable=missing-docstring
    return self._hbase_conn_pool

  def run_image(self, image_ctx, runner_ctx):
    """Provides the algorithm for running a docker image based on the given context."""

    public_ports = runner_ctx.public_ports

    port_mappings = {"{0}/tcp".format(port): None  for port in public_ports}
    self._choose_ports(image_ctx, runner_ctx, port_mappings)
    network_name = self._create_network(image_ctx, runner_ctx, port_mappings)
    self._deploy_image(image_ctx, runner_ctx, port_mappings, network_name)

  def _choose_ports(self, image_ctx, runner_ctx, port_mappings):  # pylint: disable=unused-argument
    for port in port_mappings.keys():
      public_port = self._reserve_next_free_port(image_ctx)

      if not public_port:
        # TODO(cosnita) add proper recovery mechanism.
        raise ValueError("Unable to find a public port")

      port_mappings[port] = public_port

    self._save_port_mappings(image_ctx, port_mappings)

  @abstractmethod
  def _create_network(self, image_ctx, runner_ctx, port_mappings):
    """Provides the logic for creating an isolated network for the service. It returns the
    newly created network id."""
    pass

  @abstractmethod
  def _deploy_image(self, image_ctx, runner_ctx, port_mappings, network_name):
    """Provides the logic for deploying the image on the underlining infrastructure."""
    pass

  @HbaseConnectionManager()
  def _reserve_next_free_port(self, image_ctx, hbase_manager=None):
    """It relies on the hbase provisioningmetaports table in order to obtain an available port. It
    uses an optimistic locking strategy in order to solve the potential concurrency issues."""

    conn = hbase_manager.connection
    ports_tbl = conn.table("provisioningmetaports")

    port_record = ports_tbl.scan(filter="SingleColumnValueFilter('attrs','status',=,'binary:free')",
                                 limit=1)

    try:
      port_record = next(port_record)
    except StopIteration:
      # TODO(cosnita) implement proper signaling for missing ports
      raise ValueError("No free ports ... Go away ...")

    port_id = port_record[0]
    port_id_str = port_id.decode(self._default_charset)

    # We know that the format is guid-port -> used for making sure we don't end up with a hot
    # region.
    port = port_id_str[port_id_str.rfind("-") + 1:]
    expected_status = bytes(image_ctx.api_id, self._default_charset)

    with OptimisticLocker(self._hbase_conn_pool, self._default_charset, "provisioningmetaports",
                          port_id,
                          when_acquired=lambda conn, tbl: \
                            tbl.put(port_id, {b"attrs:status": expected_status})) as lock:
      if not lock.locked:
        return

      return int(port)

  def _save_port_mappings(self, image_ctx, port_mappings):
    """Stores the association between apis and reserved ports. This actually accelerates
    the provisioning api responsible for retrieving the location of a specific domain and path."""

    self._metaports_mapping_service.save_port_mappings(image_ctx.api_id, port_mappings)

class DockerEngineImageRunner(ImageRunner):
  """Provides an implementation for the docker engine. This is designed to work on development
  environments."""

  def __init__(self, hbase_conn_pool, default_charset, metaports_mapping_service, docker_client):
    super(DockerEngineImageRunner, self).__init__(hbase_conn_pool, default_charset,
                                                  metaports_mapping_service)
    self._docker_client = docker_client

  def _create_network(self, image_ctx, runner_ctx, port_mappings):
    network_name = image_ctx.project_id

    existing_network = self._docker_client.networks.list(names=[network_name])

    if not existing_network:
      self._docker_client.networks.create(network_name, driver="bridge")

    return network_name

  def _deploy_image(self, image_ctx, runner_ctx, port_mappings, network_name):
    image_tag = runner_ctx.image_tag
    self._docker_client.containers.run(image_tag, auto_remove=True, network=network_name,
                                       detach=True, ports=port_mappings)
