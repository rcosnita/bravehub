#include "router-config.h"

namespace bravehub {
namespace router {
namespace config {
RouterConfig::RouterConfig() : enabled_(false) { }

bool RouterConfig::Enabled() const { return enabled_; }
void RouterConfig::SetEnabled(bool enabled) { enabled_ = enabled; }

std::string RouterConfig::ProvisioningProtocol() const { return provisioningProtocol_; }
void RouterConfig::SetProvisioningProtocol(const std::string& protocol) { provisioningProtocol_ = protocol; }

std::string RouterConfig::ProvisioningHost() const { return provisioningHost_; }
void RouterConfig::SetProvisioningHost(const std::string& host) { provisioningHost_ = host; }

std::string RouterConfig::ProvisioningPort() const { return provisioningPort_; }
void RouterConfig::SetProvisioningPort(const std::string& port) { provisioningPort_ = port; }

std::string RouterConfig::ProvisioningPath() const { return provisioningPath_; }
void RouterConfig::SetProvisioningPath(const std::string& path) { provisioningPath_ = path; }

std::string RouterConfig::ProvisioningFullUrl(const std::string& resource, const bool skipProtocol) const {
  auto baseUrl = (skipProtocol ? "" : provisioningProtocol_ + "://");
  baseUrl+=provisioningHost_ + ":" + provisioningPort_ + provisioningPath_;

  if (resource.empty()) {
    return baseUrl;
  }

  return baseUrl + "/" + resource;
}

}  // namespace config
}  // namespace router
}  // namespace bravehub
