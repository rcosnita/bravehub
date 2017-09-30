#ifndef LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_DATA_H_
#define LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_DATA_H_

#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  void (*Log)(uint severity, ngx_log_t* logger, const char* msg, ...);

  void* (*AllocateMemory)(ngx_pool_t *pool, size_t size);

  void* (*GetConfig)(ngx_http_request_t* request);

  ngx_int_t (*DoRequest)(ngx_http_request_t *r,
    ngx_str_t *uri, ngx_str_t *args, ngx_http_request_t **sr,
    ngx_http_post_subrequest_t *psr, ngx_uint_t flags);

  ngx_int_t (*RedirectInternal)(ngx_http_request_t *r, ngx_str_t *uri, ngx_str_t *args);

  ngx_http_handler_pt* (*WirePhase)(ngx_conf_t* cf, ngx_http_phases phase);
} ngx_http_bravehub_router_module_ngx_callbacks;

#ifdef __cplusplus
}
#endif

#endif  // LOAD_BALANCER_SRC_CPP_BRAVEHUB_MODULE_DATA_H_
