---
title: "pam-auth - Authentication with PAM"
pdf: true
toc: false
permalink: docs/plugins/pam
---

# PAM Authentication

The `pam_auth` plugin allows users to login to AskCI using the unix accounts on 
the host system.

To enable PAM authentication you must:

  * Add `pam_auth` to the `PLUGINS_ENABLED` list in `askci/settings/config.py`
  * Uncomment binds to /etc/shadow and /etc/passwd in `docker-compose.yml`
  * Build the docker image with the build argument ENABLE_PAM set to true

More detailed instructions are below.

## Getting Started

This is the detailed walkthough to set up the PAM Authentication plugin. 

First, uncomment "pam_auth" at the bottom of `askci/settings/config.py` to 
enable the login option.

```bash
PLUGINS_ENABLED = [
#    'ldap_auth',
    'pam_auth',
#    'saml_auth'
]
```

Since we need to get access to users from the host,
you need to edit the `docker-compose.yml` and uncomment binds to your host:

```bash
uwsgi:
  restart: always
  image: {{ site.container }}
  volumes:
    - .:/code
    - ./static:/var/www/static
    - ./data:/var/www/data
    # uncomment for PAM auth
    #- /etc/passwd:/etc/passwd 
    #- /etc/shadow:/etc/shadow
  links:
    - redis
    - db
```

If you do this, we lose the user added in the container for nginx! 
You also need to add the nginx user to your host:

```bash
$ sudo addgroup --system nginx
$ sudo adduser --disabled-login --system --home /var/cache/nginx --ingroup nginx nginx
```

Note that this solution [would require restarting the container](https://github.com/jupyterhub/jupyterhub/issues/535) for changes on the host to take effect (for example, adding new users). If you find a better way to do this, please test and open an issue to add to this documentation.

Finally, you must build the docker image with the build argument ENABLE_PAM set to true:

```bash
$ docker build --build-arg ENABLE_PAM=true -t {{ site.container }} .
```
