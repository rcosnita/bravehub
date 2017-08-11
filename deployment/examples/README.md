This container contains several useful examples which can be executed against bravehub platform.
If bravehub stack is up and running you can test the examples docker image by running the following command:

```bash
docker run -it --rm --network bravehub_default -v $(pwd)/python:/root/python:ro -e HBASE_THRIFT_API=hbase-thrift.api.internal.bravehub-dev.com bravehub_bravehub-examples
```
