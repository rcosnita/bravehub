"""Provides the class for running a specific image on the current infrastructure."""

from abc import ABC, abstractmethod

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

  def __init__(self, hbase_conn_pool, default_charset, metaports_service):
    self._hbase_conn_pool = hbase_conn_pool
    self._default_charset = default_charset
    self._metaports_service = metaports_service

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
    api_id = image_ctx.api_id
    for port in port_mappings.keys():
      public_port = self._metaports_service.get_port_mappings(api_id)
      if not public_port:
        public_port = self._metaports_service.reserve_next_free_port(api_id)

      if not public_port:
        # TODO(cosnita) add proper recovery mechanism.
        raise ValueError("Unable to find a public port")

      port_mappings[port] = public_port

    self._metaports_service.save_port_mappings(api_id, port_mappings)

  @abstractmethod
  def _create_network(self, image_ctx, runner_ctx, port_mappings):
    """Provides the logic for creating an isolated network for the service. It returns the
    newly created network id."""
    pass

  @abstractmethod
  def _deploy_image(self, image_ctx, runner_ctx, port_mappings, network_name):
    """Provides the logic for deploying the image on the underlining infrastructure."""
    pass

class DockerEngineImageRunner(ImageRunner):
  """Provides an implementation for the docker engine. This is designed to work on development
  environments."""

  def __init__(self, hbase_conn_pool, default_charset, metaports_service, docker_client): # pylint: disable=line-too-long
    super(DockerEngineImageRunner, self).__init__(hbase_conn_pool, default_charset, metaports_service) # pylint: disable=line-too-long
    self._docker_client = docker_client

  def _create_network(self, image_ctx, runner_ctx, port_mappings):
    network_name = image_ctx.project_id

    existing_network = self._docker_client.networks.list(names=[network_name])

    if not existing_network:
      self._docker_client.networks.create(network_name, driver="bridge")

    return network_name

  def _deploy_image(self, image_ctx, runner_ctx, port_mappings, network_name):
    image_tag = runner_ctx.image_tag

    #check if this is an existing API and stop the current container if it's going
    running_container = [c for c in self._docker_client.containers.list()
                         if c.attrs['Config']['Image'] == image_tag]
    if running_container:
      running_container[0].remove(v=True, force=True) # also remove volume.
    self._docker_client.containers.run(image_tag, auto_remove=True, network=network_name,
                                       detach=True, ports=port_mappings)
