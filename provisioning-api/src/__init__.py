"""Initializes some configuration parameters which are used in the implementation of
provisioning-api microservice."""
from src.ioc import ProvisionerContainer

API_VERSION = ProvisionerContainer.provisioner_meta.version
API_FULL_VERSION = "{0}.{1}.{2}".format(API_VERSION.major, API_VERSION.minor, API_VERSION.patch)
API_MAJOR_VERSION = "{0}.{1}".format(API_VERSION.major, API_VERSION.minor)
