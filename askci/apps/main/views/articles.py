"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.urls import reverse
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, PullRequest, Tag, TemplateRepository
from askci.apps.main.utils import lowercase_cleaned_name, get_paginated
from askci.apps.main.tasks import update_article
from askci.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    USER_ARTICLES_LIMIT,
)
from askci.apps.main.github import (
    copy_repository_template,
    get_admin_namespaces,
    get_repo,
    list_repos,
    create_webhook,
    request_review,
)

import django_rq
import os
import re
import uuid

## Article Actions


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def all_articles(request):
    """Show all articles, with most recently modified first
    """
    article_set = Article.objects.order_by("-modified")
    articles = get_paginated(request, article_set)
    return render(request, "articles/all.html", {"articles": articles})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def article_details(request, name):
    """view an article details, including the rendered markdown and an edit
       field if a user is authenciated with GitHub
    """
    try:
        article = Article.objects.get(name=name)
    except Article.DoesNotExist:
        raise Http404

    if request.method == "POST":
        markdown = request.POST.get("markdown")

        if not request.user.is_authenticated:
            return JsonResponse(
                {"message": "You must be authenticated to perform this action."}
            )

        # Is this the case?
        if not request.user.has_github_create:
            return JsonResponse(
                {"message": "You must connect with GitHub to make this request."}
            )

        # Markdown is missing
        if not markdown:
            return JsonResponse(
                {"message": "You must submit some markdown content for review"}
            )

        # Markdown is not changed
        if markdown == article.text:
            return JsonResponse(
                {"message": "You must change the content to request review."}
            )

        # Each user is only allowed one pending/open PR per article
        user_pr = request.user.get_pr(article)
        if user_pr is not None:
            message = "You already have a review pending for this article!"
            if user_pr.url is not None:
                message += " See or edit the pull request at %s" % user_pr.url
            return JsonResponse({"message": message})

        # Set off a task to parse and submit dispatch request
        status_code, pr_id = request_review(request.user, article, markdown)
        if status_code == 204:

            # Create PullRequest object request
            pr, created = PullRequest.objects.get_or_create(
                pr_id=pr_id, article=article, owner=request.user
            )

            messages.info(
                request,
                "Your changes have been submit for review to %s"
                % article.repo["full_name"],
            )
            return JsonResponse({"message": "success"})
        return JsonResponse({"message": "There was an issue with requesting changes."})

    return render(request, "articles/article_details.html", {"instance": article})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def new_article(request):
    """create a new article, only if the user has the appropriate GitHub 
       credentials. This means forking the template repository,
       renaming it to be about the term, and then editing it to have an
       updated name. In the future we will add topics (tags) here as well.
    """
    if not has_articles_opening(request):
        return redirect("index")

    if request.method == "POST":
        namespace = request.POST.get("namespace")
        summary = request.POST.get("summary")
        term = lowercase_cleaned_name(request.POST.get("term"))
        repository = "askci-term-%s" % term
        repository = os.path.join(namespace, repository)

        # We only have one template repo to start (used as fork)
        template = TemplateRepository.objects.last()

        # Generate the template repository
        repo = copy_repository_template(
            user=request.user,
            template=template.repo,
            repository=repository,
            description=summary,
        )

        # The article repo was created!
        if repo:

            # Generate the webhooks (push/deployment and pull request)
            secret = str(uuid.uuid4())

            webhook = create_webhook(request.user, repo, secret)
            webhook_pr = create_webhook(
                request.user, repo, secret, events=["pull_request"]
            )

            # Save both to webhooks json object
            webhooks = {"push-deploy": webhook, "pull_request": webhook_pr}

            if "errors" in webhook:
                messages.info(request, "Errors: %s" % webhook["errors"])
                return redirect("index")

            # namespace defaults to library
            article = Article.objects.create(
                name=term,
                owner=request.user,
                secret=secret,
                webhook=webhooks,
                repo=repo,
                summary=summary,
            )

            add_article_tags(article)

            # Run the first task
            res = django_rq.enqueue(update_article, article_uuid=article.uuid)

            messages.info(
                request,
                "%s has been created! Refresh the page for updated content." % term,
            )
            return redirect(reverse("article_details", args=[self.article.name]))

        # if we get here, there was an error
        messages.warning(
            request,
            "There was an error creating %s. " % repository,
            "Make sure that the template %s organization " % template.repo,
            "is authenticated with the application here.",
        )

    # username/orgs that the user has admin for (to create webhook)
    namespaces = get_admin_namespaces(request.user)

    context = {"templates": TemplateRepository.objects.all(), "namespaces": namespaces}
    return render(request, "articles/new_article.html", context)


def has_articles_opening(request):
    """a user can only create up to USER_ARTICLES_LIMIT. They also need
       to have the correct permissions.

       Parameters
       ==========
       request: the request object with the user. Must come from
                a view where the user is not allowed to be undefined.
    """
    if request.user.is_anonymous:
        return False

    if not request.user.has_github_create():
        messages.warning(
            request,
            "%s does not have appropriate GitHub permissions to create a knowledge repository."
            % request.user.username,
        )
        return False

    articles = Article.objects.filter(owner=request.user)
    if articles.count() >= USER_ARTICLES_LIMIT:
        messages.info(request, "You are not allowed to create more articles.")
        return False
    return True


def add_article_tags(article):
    """if topics are included in the webhook, add them to the article
    """
    if "topics" in article.webhook:
        if len(article.webhook["topics"]) > 0:
            for topic in webhook["topics"]:
                article.tags.add(topic)
                article.save()


# Import an existing article repository


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def import_article(request):
    """display unconnected repos for the user to import as articles.
       they must start with askci-term to be considered.
    """
    if not has_articles_opening(request):
        return redirect("index")

    if request.method == "GET":
        repos = list_repos(request.user)

        # Filter down to those with admin permission (webhook create)
        repos = [r for r in repos if r["permissions"]["admin"]]

        articles = [x.repo["id"] for x in Article.objects.all()]
        repos = [
            repo
            for repo in repos
            if repo["id"] not in articles and repo["name"].startswith("askci-term")
        ]
        context = {"repos": repos}
        return render(request, "articles/import_article.html", context)

    elif request.method == "POST":

        # The checked repos are sent in format REPO_{{ repo.owner.login }}/{{ repo.name }}
        repos = [
            x.replace("REPO_", "")
            for x in request.POST.keys()
            if re.search("^REPO_", x)
        ]
        secret = uuid.uuid4().__str__()

        if len(repos) > 0:

            # Always just take the first one
            username, reponame = repos[0].split("/")

            # Retrieve the repo fully
            repo = get_repo(request.user, reponame=reponame, username=username)

            # Check again for webhook permission
            if not repo["permissions"]["admin"]:
                messages.info(
                    request, "You must be an admin on the repository to import it."
                )
                return redirect("import_article")

            # Generate the webhook
            secret = str(uuid.uuid4())

            webhook = create_webhook(request.user, repo, secret)
            webhook_pr = create_webhook(
                request.user, repo, secret, events=["pull_request"]
            )

            # Save both to webhooks json object
            webhooks = {"push-deploy": webhook, "pull_request": webhook_pr}

            # If there are errors, or can't create, don't continue
            if "errors" in webhook:
                messages.info(request, "Errors: %s" % webhook["errors"])
                return redirect("import_article")

            # The term is the end of the repository name
            term = reponame.replace("askci-term-", "")

            # namespace defaults to library
            article = Article.objects.create(
                name=term,
                owner=request.user,
                secret=secret,
                webhook=webhooks,
                repo=repo,
                summary=repo["description"],
            )

            add_article_tags(article)

            # Run the first task
            res = django_rq.enqueue(update_article, article_uuid=article.uuid)

            messages.info(
                request,
                "%s has been created! Refresh the page for updated content." % term,
            )
            return redirect(reverse("article_details", args=[self.article.name]))

    return redirect("index")
