#include "module.h"
#include <iostream>
#include <string>
#include <thread>

#include <rapidjson/document.h>
#include "cpp/bravehub/config/router-config.h"
#include "cpp/bravehub/utils/ngx-utils.h"

using bravehub::router::config::RouterConfig;
using bravehub::router::utils::nginx::GetArgStdString;
using bravehub::router::utils::nginx::ToStdString;
using bravehub::router::utils::nginx::ToNgxString;

thread_local static ngx_http_bravehub_router_module_ngx_callbacks* NGX_CALLBACKS = nullptr;

ngx_int_t ngx_http_bravehub_router_module_bootstrap(ngx_conf_t *cf,
                                                    ngx_http_bravehub_router_module_ngx_callbacks* ngxCallbacks)
{
  NGX_CALLBACKS = ngxCallbacks;

  auto handler = ngxCallbacks->WirePhase(cf, NGX_HTTP_CONTENT_PHASE);
  *handler = bravehub::router::HandleRequest;
  return NGX_OK;
}

void* ngx_http_bravehub_router_module_create_loc_conf(ngx_conf_t *cf) {
  auto conf = new RouterConfig();
  return conf;
}

char *ngx_http_bravehub_router_module_enable(ngx_conf_t *cf, ngx_command_t *cmd,
    void *conf)
{
  auto routerConfig = static_cast<RouterConfig*>(conf);
  routerConfig->SetEnabled(true);

  return NGX_CONF_OK;
}

char *ngx_http_bravehub_router_module_provisioning_protocol(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
  auto routerConfig = static_cast<RouterConfig*>(conf);
  auto protocol = GetArgStdString(cf->args->elts);

  routerConfig->SetProvisioningProtocol(protocol);
  return NGX_CONF_OK;
}

char *ngx_http_bravehub_router_module_provisioning_host(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
  auto routerConfig = static_cast<RouterConfig*>(conf);
  auto host = GetArgStdString(cf->args->elts);

  routerConfig->SetProvisioningHost(host);
  return NGX_CONF_OK;
}

char *ngx_http_bravehub_router_module_provisioning_port(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
  auto routerConfig = static_cast<RouterConfig*>(conf);
  auto port = GetArgStdString(cf->args->elts);

  routerConfig->SetProvisioningPort(port);
  return NGX_CONF_OK;
}

char *ngx_http_bravehub_router_module_provisioning_path(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
  auto routerConfig = static_cast<RouterConfig*>(conf);
  auto path = GetArgStdString(cf->args->elts);

  routerConfig->SetProvisioningPath(path);
  return NGX_CONF_OK;
}

namespace bravehub {
namespace router {
std::string GetProvisioningHostFromBody(const std::string& body)
{
  rapidjson::Document document;
  document.Parse(body.c_str());

  std::string domain = document["workerDomain"].GetString();
  auto port = document["workerPort"].GetInt();

  return domain + ":" + std::to_string(port);
}

static ngx_int_t HandleProvisioningResponse(ngx_http_request_t *request, void *data, ngx_int_t rc)
{
  size_t contentLength = request->headers_out.content_length_n;
  std::string contentStd(static_cast<char*>(static_cast<void*>(request->upstream->buffer.pos)), contentLength);

  NGX_CALLBACKS->Log(NGX_LOG_NOTICE, request->pool->log, "[Bravehub Router] Handling a new request ...");
  auto newHost = GetProvisioningHostFromBody(contentStd);

  ngx_str_t uri = ToNgxString(request->pool, std::string("/proxy-request"), NGX_CALLBACKS);
  std::string argsStd = "host=" + newHost + "&originalPath=" + ToStdString(request->main->uri);
  argsStd += "&originalQuery=" + ToStdString(request->main->args);

  ngx_str_t args = ToNgxString(request->pool, argsStd, NGX_CALLBACKS);

  return NGX_CALLBACKS->RedirectInternal(request->main, &uri, &args);
}

ngx_int_t HandleRequest(ngx_http_request_t* request)
{
  auto routerConfig = static_cast<RouterConfig*>(NGX_CALLBACKS->GetConfig(request));

  if (!routerConfig->Enabled()) {
    return NGX_DECLINED;
  }

  ngx_str_t uri = ToNgxString(request->pool, std::string("/proxy"), NGX_CALLBACKS);
  std::string argsStd = "protocol=" + routerConfig->ProvisioningProtocol();
  argsStd += "&host=" + routerConfig->ProvisioningFullUrl("domains", true);
  argsStd += "&originalHost=" + ToStdString(request->headers_in.host->value);
  argsStd += "&path=" + ToStdString(request->uri);

  auto args = ToNgxString(request->pool, argsStd, NGX_CALLBACKS);

  ngx_http_request_t *subreq = NULL;
  ngx_http_post_subrequest_t *continuation = 
    static_cast<ngx_http_post_subrequest_t*>(NGX_CALLBACKS->AllocateMemory(request->pool, sizeof(ngx_http_post_subrequest_t)));
  continuation->handler = HandleProvisioningResponse;
  continuation->data = routerConfig;

  NGX_CALLBACKS->DoRequest(request, &uri, &args, &subreq, continuation, NGX_HTTP_SUBREQUEST_IN_MEMORY);

  return NGX_DONE;
}
}  // namespace router
}  // namespace bravehub
