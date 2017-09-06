"""Provides the algorithms for working with binary content and persisting it to a filesystem.""" 
from abc import ABC, abstractmethod

import hashlib
import os

class FileSystemAbstract(ABC):
  """Provides the contract for implementing custom file systems compatible with the platform."""

  @abstractmethod
  def store(self, file_name, stream, folder_path):
    """Stores the given file under the specified path."""
    pass

  @abstractmethod
  def get(self, file_path):
    """Retrieves the given file as a stream of data."""
    pass

  @abstractmethod
  def delete(self, file_path):
    """Deletes an existing file from the filesystem."""
    pass

  @abstractmethod
  def exists(self, file_path):
    """Check if the given path exists in the filesystem."""
    pass

  @abstractmethod
  def size(self, file_path):
    """Returns the file size in bytes."""
    pass

  @abstractmethod
  def crc(self, file_path):
    """Returns a file verification hash. This will usually be an md5 of the file content."""
    pass

  def split_file_path(self, file_path): # pylint: disable=no-self-use
    """Returns a tuple containing the folder path and file name components."""

    folder_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    return (folder_path, file_name)

class LocalFileSystem(FileSystemAbstract):
  """Provides a very simple implementation which relies on a local file system or a NAS.
  In either case, the filesystem uses standard python I/O methods."""

  FS_CHUNK = 4096

  def __init__(self, mount_location):
    self._mount_location = mount_location

  def store(self, file_name, stream, folder_path):
    """We build the full folder path within the current filesystem and create it recursively.
    Afterwards we start writing the stream in small chunks of data."""

    if folder_path.startswith("/") and len(folder_path) > 1:
      folder_path = folder_path[1:]

    full_path = os.path.join(self._mount_location, folder_path)
    file_path = os.path.join(full_path, file_name)
    os.makedirs(full_path, exist_ok=True)

    with open(file_path, "wb+") as file_output:
      while True:
        buf = stream.read(self.FS_CHUNK)

        if not buf:
          break

        file_output.write(buf)

  def get(self, file_path):
    """We try to open the given file_path if it exists."""
    file_path = self._get_full_path(file_path)
    return open(file_path, "rb")

  def delete(self, file_path):
    """We first remove the file path and then we check to see if the parent folder is empty.
    In case it is, we also remove the parent folder."""

    file_path = self._get_full_path(file_path)

    try:
      os.remove(file_path)
    except FileNotFoundError:
      pass

    folder_path = os.path.dirname(file_path)

    try:
      os.rmdir(folder_path)
    except OSError:
      pass

  def exists(self, file_path):
    pass

  def size(self, file_path):
    file_path = self._get_full_path(file_path)
    return os.stat(file_path).st_size

  def crc(self, file_path):
    file_path = self._get_full_path(file_path)

    with open(file_path, mode='rb') as file_obj:
      code = hashlib.md5()
      while True:
        buf = file_obj.read(128) # 128 is smaller than the typical filesystem block
        if not buf:
          break

        code.update(buf)

      return code.hexdigest()

  def _get_full_path(self, file_path):
    if file_path.startswith("/") and len(file_path) > 1:
      file_path = file_path[1:]

    return os.path.join(self._mount_location, file_path)
