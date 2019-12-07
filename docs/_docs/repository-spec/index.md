---
title: Repository Specification
description: Structure and content of a knowledge repository
---

## Overview

Much of the interaction from the site here is dependent on actions that
interact with the server defined in the [AskCI repository template](https://github.com/hpsee/askci-template-term). **Important**: the organization that serves the template _must_ be
autheticated with the application, meaning that someone that is an owner
must give the permission when connecting. If the permission isn't granted,
using the repository as a template will not work, and creating new articles
will not work.

## What is a template?

A template is a GitHub repository that is used as a template when a new knowledge repository
is created. It contains examples, and GitHub workflows that ensure that events are
triggered to update and interact with the repository. We currently
just have one GitHub template, and this could either be extended, or
the server could allow for different templates that serve different
purposes. Although forks would maintain commits, they aren't appropriate to
use because an organization or user couldn't fork the same repository to his
or her namespace (with a different name). In practice, the template repository
just gets renamed.
 
## How Does this work?

Each repository is a knowledge repository, meaning that is represents a single term or concept that folks might have questions about. 

### Adding Knowledge

The main logic works by way of continuous integration (GitHub workflows) and webhooks.

 1. The user changes a knowledge item in the interface. This triggers a [repository dispatch](https://developer.github.com/v3/activity/events/types/#repositorydispatchevent) event. The event triggers a GitHub action that will create a new branch and push the updates to it, and open a pull request.
 2. The owner of the repository is notified, and the pull request is reviewed.
 3. On merge to master, another webhook is triggered (push event) that grabs the commit id, and the updated content.
 
The interface should keep an update of pull requests in progress for the term? Or link to them?
This assumes that knowledge owners are okay with using GitHub and managing pull requests.

### Asking Questions

A question will be linked to a GitHub issue. 

 - Each article model links to questions
 - The questions can be searched from the home screen of the site
 - If a question isn't found, the user can find a related topic
 - If the topic doesn't exist, he/she can make it (or request it to be made)
 - If a related topic exists, the user asks the question to the GitHub issue board
 - The question is then embedded in the text


### Actions

Creating a new repository for a term coincides with authenticating with GitHub, and using the
GitHub API to fork the repository template to a new repository that is then connected to the website.
The connection is done via webhooks, and other actions that sync content between the repository and the
server, and allow events on the server to trigger events. Specifically:

 - **github updating the server**: a webhook is created to ping the server when any update is done to the master branch. On this event, the README.md (the core of the knowledge) is parsed from the repository to update the AskCI server.
 - **asking a question**: when a user asks a question, either by way of the web interface or a connected tool, we use the GitHub API to open an issue on the GitHub issues board for the connected repository. The issue is opened on behalf of the user asking the question. Addressing the issue means updating the README.md to answer the user question, and then embedding a question tag alongside it (see [questions](#questions) below).
 - **request for review**: a user can edit a connected repository content directly from the website. This requires Github being authenticated, and it triggers a dispatch event with the updated the content. The dispatch event creates a new branch with the content, and opens a pull request for the term maintainer to review. When it's merged, the first bullet (github updating the server) is triggered to update the content on the server. All associated pull requests that are open (and warrant others to review) are listed on the term's page. The workflow that drives this action is [request-review.yaml](https://github.com/hpsee/askci-template-term/blob/master/.github/workflows/request-review.yaml)
 - **updates from template**: you can imagine that the base template repository will be updated at certain points. To drive this, we have the [update-template.yaml](https://github.com/hpsee/askci-template-term/blob/master/.github/workflows/update-template.yaml) dispatch event, which looks for metadata in the payload to indicate a request to update. This will be triggered from the server by an admin user when an update is warranted. Akin to requesting review, it creates a new branch and opens a pull request for the maintainer to safely review.
 - **closing a pull request**: closing of a pull request will need to update the server too - I haven't implemented this yet and need to think it over more.

For the **request for review** and **updates from template**, since both of these are dispatch events, we identify the name based on the client_payload.event_name, which is `request-review` and `update-template`, respectively. More dispatch events can be added in this fashion.

These same actions can also be afforded by way of a repository import (importing a knowledge repository that already exists), which means that multiple servers can be connected to and work on the same repository at the same time given appropriate GitHub permissions. I'm not sure if this would be wanted, but it's possible.


### README

The [README.md](https://github.com/hpsee/askci-template-term/blob/master/README.md) is the core of the knowledge repository. All writing about the term, links to examples, and questions go here. This is modeled after a wikipedia page for which we are presented with a single page per article. This content in the README.md is rendered into the AskCI server interface, and parsed for questions and examples.
 
#### Questions

A question is an embedded span with an id that can appear anywhere in the README.md. For example:

```html
<span id="question-how-do-i-build-a-container"></span>
```

That span would be embedded directly before the question is answered, whether that be at the
start of a section, or in the middle of it. Notably, the following must be true:

 - the identifier starts with question
 - there are no characters other than letters and dashes
 - all letters are lowercase

The repository has a testing file to [test the markdown](https://github.com/hpsee/askci-template-term/blob/master/.github/workflows/test_markdown.py) that ensures that this is followed, and the check is also done on the server.
When an update is made to the README.md, meaning that an update is made to the master branch,
if the repository is connected, the server is notified and questions are parsed from the README
and indexed. This means that a user can easily search across the site to find the question.

#### Examples

Currently, an example is a section of code that appears directly after an equivalent span, however
the span needs to start with "example-" (this is also tested).

```html
<span id="example-how-do-i-build-a-container"></span>
```

A code block would need to follow this span directly. Currently, only a single code block
will be parsed and indexed, and it's required. 


## How can we improve?

### Templates

Currently, we just have one base template, and it supports a main article (README) that includes content, questions, and examples. We could easily add other kinds of span identifiers, or even custom content types (files looked for in 
the repository) that the server knows how to render. When the time is right for this, the repository might serve a metadata file that indicates included content.

### Examples

Currently, only single code blocks after spans are allowed for examples. We could also easily support:

 - external links
 - relative links to an examples/ folder in the repository with files.
