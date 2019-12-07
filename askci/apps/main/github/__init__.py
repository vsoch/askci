"""

Copyright (C) 2016-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import django_rq

from askci.apps.main.tasks import repository_change, update_article, update_pullrequest
from askci.apps.users.models import User
from askci.apps.main.models import Article
from askci.settings import DISABLE_WEBHOOKS, DOMAIN_NAME

from .utils import (
    check_headers,
    get_default_headers,
    JsonResponseMessage,
    load_body,
    paginate,
    validate_payload,
    DELETE,
    POST,
)

from dateutil.parser import parse
from datetime import datetime
import re
import requests
import uuid
import json

api_base = "https://api.github.com"


## Authentication


def get_auth(user, headers=None, idx=0):
    """get_auth will return the authentication header for a user
       the default headers (without auth) are returned if provider not github

       Parameters
       ==========
       user: a user object
    """
    if headers is None:
        headers = get_default_headers()

    # Tasks might provide a user id instead
    if not isinstance(user, User):
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            pass

    token = get_auth_token(user)

    if token is not None:
        token = "token %s" % (token)
        headers["Authorization"] = token
    return headers


def get_auth_token(user):
    """get_auth_token will return the auth token for a user.

       Parameters
       ==========
       user: a user object
    """
    # 1. Github with repo permissions first priority
    auth = [x for x in user.social_auth.all() if x.provider == "github"]

    # 2. Github public second priority
    if not auth:
        auth = [x for x in user.social_auth.all() if x.provider == "github-readonly"]

    if auth:
        return auth[0].access_token


# Meta


def get_meta():
    """return meta endpoint, allowing to ensure requests are from GitHub
       servers. See https://developer.github.com/v3/meta/
    """
    url = "%s/meta" % api_base
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()


# Repositories


def get_repo(user, reponame, username, headers=None):
    """get_repo will return a single repo, username/reponame
       given authentication with user

       Parameters
       ==========
       user: the user to get github credentials for
       reponame: the name of the repo to retrieve
       username: the username of the repo (owner)
    """
    # Case 1, the user just has one auth or just public
    if headers is None:
        headers = get_auth(user)
    headers["Accept"] = "application/vnd.github.mercy-preview+json"
    url = "%s/repos/%s/%s" % (api_base, username, reponame)
    response = requests.get(url, headers=headers)

    # Case 2: public and private
    if response.status_code != 200:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        response = requests.get(url, headers=headers)
    response = response.json()
    return response


def get_admin_namespaces(user):
    """get user namespaces, and then look up which the user has admin access 
       (to create webhooks)
    """
    namespaces = [user.username]
    headers = get_auth(user)

    url = "%s/user/memberships/orgs" % api_base
    response = requests.get(url, headers=headers)

    for org in response.json():
        if org["role"] == "admin":
            namespaces.append(org["organization"]["login"])
    return namespaces


def get_namespaces(user):
    """for a given user, list the organizations and username (namespaces)
       they have create access to.
    """
    namespaces = []
    if not user.has_github_create():
        return namespaces

    headers = get_auth(user)

    namespaces = [user.username]
    # this url is supposed to return public/private but doens't seem to work
    # url = "%s/user/orgs" % api_base
    url = "%s/users/%s/orgs" % (api_base, user.username)
    response = requests.get(url, headers=headers)

    # User can create for personal repo, not org
    if response.status_code in [401, 403]:
        return namespaces

    response = response.json()

    # No orgs to add
    if not response:
        return namespaces

    namespaces = namespaces + [x["login"] for x in response]
    return namespaces


def open_issue(user, article, title, summary):
    """given a user with GitHub permissions, an article, and markdown, dispatch an action
       to generate a pull request and return the link to the user.
    """
    # User must be authenticated with GitHub create
    if not user.has_github_create():
        return

    headers = get_auth(user)
    headers["Accept"] = "application/vnd.github.symmetra-preview+json"
    data = {"title": title, "body": summary}

    # Data should include updated markdown (for README)
    url = "%s/repos/%s/issues" % (api_base, article.repo["full_name"])
    response = requests.post(url, headers=headers, json=data)

    return response.json()


def request_review(user, article, markdown):
    """given a user with GitHub permissions, an article, and markdown, dispatch an action
       to generate a pull request and return the link to the user.
    """
    # Must be authenticated with GitHub create? (need to check this)
    if not article.owner.has_github_create():
        return

    # Replace all "\r\n" with just \n
    markdown = markdown.replace("\r\n", "\n")
    headers = get_auth(article.owner)
    headers["Accept"] = "application/vnd.github.everest-preview+json"

    data = {
        "event_type": "request_review_by_%s" % user.username,
        "client_payload": {
            "markdown": markdown,
            "username": user.username,
            "article": str(article.uuid),
            "event_name": "request-review",
        },
    }

    # Data should include updated markdown (for README)
    url = "%s/repos/%s/dispatches" % (api_base, article.repo["full_name"])
    response = requests.post(url, headers=headers, json=data)
    return response.status_code


def fork_repository(user, template, repository=None):
    """Fork a repository. If repository is defined, rename to this

       Parameters
       ==========
       user: the user to request permission to fork. Must be connected to the 
             GitHub API.
       template: the template repository name (https://github.com/<user>/<repo>
       repository: rename the fork to this <user>/<repo>
    """
    repo = None
    if user.has_github_create():
        headers = get_auth(user)
        headers["Accept"] = "application/vnd.github.baptiste-preview+json"

        repo_owner, repo_name = template.split("/")[-2:]

        # Default data is None
        data = None

        # If the repository is to be renamed
        if repository is not None:
            owner, term_name = repository.split("/")

            # If the owner isn't the user, we need to specify data
            if owner != user.username:
                data = {"organization": owner}

        url = "%s/repos/%s/%s/forks" % (api_base, repo_owner, repo_name)
        response = requests.post(url, headers=headers, json=data)

        # Success?
        if response.status_code in [200, 202, 201]:
            repo = response.json()

            # Rename it with the edit api, and ensure has issues
            updates = {"has_issues": True}
            if repository is not None:
                updates["name"] = term_name

            url = "%s/repos/%s/%s" % (api_base, owner, repo_name)
            response = requests.patch(url, headers=headers, json=updates)
            if response.status_code == 200:
                repo = response.json()

    return repo


def copy_repository_template(user, template, repository, description=None):
    """create a repository from a template, and return content to connect
       to an article. Returns None if not possible. The organization
       for which the template belongs must be authenticated with the repo.
    """
    if user.has_github_create():
        headers = get_auth(user)
        headers["Accept"] = "application/vnd.github.baptiste-preview+json"

        template_owner, template_repo = template.split("/")[-2:]
        owner, repo = repository.split("/")

        data = {
            "owner": owner,
            "name": repo,
            "description": description or "Documentation repository for AskCI",
        }
        url = "%s/repos/%s/%s/generate" % (api_base, template_owner, template_repo)
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            return response.json()


def list_repos(user, headers=None):
    """list_repos will list the public repos for a user

       Parameters
       ==========
       user: a user object to list
       headers: headers to replace default
    """
    if headers is None:
        headers = get_auth(user)

    url = "%s/user/repos" % (api_base)
    repos = paginate(url=url, headers=headers)
    return repos


# Webhooks


def create_webhook(
    user, repo, secret, events=["push", "deployment"], reverse_url="receive_hook"
):
    """create_webhook will create a webhook for a repo to send back
       to askci on push.

       Parameters
       ==========
       user: user: should be an askci user with GitHub authentication.
       repo: should be a complete repo object, including username and reponame
       secret: should be a randomly generated string, created when repo connected,
               to validate future pushes
    """
    if user.has_github_create():
        headers = get_auth(user)
        url = "%s/repos/%s/hooks" % (api_base, repo["full_name"])
        callback_url = "%s%s/" % (DOMAIN_NAME.strip("/"), reverse(reverse_url))
        config = {"url": callback_url, "content_type": "json", "secret": secret}

        params = {"name": "web", "active": True, "events": events, "config": config}

        # Create webhook
        response = POST(url, headers=headers, data=params)
        response = response.json()

        return response


## Delete


def delete_webhook(user, repo, hook_id):
    """delete_webhook will delete a webhook, done when a user deletes a collection.
       https://developer.github.com/v3/repos/hooks/#delete-a-hook
       DELETE /repos/:owner/:repo/hooks/:hook_id

       Parameters
       ==========
       user: should be a singularity hub user. This is used to get
             the Github authentication
       repo: should be a complete repo object, including username and reponame
    """
    if user.has_github_create():
        headers = get_auth(user)
        url = "%s/repos/%s/hooks/%s" % (api_base, repo, hook_id)

        response = DELETE(url, headers)
        return response.json()


# Receive GitHub webhook


@csrf_exempt
def receive_github_hook(request):
    """a hook is sent on some set of events, specifically:

          push/deploy: indicates that the content for the repository changed
          pull_request: there is an update to a pull request.

         This function checks that (globally) the event is valid, and if
         so, runs a function depending on the event.
    """
    # We do these checks again for sanity
    if request.method == "POST":

        if DISABLE_WEBHOOKS:
            return JsonResponseMessage(message="Webhooks disabled")

        if not re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]):
            return JsonResponseMessage(message="Agent not allowed")

        # Only allow application/json content type
        if request.META["CONTENT_TYPE"] != "application/json":
            return JsonResponseMessage(message="Incorrect content type")

        # Check that it's coming from the right place
        required_headers = ["HTTP_X_GITHUB_DELIVERY", "HTTP_X_GITHUB_EVENT"]
        if not check_headers(request, required_headers):
            return JsonResponseMessage(message="Agent not allowed")

        # Has to be a push, deployment, or pull_request
        event = request.META["HTTP_X_GITHUB_EVENT"]

        # Ping happens on setup
        if event == "ping":
            return JsonResponseMessage(
                message="Ping received, no action taken.", status=200
            )

        # But don't allow types beyond push, deploy, pr
        if event not in ["push", "deployment", "pull_request"]:
            return JsonResponseMessage(message="Incorrect delivery method.")

        # A signature is also required
        signature = request.META.get("HTTP_X_HUB_SIGNATURE")
        if not signature:
            return JsonResponseMessage(message="Missing credentials.")

        # Parse the body
        payload = load_body(request)
        repo = payload.get("repository")

        # Retrieve the article
        try:
            article = Article.objects.get(repo__full_name=repo["full_name"])
        except Article.DoesNotExist:
            return JsonResponseMessage(message="Article not found", status=404)

        # Don't continue if the repository is archived (this shouldn't happen)
        if article.archived:
            return JsonResponseMessage(message="Repository is archived.")

        # Validate the payload with the collection secret
        status = validate_payload(
            secret=str(article.secret),
            payload=request.body,
            request_signature=signature,
        )

        if not status:
            return JsonResponseMessage(message="Invalid credentials.")

        # Branch must be master
        branch = payload.get("ref", "refs/heads/master").replace("refs/heads/", "")

        # Update repo metadata that might change
        article.repo = repo
        article.save()

        # Submit job with django_rq to update article
        if event == "pull_request":

            against_branch = payload["pull_request"]["base"]["ref"]
            branch = payload["pull_request"]["head"]["ref"]

            if not branch.startswith("update/term") or against_branch != "master":
                return JsonResponseMessage(message="Ignoring branch.", status=200)

            # Requesting user is derived from branch
            user = branch.replace("update/term-", "").split("-")[0]

            res = django_rq.enqueue(
                update_pullrequest,
                article_uuid=article.uuid,
                user=user,
                action=payload["action"],
                url=payload["pull_request"]["html_url"],
                number=payload["number"],
                merged_at=payload["pull_request"]["merged_at"],
            )

        elif event in ["push", "deployment"]:
            if branch != "master":
                return JsonResponseMessage(message="Ignoring branch.", status=200)

            article.commit = payload["after"]
            article.save()
            res = django_rq.enqueue(update_article, article_uuid=article.uuid)

        elif event == "repository":
            res = django_rq.enqueue(
                repository_change,
                article_uuid=article.uuid,
                action=payload["action"],
                repo=json.dumps(payload["repository"]),
            )

        return JsonResponseMessage(
            message="Hook received and parsing.", status=200, status_message="Received"
        )

    return JsonResponseMessage(message="Invalid request.")
