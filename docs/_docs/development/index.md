---
title: Development
description: Setup, Install, and Deploy via Containers
---

# Development

First, clone the project.

```bash
git clone https://www.github.com/hpsee/askci
cd askci
```

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

Then you can use a single command to bring up a development server.

```bash
./askci.sh dev <expose_port>
```

For development, you likely want to expose port 80, and use localhost. Here is an example of
responding to the prompts for the first time:

```bash
$ ./askci.sh dev 80
.=----------------------------------------------=.
|                  AskCI CLI                     |
|   Welcome to the setup process for AskCI!      |
|      This won't take more than a minute.       |
.=----------------------------------------------=.

Asking for host details :->

Enter your host IP address (e.g. 173.194.122.231): 127.0.0.1
Do you confirm 127.0.0.1 for your host IP address? [y|n] y

Enter your host domain name (e.g. google.com): localhost
Do you confirm localhost for your host domain name? [y|n] y

Asking for app-required paths :->
  If a path you entered didn't exist, It will be created.

Enter database storage path /path/to/db: ./data/db
Do you confirm ./data/db for database storage path? [y|n] y

Enter git repositories storage path /path/to/deposit: ./data/repos
Do you confirm ./data/repos for git repositories storage path? [y|n] y

Enter collected static files path /path/to/static: ./data/static
Do you confirm ./data/static for collected static files path? [y|n] y

Enter uploaded media files path /path/to/media: ./data/media
Do you confirm ./data/media for uploaded media files path? [y|n] y
```

**Important!** Notice that all paths are relative, meaning they start with `./`.
If you don't do this, there will be an error from compose about the volume
declaration. Also notice that we are placing all folders for data and
static files in one upper level `data`.

Finally, after you run this command the first time, your settings
are saved in an `.env` file. To regenerate, either delete the file and 
run again, or edit the file directly.

## Containers

The development setup is simple - one container runs a development server,
and the second builds and updates the backend (e.g., collecting static and
making migrations).

 - askci_dev_base: handles collecting static and migrations, and then exists
 - askci_backend: starts the development server

## Commands

Restart the containers:

```bash
$ ./askci.sh restart dev
```

View logs

```bash
$ ./askci.sh logs dev
$ ./askci.sh logs dev askci_dev_base
```

Stop containers:

```bash
./askci.sh stop dev
```

To remove the images:

```bash
./askci.sh rm_dev
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

Now open web browser to your host address to see AskCI in production. NGINX logs will appear in nginx/logs and gunicorn logs in run/logs.<br>
This process will also create a superuser with
```
    username: admin
    password: lukedidntknow
```
credentials, if there's not any. Keep in mind to change/remove this and create another one in Django admin panel.


**under development**

Before starting your server, you should next look at options for [plugins]({{ site.baseurl }}/docs/plugins/).
Would you like to ask a question? Please [open an issue]({{ site.repo }}/issues/new).
