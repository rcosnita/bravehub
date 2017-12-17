In order to provision our platform layers we rely on modular ansible playbooks. We assume each instance is told what role
it plays in the platform. Based on that information specific tags and roles will be executed in order to bootstrap new instances.

We decided to rely on a Linux distribution which is available in all clouds: Ubuntu linux.

At boot time, every instance also downloads a specific systemd unit file which orchestrates the bootstrap and instance preparation.

In order to add new components into the cluster you must upload the provisioning folder into the environment dedicated s3 bucket.
