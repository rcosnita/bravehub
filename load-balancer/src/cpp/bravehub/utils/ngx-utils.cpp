#include "ngx-utils.h"

namespace bravehub {
namespace router {
namespace utils {
namespace nginx {
std::string GetArgStdString(void* arg, uint8_t idx)
{
  if (!arg) {
    return "";
  }

  auto strArray = static_cast<ngx_str_t*>(arg);
  auto strData = static_cast<char*>(static_cast<void*>(strArray[idx].data));
  return std::string(strData, strArray[idx].len);
}

std::string ToStdString(ngx_str_t str)
{
  std::string buffer(static_cast<char*>(static_cast<void*>(str.data)), str.len);
  return buffer;
}

ngx_str_t ToNgxString(ngx_pool_t* pool, const std::string& str,
  ngx_http_bravehub_router_module_ngx_callbacks* ngxCallbacks)
{
  ngx_str_t result = {
    str.length(),
    static_cast<u_char*>(ngxCallbacks->AllocateMemory(pool, sizeof(char) * str.length()))
  };
  memcpy(result.data, str.c_str(), str.length());

  return result;
}
}  // namespace nginx
}  // namespace utils
}  // namespace router
}  // namespace bravehub
