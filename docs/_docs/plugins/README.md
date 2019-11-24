---
title: Plugins
pdf: true
toc: false
permalink: docs/plugins/
---

# Plugins

AskCI supports additional functionality through plugins. Currently, additional
authentication frameworks are supported, but any added functionality is plausible to develop.
The plugins distributed with AskCI are found in the `askci/plugins` folder.
For any plugin you want to enable, you should follow the instructions in the
pages below.

## Included Plugins

The following plugins are included, and can be enabled by adding them to the
`PLUGINS_ENABLED` entry in `askci/settings/config.py`. Plugins may require further configuration in
your local `askci/settings/secrets.py` file.

 - [LDAP-Auth](ldap): authentication against LDAP directories
 - [PAM-Auth](pam): authentication using PAM (unix host users)
 - [SAML](saml): Authentication with SAML

The Dockerfile has some build arguments to build the Docker image according to the plugins software requirements. These variables are set to false by default:

```bash
ARG ENABLE_LDAP=false
ARG ENABLE_PAM=false
ARG ENABLE_SAML=false
```

Therefore, if you want to install the requirements of all current supported plugins, you can build the image as follows: 

```bash
docker build --build-arg ENABLE_LDAP=true --build-arg ENABLE_PAM=true --build-arg ENABLE_SAML=true -t {{ site.container }} .
```

## Writing a Plugin

A AskCI plugin is a Django App, that lives inside `askci/plugins/<plugin-name>`.
Each plugin:

 - Must provide a `urls.py` listing any URLs that will be exposed under `/plugin-name`
 - Can provide additional, models, views, templates, static files.
 - Can register an additional `AUTHENTICATION_BACKEND` by specifying `AUTHENTICATION_BACKEND` in
   its `__init.py__`
 - Can register additional context processors by defining a tuple of complete paths to the relevant processors by specifying `CONTEXT_PROCESSORS` in its `__init.py__`
 - Must provide a documentation file and link in this README.

Plugins are loaded when the plugin name is added to `PLUGINS_ENABLED` in `askci/settings/config.py`.
A plugin mentioned here is added to `INSTALLED_APPS` at runtime, and any `AUTHENTICATION_BACKEND`
and `CONTEXT_PROCESSORS` listed in the plugin `__init.py__` is merged into the project settings.

See plugins distrubuted with under `askci/plugins` for example code. If your plugin has any specific software requirements that are not currently available in the Docker image and **those requirements are compatible with the current software**, you can set a new build argument `ENABLE_{PLUGIN_NAME}` and add the corresponding installation commands in the `PLUGINS` section of the Dockerfile with the following format:

```bash
RUN if $ENABLE_{PLUGIN_NAME}; then {INSTALLATION_COMMAND}; fi;
```
## Writing Documentation

Documentation for your plugin is just as important as the plugin itself! You should create a subfolder under
`_docs/plugins/<your-plugin>` with an appropriate README.md that is linked to in this file.
Use the others as examples to guide you.
