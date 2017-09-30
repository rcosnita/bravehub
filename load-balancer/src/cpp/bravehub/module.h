#ifndef LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_H_
#define LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_H_

#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>
#include <ngx_log.h>

#include "cpp/bravehub/module-data.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Bootstraps the C++ code for the bravehub module.
 */
ngx_int_t ngx_http_bravehub_router_module_bootstrap(ngx_conf_t *cf,
                                                    ngx_http_bravehub_router_module_ngx_callbacks* ngxCallbacks);

/**
 * Builds a configuration object for bravehub router module. Based on this configuration,
 * we can decide if the http request must be handled by our module or must be declined.
 */
void* ngx_http_bravehub_router_module_create_loc_conf(ngx_conf_t *cf);

/**
 * Enables the bravehub router module for the current location.
 */
char *ngx_http_bravehub_router_module_enable(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);

/**
 * Configures the protocol we want to use for communicating with the provisioning api.
 */
char *ngx_http_bravehub_router_module_provisioning_protocol(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);

/**
 * Configures the provisioning api host.
 */
char *ngx_http_bravehub_router_module_provisioning_host(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);

/**
 * Configures the provisioning api port.
 */
char *ngx_http_bravehub_router_module_provisioning_port(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);

/**
 * Configures the provisioning api path.
 */
char *ngx_http_bravehub_router_module_provisioning_path(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
namespace bravehub {
namespace router {
/**
 * Decides for the incoming request if it must be routed in the bravehub platform or it must be rejected
 * because the domain is not currently provisioned.
 *
 * Provisioning API tells us if we must proxy the request or not.
 */
ngx_int_t HandleRequest(ngx_http_request_t* request);
}  // namespace router
}  // namespace bravehub
#endif

#endif  // LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_H_
