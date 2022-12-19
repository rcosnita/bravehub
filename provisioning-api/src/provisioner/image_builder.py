"""Provides the class for creating self contained build images. These can be easily deployed
using a custom provisioner provider."""

from abc import ABC, abstractmethod
import io
import os
import tarfile

from bravehub_shared.utils.dynamic_object import DynamicObject

class ImageBuilderContext(object):
  """Provides the model on which every image builder provider can rely on. It is the
  translation layer between bravehub platform data model and the physical orchestrator."""

  def __init__(self, project_id, api_id, build_num, config_data):
    self._project_id = project_id
    self._api_id = api_id
    self._build_num = build_num
    self._config_data = config_data

    build_data = [DynamicObject(build)
                  for build in config_data.builds
                  if str(build["build"]) == str(build_num)]
    self._build_data = build_data[0]

  @property
  def project_id(self):  # pylint: disable=missing-docstring
    return self._project_id

  @property
  def api_id(self):  # pylint: disable=missing-docstring
    return self._api_id

  @property
  def build_num(self):  # pylint: disable=missing-docstring
    return self._build_num

  @property
  def config_data(self):  # pylint: disable=missing-docstring
    return self._config_data

  @property
  def build_data(self):  # pylint: disable=missing-docstring
    return self._build_data

class ImageBuilder(ABC):  # pylint: disable=too-few-public-methods
  """Provides the interface which must be implemented by an image builder."""

  @abstractmethod
  def build_image(self, context):
    """Builds an image in the provider's binary format. Returns the image tag once the build process
    is complete."""
    pass

class DockerImageBuilder(ImageBuilder):  # pylint: disable=too-few-public-methods
  """Provides a docker based image builder. It relies on the docker sdk for python."""

  def __init__(self, file_system, docker_client, default_charset):
    self._file_system = file_system
    self._docker_client = docker_client
    self._default_charset = default_charset

  def build_image(self, context):
    """Based on the given context, this method aggregates all assets into a single image.
    Based on the image type, it installs some dependencies so that the application will
    run as expected."""
    image_folder = os.path.join("projects", context.project_id, "images", "apis", context.api_id,
                                str(context.build_num))
    image_folder_abs = self._file_system.absolute_path(image_folder)

    self._file_system.rmdir(image_folder)

    self._generate_build_files(context, image_folder)
    self._generate_dockerfile(context, image_folder)

    image_tag = "bravehub/{0}-{1}:{2}".format(context.project_id, context.api_id,
                                              context.build_num)
    self._docker_client.images.build(path=image_folder_abs, tag=image_tag, forcerm=True,
                                     nocache=True, quiet=False)

    return image_tag

  def _generate_build_files(self, context, image_folder):
    """Download all binary files, configuration and assets which must be made available
    to the container."""

    # Download environment variables
    self._generate_env_file(context.build_data.configuration.environment, image_folder)

    # Download configuration assets
    self._download_configuration_assets(context.build_data.configuration.assets, image_folder)

    # Download droplet
    self._download_droplet(context.build_data.configuration.droplet, image_folder)

  def _generate_env_file(self, env_data, image_folder):
    """Based on the environemnt variables returned by configuration api we generate
    a script containing the adequate exports."""
    # TODO(cosnita) make sure the file is compatible with the underlining OS.

    content = "\n".join([
      "export {key}={value}".format(key=data["key"], value=data["value"])
      for data in env_data
    ])

    file_name = "bravehub-environment.sh"
    self._file_system.store(file_name, io.BytesIO(bytes(content, self._default_charset)),
                            image_folder)

  def _download_configuration_assets(self, assets, image_folder):
    """Base on the list of assets we put all files together in the correct locations."""

    for asset in assets:
      asset = DynamicObject(asset)
      asset_path = asset.downloadPath
      asset_dest = os.path.join(image_folder, asset.mountPath[1:])
      self._file_system.cp(asset_path, asset_dest)

  def _download_droplet(self, droplet_data, image_folder):
    """Download the droplet, unarchive it and store it in the image folder."""

    droplet_path = droplet_data.downloadPath
    droplet_dest = os.path.join(image_folder, os.path.basename(droplet_path))
    self._file_system.cp(droplet_path, droplet_dest)

    droplet_dest = self._file_system.absolute_path(droplet_dest)
    with tarfile.open(droplet_dest) as archive:
      def is_within_directory(directory, target):
          
          abs_directory = os.path.abspath(directory)
          abs_target = os.path.abspath(target)
      
          prefix = os.path.commonprefix([abs_directory, abs_target])
          
          return prefix == abs_directory
      
      def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
      
          for member in tar.getmembers():
              member_path = os.path.join(path, member.name)
              if not is_within_directory(path, member_path):
                  raise Exception("Attempted Path Traversal in Tar File")
      
          tar.extractall(path, members, numeric_owner=numeric_owner) 
          
      
      safe_extract(archive, self._file_system.absolute_path(image_folder))

    os.remove(droplet_dest)

  def _generate_dockerfile(self, context, image_folder):  # pylint: disable=unused-argument
    """Generate a compatible docker file for the given context."""

    # TODO(cosnita) based on the context generate a docker file from plugins.
    dockerfile = io.BytesIO(bytes("""
FROM node:8-alpine
USER root

ADD . /root/app
RUN cd /root/app && npm install -d

VOLUME [ "/root/app/node_modules" ]

WORKDIR /root/app
ENTRYPOINT node index.js
""", self._default_charset))

    self._file_system.store("Dockerfile", dockerfile, image_folder)
