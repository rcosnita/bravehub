#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>
#include <ngx_log.h>

#include "cpp/bravehub/module.h"

static ngx_int_t ngx_http_bravehub_router_module_init(ngx_conf_t *cf);

static ngx_http_module_t ngx_http_bravehub_router_module_ctx = {
    NULL,                                 /* preconfiguration */
    ngx_http_bravehub_router_module_init, /* postconfiguration */

    NULL, /* create main configuration */
    NULL, /* init main configuration */

    NULL, /* create server configuration */
    NULL, /* merge server configuration */

    ngx_http_bravehub_router_module_create_loc_conf, /* create location configuration */
    NULL  //    ngx_http_va_redis_merge_loc_conf /* merge location configuration
          //    */
};

static ngx_command_t ngx_http_bravehub_router_module_commands[] = {
    { ngx_string("bravehub_router_module"), /* directive */
      NGX_HTTP_LOC_CONF|NGX_CONF_NOARGS, /* location context and takes
                                            no arguments*/
      ngx_http_bravehub_router_module_enable, /* configuration setup function */
      NGX_HTTP_LOC_CONF_OFFSET, /* No offset. Only one context is supported. */
      0, /* No offset when storing the module configuration on struct. */
      NULL},

    { ngx_string("bravehub_router_module_provisioning_protocol"), /* directive */
      NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1, /* location context and takes
                                            no arguments*/
      ngx_http_bravehub_router_module_provisioning_protocol, /* configuration setup function */
      NGX_HTTP_LOC_CONF_OFFSET, /* No offset. Only one context is supported. */
      0, /* No offset when storing the module configuration on struct. */
      NULL},

    { ngx_string("bravehub_router_module_provisioning_host"), /* directive */
      NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1, /* location context and takes
                                            no arguments*/
      ngx_http_bravehub_router_module_provisioning_host, /* configuration setup function */
      NGX_HTTP_LOC_CONF_OFFSET, /* No offset. Only one context is supported. */
      0, /* No offset when storing the module configuration on struct. */
      NULL},

    { ngx_string("bravehub_router_module_provisioning_port"), /* directive */
      NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1, /* location context and takes
                                            no arguments*/
      ngx_http_bravehub_router_module_provisioning_port, /* configuration setup function */
      NGX_HTTP_LOC_CONF_OFFSET, /* No offset. Only one context is supported. */
      0, /* No offset when storing the module configuration on struct. */
      NULL},

    { ngx_string("bravehub_router_module_provisioning_path"), /* directive */
      NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1, /* location context and takes
                                            no arguments*/
      ngx_http_bravehub_router_module_provisioning_path, /* configuration setup function */
      NGX_HTTP_LOC_CONF_OFFSET, /* No offset. Only one context is supported. */
      0, /* No offset when storing the module configuration on struct. */
      NULL},

    ngx_null_command
};

ngx_module_t ngx_http_bravehub_router_module = {
    NGX_MODULE_V1,
    &ngx_http_bravehub_router_module_ctx,     /* module context */
    ngx_http_bravehub_router_module_commands, /* module directives */
    NGX_HTTP_MODULE,                          /* module type */
    NULL,                                     /* init master */
    NULL,                                     /* init module */
    NULL,                                     /* init process */
    NULL,                                     /* init thread */
    NULL,                                     /* exit thread */
    NULL,                                     /* exit process */
    NULL,                                     /* exit master */
    NGX_MODULE_V1_PADDING};

static void ngx_http_bravehub_router_module_log(uint severity, ngx_log_t* logger, const char* msg, ...)
{
  va_list args;
  va_start(args, msg);
  ngx_log_error(severity, logger, 0, msg, args);
  va_end(args);
}

static ngx_http_handler_pt* ngx_http_bravehub_router_module_wire_phase(ngx_conf_t* cf, ngx_http_phases phase)
{
  ngx_http_core_main_conf_t* cmcf;
  ngx_http_handler_pt* h;

  cmcf = ngx_http_conf_get_module_main_conf(cf, ngx_http_core_module);
  h = ngx_array_push(&cmcf->phases[phase].handlers);

  return h;
}

static void* ngx_http_bravehub_router_module_get_request_config(ngx_http_request_t* request)
{
  return ngx_http_get_module_loc_conf(request, ngx_http_bravehub_router_module);
}

static ngx_int_t ngx_http_bravehub_router_module_init(ngx_conf_t *cf) {
  // TODO(cosnita) Find a way to cleanup the memory correctly. Probably exit master is the best place.
  ngx_http_bravehub_router_module_ngx_callbacks* ngxCallbacks = \
        ngx_pcalloc(cf->pool, sizeof(ngx_http_bravehub_router_module_ngx_callbacks));

  ngxCallbacks->AllocateMemory = ngx_pcalloc;
  ngxCallbacks->DoRequest = ngx_http_subrequest;
  ngxCallbacks->GetConfig = ngx_http_bravehub_router_module_get_request_config;
  ngxCallbacks->Log = ngx_http_bravehub_router_module_log;
  ngxCallbacks->RedirectInternal = ngx_http_internal_redirect;
  ngxCallbacks->WirePhase = ngx_http_bravehub_router_module_wire_phase;

  return ngx_http_bravehub_router_module_bootstrap(cf, ngxCallbacks);
}
