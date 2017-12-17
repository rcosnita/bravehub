Bravehub platform provides several services which represent cross cutting concerns:

- router layer (internal api gateway for the whole platform).
- ntp layer (time synchronization infrastructure).
- hbase / zookeeper layers (storage infrastructure).
- docker swarm mode (containers orchestrator).

In order to be able to easily locate each service we are using internal DNS servers for AWS / Azure / GCE.

Every instance which is started registers itself in one or more record sets based on the instance role.

Moreover, DNS is also used during machine provisioning. For instance, while we provision ntp layer we decide if the ntp must use a client or a server configuration
based on the current dns entries available for the platform.

## Known services / dns entries

| **DNS Entry** | **Role** | **DNS Balancing** |
|---------------|----------|-------------------|
| ntp.\<platform suffix\> | ntp server | no |
| router.\<platform suffix\> | internal gateway | yes |
| zookeeper-1.\<platform suffix\> | storage | no |
| zookeeper-2.\<platform suffix\> | storage | no |
| zookeeper-3.\<platform suffix\> | storage | no |
| hbase-master-1.\<platform suffix\> | storage | no |
| hbase-master-2.\<platform suffix\> | storage | no |
| hbase-thrift.\<platform suffix\> | storage gateway | yes |
| hbase-regionserver-1.\<platform suffix\> | storage | no |
| hbase-regionserver-n.\<platform suffix\> | storage | no |
| swarm-master-1.\<platform suffix\> | containers orchestrator | no |
| swarm-master-n.\<platform suffix\> | containers orchestrator | no |
| swarm-workers.\<platform suffix\> | containers orchestrator | yes |
| portainer.\<platform suffix\> | containers manager | no |

* **\<platform suffix\>** is a meta information configured for every deployment of bravehub platform
    - E.g: **api.internal.bravehub-stage.com**

## Known issues

Because we use a service discovery mechanism based on DNS there are several known issues:

- there might be cases when packets sent to **internal gateway** will fail.
    + This can be resolved through connection draining and kill interval > 2 x DNS TTL.
- there might be cases when packets sent to **storage gateway** will fail.
    + This can be resolved through connection draining and kill interval > 2 x DNS TTL.
- DNS entries might not always be up to date. This is caused by the highly scalable nature of the platform and to the fact that we want to scale down.
    + In order to solve this problem, we need an authoritative process which always keep the dns configuration updated.
    + It is perfectly fine to have this supervisor run on top of docker swarm infrastructure.
