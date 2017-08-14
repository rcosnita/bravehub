Place in this folder all tar docker images which must be used by the bravehub platform. The images are usually exported from a docker engine
using the following command:

```bash
docker save <imageid>:<image-version> -o <image-name>-<image-version>.tar
```

All images from here are imported automatically on every instance from the platform. This allows us to make deployments without actually using
a docker repository.
