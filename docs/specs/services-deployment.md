In this document you can find all relevant information for deploying Bravehub core services:

* configuration app
* configuration api
* provisioning api
* provisioner

Ideally, they should be deployed using the same architecture as the one we use for clients services. Because the CI/CD pipeline for our customers
is still work in progress, we are going to deploy the core services using ansible.

During bootstrap phase, the services role will be run on a swarm master after the cluster is fully functional.
