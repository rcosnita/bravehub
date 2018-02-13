In this document we describe the authentication and authorization flows currently supported in bravehub.

# Authorization

For authorization and better integration with third party sources we rely on OAuth2 framework specification.

![OAuth2 abstract](../../images/security/oauth2-abstract.png?raw)

In Bravehub platform we support:

* A single authorization server.
* Multiple resource owners.
* Multiple resource servers.
* Multiple identity providers.
    - Github
    - Facebook
    - Google
    - Microsoft
    - Linkedin

Authentication process is orchestrated by our authorization server. The whole authentication process is covered in the next diagram.

## Authentication

Authentication process is built into the authorization server. There are two types of identities which can be used on bravehub platform:

* Remote (e.g Github / Facebook / ...).
* Local (created through the native ui).

### Local identity

The local identity is a simple combination of username and password (and optionally MFA). It is created through the [signup process](signup.md).

### Remote identity

A remote identity is a hybrid between an identity provider and local username which corresponds to the remote identity provider username.

The remote identity does not support username and password authentication so the authorization must rely on the remote identity provider for authentication.

The remote identity must be transparently converted to a local identity in order to have an entry which can own Bravehub resources.

# Supported grants

In Bravehub OAuth2 implementation we support the following grants:

* Implicit grant (used by the public UIs.)
* Authorization code (used by third party apps which can guarantee confidentiality)
* Service grant (used by Bravehub platform APIs).

# Supported tokens

In Bravehub OAuth2 implementation we support bearer tokens which are self descriptive and signed. In order to be able to 
quickly validate a token, we are going to use the following structure:

```json
{
  "public": {
    "owner": "3746656e-c319-447f-9fc1-2f85f1cbcd33",
    "client_id": "bravehub-projects-api",
    "created": "2018-02-13T06:04:39",
    "validity": 240,
    "usage": "multiple" 
  },
  "private": {
    "publicToken": "base64 representation of the public token representation.",
    "scopes": [
      "bravehub.projectowners.view",
      "bravehub.projects.list",
      "bravehub.projects.create",
      "bravehub.projects.update",
      "bravehub.projects.delete"
    ],
    "identity": {
      "email": "radu.cosnita@gmail.com",
      "firstName": "Radu Viorel",
      "lastName": "Cosnita"
    },
    "security": {
      "code": "base64 representation of the authorization code.",
      "serviceToken": "base64 representation of the service token."
    }
  }
}
```

The token will be base64 encoded. The public part of the token is plain text and can be used by applications.
The private part of the token will be decrypted using a symmetric algorithm. Only Bravehub platform will be able to access the private part.

Every property from **security** section is optional. For instance, tokens emitted through implicit grant will not have a security entry altogether.

## Tokens revocation

Tokens can be revoked in one of the following ways:

* If the token contains a persistent proof (authorization code) we simply revoke the authorization code.
* It the token does not contain a persistent proof (e.g service api bearer token, refresh token, access token from implicit grant) we will blacklist the token in a persistent storage.

Tokens revocation is useful for logout scenarios when we want all tokens from that sessions to be removed.

## Token scopes

Scopes provides the main mechanism for implementing granular Access Control Rules. Each specific API must define its scopes and each scope purpose.

We strongly recommend documenting all scopes under [Scopes spec](scopes.md) page.

### Static and dynamic scopes

Most operations we protect using scopes can be defined as static string. Tuple (owner,scope) will be enough to protect resources.

There are some more granular Access Control Rules which requires dynamic scopes. For instance, we have **Admin** and **Individual** users.

Lets assume the **Admin** is allowed to list all projects belonging to his company while the **Individual user** is only allowed to see projects where he contributes.

Obviously, we can not achieve this with static scopes. We solve this problem using dynamic scopes.

| **Scope**        |**Description**|
|------------------|------------------------------------------------------|
| **bravehub.projects.view.\<project_id\>** | The api will apply additional validation on **project_id** and will be able to limit user access to that specific project. |
| **bravehub.projects.view** | This will grant user access to see all projects beloning to his company account. |

Dynamic scopes are extremely important for implementing enterprise and collaboration use cases.
