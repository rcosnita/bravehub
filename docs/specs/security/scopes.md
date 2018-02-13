In this page you can find all scopes currently used in the Bravehub platform.

| **API** | **Scope** | **Description** |
|---------|-----------|-----------------|
| **projectowners** | **bravehub.projectowners.view.me** | Allows a user to use /me endpoint for retrieving personal information based on the current token. |
| **projects** | **bravehub.projects.list** | Allows a user to list all projects from his account. |
| **projects** | **bravehub.projects.view.\<project_id\>** | Allows a user to view only the specified project. A token can contain multiple such scopes. |
| **projects** | **bravehub.projects.create** | Allows a user to create a new project. |
| **projects** | **bravehub.projects.update** | Allows a user to update an existing project. This applies only for the projects he is allowed to view. |
| **projects** | **bravehub.projects.delete** | Allows a user to delete an existing project. This applies only for the projects he is allowed to view. |
| **projectapis** | **bravehub.projectapis.list** | Allows a user to list all apis belonging to projects he is allowed to see. |
| **projectapis** | **bravehub.projectapis.view.\<api_id\>** | Allows a user to see details about a specific api. A token can contain multiple such scopes. |
| **projectapis** | **bravehub.projectapis.create** | Allows a user to create new apis. |
| **projectapis** | **bravehub.projectapis.update** | Allows a user to update existing apis. This correlates with view scopes in case they are contained in the token. |
| **projectapis** | **bravehub.projectapis.delete** | Allows a user to delete existing apis. This correlates with view scopes in case they are contained in the token. |
| **provisioning** | **bravehub.provisioning.tasks.list** | Allows a user to list all provisioning pending states. |
| **provisioning** | **bravehub.provisioning.tasks.view.\<project_id\>** | Allows a user to view all pending tasks for a specific project. A token can contain multiple such scopes. |
| **provisioning** | **bravehub.provisioning.tasks.create** | Allows a user to create a provisioning task. |
