The platform for planning, deploying and releasing new innovators ideas.

![Architecture overview](docs/images/architecture-overview.png)

# Technology stack

* Docker Swarm Mode
* Python 3
* Flask Micro Framework
* HTML5 / JS / CSS
* Web components
* Ansible 2

# Getting started

In order to start the platform follow the steps below:

```bash
docker-compose up
```

This will start the platform and all APIs will be hot reloaded once you change the code.

## Best practices

### Python linting

```bash
sh cicd/lint-code.sh <project-name>
```

For instance, you might want to lint configuration api project.

```bash
sh cicd/lint-code.sh configuration-api
```

### Python unit testing

```bash
sh cicd/run-unit-tests.sh <project-name>
```

For instance, you might want to run the unit tests for the configuration api project.

```bash
sh cicd/run-unit-tests.sh configuration-api
```
