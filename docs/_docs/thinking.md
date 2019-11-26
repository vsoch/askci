---
title: Thinking
description: Brainstorming and general design thinking
---

## Overview

This is a new project - an attempt to build a version controlled, documentation
support forum.

## How might this work?

Each repository is a knowledge repository, meaning that is represents a single term or concept that folks might have questions about. 

## Authentication

A user can be anonymous and view content of the site, or authenticate with GitHub (or similar)
to log in and make changes. When the user logs in, this gives access to the full GitHub API.

## Repository Structure

 - organization: is a group of moderators for a family of topics
 - repository: is a single topic or concept

When adding knowledge, the user must be connected to GitHub. We first
ask for the term or concept to add (it will be added under `library/<term>`
and then for a repository to connect to (`<organization>/<repo>`). The GitHub
namespace does not need to match the term name. We will have a template
repository that will be used to populate the new respository, with the
following structure:

```bash
README.md             # The main content of the article is in the README so it's rendered immediately
.github/              # Each template comes with community files
    CONTRIBUTING.md
    CODE_OF_CONDUCT.md
    PULL_REQUEST.md
    workflows/
       main.yml     # tests required before commit to master (and webhook update?) 
```

I had originally intended to use a template proper, but the API doesn't seem to
be working to use it, so I'm trying a fork instead. With a fork, each knowledge
repository can always be updated from the upstream master. I might actually
do a task to handle this as a regular job.

## Adding Knowledge

The main logic works by way of continuous integration and webhooks.

 1. The user changes a knowledge item in the interface. This triggers a [repository dispatch](https://developer.github.com/v3/activity/events/types/#repositorydispatchevent) event. The event triggers a GitHub action that will create a new branch and push the updates to it, and open a pull request.
 2. The owner of the repository is notified, and the pull request is reviewed.
 3. On merge to master, another webhook is triggered (push event) that grabs the commit id, and the updated content.
 
The interface should keep an update of pull requests in progress for the term? Or link to them?
This assumes that knowledge owners are okay with using GitHub and managing pull requests.


## Asking Questions

A question will be linked to a GitHub issue. 

 - Each article model links to questions
 - The questions can be searched from the home screen of the site
 - If a question isn't found, the user can find a related topic
 - If the topic doesn't exist, he/she can make it (or request it to be made)
 - If a related topic exists, the user asks the question to the GitHub issue board
 - The question is then embedded in the text
 - The interface should have an editor with an easy way to "insert a question here"

### Questions to Think About

 - **knowledge ownership**: How do we manage permissions? Meaning, how do we assign a group of moderators to an organization, under which we have some family of concepts? Is GitHub permissions going to make people happy?
 - **templates**: each repository (based on type?) could have some custom markdown file(s) template that knows how to render
 - **examples**: if the repository serves associated content, how do we link to or render it? It might be simple enough to just look for an examples folder, and if it exists, direct the reader to it.
 - **branches**: to start, we should just use master branch
 
The following is from the [original conception](https://github.com/researchapps/helpme-server) that I was thinking of in 2017. Instead of creating a server that would require hosting,
I opted to create [helpme](https://vsoch.github.io/helpme) instead.

## What do I want to build?

1. A user or organization creates a "issue-router," which is simply a board that will handle logic for directing issues to their respective knowledge bases.  The helpme command line tool is configured to send issues here.
 - each issue will have an environment and capture (asciinema)
 - each issue will be associated with a user (authenticated in some way based on the setup)
2. On the cluster (or other) resource, the config file for "helpme" will have a call to post an issue to the issue-router on behalf of the user. The user credentials (authorization) are handled with some custom authentication backend (e.g., LDAP), or a private account.
3. The upload process does the following:
 - Asks the user for various metadata
 - Records a capture and the environment
 - checks for environment variables (e.g., tags or topics) to send to the router.
4. Upon receiving a new issue, the router checks tags / topics and then sends a webhook to one or more knowledge repos that match the tags. If there are no matches, it is not hooked (and some message should show that knowledge isn't found / should be made). This means that upon config of the issue router, one or more tags should be assigned to other repositories. E.g.:

 
```
error --> stanford-error
error+sherlock --> sherlock-error
```

The specific way of tagging and matching is TBD. The general idea is that then the webhook sends the issue down a chain of knowledge repos, each of which assesses the new issue (content extracted, webhooks, etc) and then matches it against its own content. A response with a uri to the match is then sent back to the issue tracker for the user to find.

5. The user (on the command line) gets a link to the original issue-router, which will have a manifest / direction of where knowledge for the answer can be found. In the future, it could include a direct link to the content / answer and return this to the user.

## Plan of Action

1. First customize the interface so it is "HelpMe" branded
2. Figure out if gogs has an API. If so, turn it on
3. Create a command line tool (helpme container) that is able to collect a help request, record asciinema, and then submit to an API endpoint.
4. Figure out how to (programatically? In the interface?) configure a webhook to trigger other repos, and then do something with the content.
