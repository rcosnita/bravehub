The storage for the platform is currently relying on HBase on top of a strong consistency filesystem: Elastic File Search.
This mix of technologies provides high scalability at very low price.

Our storage has two main purposes:

* Store data specific to our APIs.
* Store time series data required by our monitoring and alerting solution.

The discovery of the storage is relying on dns. Customers who require access to the HBase storage must use the following zookeeper quorum:

```
zookeeper-1.api.internal.bravehub-dev.com
zookeeper-2.api.internal.bravehub-dev.com
zookeeper-3.api.internal.bravehub-dev.com
```

For development environments, only **zookeeper-1** is available.
