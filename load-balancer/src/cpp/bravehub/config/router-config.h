#ifndef LOAD_BALANCER_SRC_CPP_BRAVEHUB_CONFIG_ROUTER_CONFIG_H_
#define LOAD_BALANCER_SRC_CPP_BRAVEHUB_CONFIG_ROUTER_CONFIG_H_

#include <string>

namespace bravehub {
namespace router {
namespace config {
/**
 * Provides a model object for storing the current router configuration.
 */
class RouterConfig {
 public:
  RouterConfig();

  bool Enabled() const;
  void SetEnabled(bool enabled);

  std::string ProvisioningProtocol() const;
  void SetProvisioningProtocol(const std::string& protocol);

  std::string ProvisioningHost() const;
  void SetProvisioningHost(const std::string& host);

  std::string ProvisioningPort() const;
  void SetProvisioningPort(const std::string& port);

  std::string ProvisioningPath() const;
  void SetProvisioningPath(const std::string& path);

  std::string ProvisioningFullUrl(const std::string& resource = "",
                                  const bool skipProtocol = false) const;

 private:
  bool enabled_;

  std::string provisioningProtocol_;
  std::string provisioningHost_;
  std::string provisioningPort_;
  std::string provisioningPath_;
};
}  // namespace config
}  // namespace router
}  // namespace bravehub

#endif  // LOAD_BALANCER_SRC_CPP_BRAVEHUB_CONFIG_ROUTER_CONFIG_H_
