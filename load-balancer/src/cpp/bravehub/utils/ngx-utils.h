#ifndef LOAD_BALANCER_SRC_CPP_BRAVEHUB_UTILS_NGX_UTILS_H_
#define LOAD_BALANCER_SRC_CPP_BRAVEHUB_UTILS_NGX_UTILS_H_

#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_list.h>
#include <ngx_string.h>
#include <string>

#include "cpp/bravehub/module-data.h"

namespace bravehub {
namespace router {
namespace utils {
namespace nginx {
/**
 * Provides the logic for retrieving a specific argument of a directive.
 */
std::string GetArgStdString(void* arg, uint8_t idx = 1);

/**
 * Provides a simple conversion mechanism between nginx string and standard string.
 */
std::string ToStdString(ngx_str_t str);

ngx_str_t ToNgxString(ngx_pool_t* pool, const std::string& str,
  ngx_http_bravehub_router_module_ngx_callbacks* ngxCallbacks);
}  // namespace nginx
}  // namespace utils
}  // namespace router
}  // namespace bravehub

#endif  // LOAD_BALANCER_SRC_CPP_BRAVEHUB_UTILS_NGX_UTILS_H_
