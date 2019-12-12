---
title: About
permalink: /about/
---

# About

AskCI Server is a version controlled, documentation and knowledge support server. What does that mean?

 - **version control**: All content is created, worked on, and updated on GitHub.
 - **documentation and knowledge**: each article (repository) corresponds to a single concept or idea, akin to Wikipedia
 - **support**: questions are embedded in articles, and then indexed by the server. A user can ask a question via the interface or a connected tool to easily find an answer, whether it be in the text, or a code snippet example.

See the [repository]({{ site.repo }}) for more details, or continue reading below.

## Background

I invisioned creating a shared documentation server back in 2017, something I called "The Documentation Octopus" since it would span multiple universities.  See the [history](#history) section below for this original thinking.
I started to work on a [server](https://www.github.com/researchapps/helpme-server) that users could submit help requests to, but realized that a much more extendable tool would be to provide a client that can submit help requests to already existing servers. 
That project turned into [helpme](https://www.github.com/vsoch/helpme) and the server was largely abandoned. 
I joined the [AskCI](https://ask.ci) community at the end of 2018, and while we use a Discourse installation, it still feels like many elements are missing. 
Since I can make some time, I figured I'd give this another go.

## Concepts

 - **articles**: an article is a topic or concept that you might want to ask questions about. On a high level, it's a piece of knowledge that can be collaboratively worked on. On a functional level, an article on AskCI corresponds to a single GitHub repository. See the [repository technical specification]({{ site.baseurl }}/docs/repository-spec) for information about how this works.
 - **questions**: a question is an embedded inquiry in an article that is indexed and searchable.
 - **user**: can be a visitor (non-authenticated), an editor or reviewer (authenticated but without ownership of knowledge repos) or an owner (authenticated with ownership). Visitors can browse content, editors and reviewers can update or ask new questions, and owners can do all of the above plus serve as maintainers for the knowledge repos.

Those are the basic units of the site. What we can we do with them?

## Actions

 - **ask a question** the user can ask a question to find existing content, or ask a new question
 - **create an article** a new article (and repository) can be created for a new concept or erm
 - **application programming interface (api)**: can be used to support external tools.

For more details about how these actions work, see the [repository technical specification]({{ site.baseurl }}/docs/repository-spec), or the [getting started walkthrough]({{ site.baseurl }}/docs/getting-started)

## History
 
The following is from the [original conception](https://github.com/researchapps/helpme-server) that I was thinking of in 2017. Instead of creating a server that would require hosting,
I opted to create [helpme](https://vsoch.github.io/helpme) instead.

### What do I want to build?

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

### Plan of Action

1. First customize the interface so it is "HelpMe" branded
2. Figure out if gogs has an API. If so, turn it on
3. Create a command line tool (helpme container) that is able to collect a help request, record asciinema, and then submit to an API endpoint.
4. Figure out how to (programatically? In the interface?) configure a webhook to trigger other repos, and then do something with the content.


## Support

If you need help, please don't hesitate to [open an issue](https://www.github.com/{{ site.repo }}).
