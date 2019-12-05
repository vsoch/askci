---
title: Deployment
description: Deployment
tags: 
 - docker
---

# Deployment

For a deployment with a domain name (typically on a cloud or hosted server) we need again clone the repostory, and then build and bring up images. The extra step here is that we will also do additional setup, and create a certificate. 

## Server Setup

You'll need to set up the server, including installing docker-compose, Docker, and 
other software dependencies. See [the Deployment setup]({{ site.baseurl }}/docs/deployment/setup/)
docs for how to do this, and then come back here to build and start containers.

## Start Development Server

Take a look at the client usage first:

```bash
$ ./askci.sh 
.=----------------------------------------------=.
|                  AskCI CLI                     |
|             Available Instructions             |
.=----------------------------------------------=.

dev
  Starts development containers.

prod
  Starts production stack.

stop <prod|dev>
  Stops containers.

up <prod|dev>
  Restart containers.

restart <prod|dev>
  View logs.

logs <prod|dev>
  Just brings up the containers. no building.

rm <prod|dev>
  Remove containers.

uninstall
  Removes all the content and containers related to AskCI.
```

Then you can use a single command to bring up a server:

```bash
./askci.sh prod
```

For development, you likely want to expose port 80, and use localhost. Here is an example of
responding to the prompts for the first time:

```bash
$ ./askci.sh prod
.=----------------------------------------------=.
|                  AskCI CLI                     |
|   Welcome to the setup process for AskCI!      |
|      This won't take more than a minute.       |
.=----------------------------------------------=.

Asking for host details :->

Enter your host IP address (e.g. 173.194.122.231): 34.83.45.68
Do you confirm 34.83.45.68 for your host IP address? [y|n] y

Enter your host domain name (e.g. google.com): askci.dev
Do you confirm askci.dev for your host domain name? [y|n] y

Asking for server details:->

Enter a help contact email for your server (e.g., name@institution.edu): vsochat@stanford.edu
Do you confirm vsochat@stanford.edu for a help contact email for your server? [y|n] y

Enter an institutional help or support site (e.g., https://srcc.stanford.edu): https://github.com/vsoch/askci/issues
Do you confirm https://github.com/vsoch/askci/issues for an institutional help or support site? [y|n] y

Enter your institution or affiliation  (e.g., Stanford University): Stanford University
Do you confirm Stanford University for your institution or affiliation ? [y|n] y

Enter a lowercase (no spaces) unique resource identifier for the server  (e.g., askci-server): askci-dev
Do you confirm askci-dev for a lowercase (no spaces) unique resource identifier for the server ? [y|n] y  

Enter the name of the server  (e.g., AskCI): AskCI
Do you confirm AskCI for the name of the server ? [y|n] y

Enter a Twitter account  (e.g., askcyberinfra): askcyberinfra
Do you confirm askcyberinfra for a Twitter account ? [y|n] y

Generating a secret for you... done ✔ 
>>> (We'are all set and ready to go.) <<<
```

Finally, after you run this command the first time, your settings
are saved in an `.env` file. To regenerate, either delete the file and 
run again, or edit the file directly.

## Containers

The development setup is simple - one container runs a development server,
and the second builds and updates the backend (e.g., collecting static and
making migrations).

 - askci_base: handles collecting static and migrations, and then exists
 - askci_worker: is a task worker
 - askci_scheduler and askci-dev_worker handle scheduled tasks
 - askci_nginx is the web server
 - askci_redis is a redis database for scheduled tasks

## Commands

Restart the containers:

```bash
$ ./askci.sh restart prod
```

View logs

```bash
$ ./askci.sh logs prod
$ ./askci.sh logs prod askci_base
```

Stop containers:

```bash
./askci.sh stop prod
```

To remove the images:

```bash
./askci.sh rm prod
```

You can also easily use docker-compose directly, but you need to specify the path to the https file in "https"

```bash
docker-compose -f https/docker-compose.yml restart uwsgi
docker-compose -f https/docker-compose.yml stop
docker-compose -f https/docker-compose.yml rm
```

or use the Makefile to run the linted (required [black](https://black.readthedocs.io/en/stable/)). It skips over migration
folders.

```bash
make lint
```

## Custom Build

The docker-compose will build the container automatically,
but if you want to build manually (such as without using cache) you can
do

```bash
docker build --no-cache -t askci_dev_image .
```

If you change anything in the `requirements.txt` file you'll likely need to do this.

## Web Interface

Now open web browser to your host address to see AskCI. NGINX logs will appear in nginx/logs and gunicorn logs in run/logs.<br>
This process will also create a superuser with
```
    username: admin
    password: lukedidntknow
```
credentials, if there's not any. Keep in mind to change/remove this and create another one in Django admin panel.

Before starting your server, you should next look at options for [plugins]({{ site.baseurl }}/docs/plugins/).
Would you like to ask a question? Please [open an issue]({{ site.repo }}/issues/new).
