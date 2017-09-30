cmake_minimum_required(VERSION 3.8.1)

set(NGINX_FOLDER /root/nginx)
set(NGINX_SRC_FOLDER ${NGINX_FOLDER}/src)
set(ROUTER_FOLDER ./)
set(THIRD_PARTY_FOLDER /root/third-party)

set(CMAKE_CPP_FLAGS "${CMAKE_CPP_FLAGS} -fPIC -std=c++11 -Wall -ggdb -fno-omit-frame-pointer")

include_directories(
  ${NGINX_SRC_FOLDER}/core
  ${NGINX_SRC_FOLDER}/event
  ${NGINX_SRC_FOLDER}/event/modules
  ${NGINX_SRC_FOLDER}/http
  ${NGINX_SRC_FOLDER}/http/modules
  ${NGINX_SRC_FOLDER}/http/modules/perl
  ${NGINX_SRC_FOLDER}/http/v2
  ${NGINX_SRC_FOLDER}/os/unix
  ${NGINX_SRC_FOLDER}/mail
  ${NGINX_SRC_FOLDER}/stream
  ${NGINX_FOLDER}/objs

  ${ROUTER_FOLDER}
  ${THIRD_PARTY_FOLDER}/rapidjson/include
)

list(APPEND BRAVEHUB_ROUTER_SOURCES
  ${ROUTER_FOLDER}/cpp/bravehub/module.cpp
  ${ROUTER_FOLDER}/cpp/bravehub/config/router-config.cpp
  ${ROUTER_FOLDER}/cpp/bravehub/utils/ngx-utils.cpp
)

add_library(
  bravehub-router
  SHARED

  ${BRAVEHUB_ROUTER_SOURCES}
)

target_link_libraries(
  bravehub-router
)
