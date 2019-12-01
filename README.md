# AskCI

![https://vsoch.github.io/askci/docs/getting-started/img/home.png](https://vsoch.github.io/askci/docs/getting-started/img/home.png)

See the [documentation](https://vsoch.github.io/askci/) for getting started.

**under development**

## Background

I invisioned creating a shared documentation server back in 2017, something I called "The Documentation Octopus" since it would span multiple universities. I started to work on a [server](https://www.github.com/researchapps/helpme-server) that users could submit help requests to,
but realized that a much more extendable tool would be to provide a client that can submit
help requests to already existing servers. That project turned into [helpme](https://www.github.com/vsoch/helpme) and the server was largely abandoned. I joined the [AskCI](https://ask.ci) community at the end of 2018, and while we use a Discourse installation, it still feels like many elements are missing. Since I can make some time, I figured I'd give this another Go.

## Images Included

AskCI consists of several Docker images, and they are integrated 
to work together using [docker-compose.yml](docker-compose.yml). 
The images are the following:

 - **vanessa/askci**: is the main uwsgi application, which serves a Django (python-based) application.
 - **nginx**: pronounced (engine-X) is the webserver. The starter application is configured for http, however you should follow the instructions to set up https properly. Note that we build a custom nginx image that takes advantage of the [nginx upload module](https://www.nginx.com/resources/wiki/modules/upload/).
 - **worker**: is the same uwsgi image, but with a running command that is specialized to perform tasks. The tasks are run via [django-rq](https://github.com/rq/django-rq) that uses a
 - **redis**: database to organize the jobs themselves.
 - **scheduler** jobs can be scheduled using the scheduler.

## Thank Yous

 - [tui.editor](https://github.com/nhn/tui.editor) offers a beautiful editor for markdown.

## License

This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text. See [LICENSE-djacket](.github/LICENSE-djacket) for the upstream license.
