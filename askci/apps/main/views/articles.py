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
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, PullRequest, Tag, TemplateRepository
from askci.apps.main.utils import lowercase_cleaned_name, get_paginated
from askci.apps.main.tasks import update_article
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block
from askci.apps.main.github import (
    get_namespaces,
    fork_repository,
    create_webhook,
    request_review,
)

import os
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

            return JsonResponse(
                {
                    "message": "Your changes have been submit for review to %s"
                    % article.repo["full_name"]
                }
            )
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
    if request.method == "POST":
        namespace = request.POST.get("namespace")
        summary = request.POST.get("summary")
        repository = lowercase_cleaned_name(request.POST.get("repository"))
        term = lowercase_cleaned_name(request.POST.get("term"))
        repository = os.path.join(namespace, repository)

        # We only have one template repo to start (used as fork)
        template = TemplateRepository.objects.last()

        # Generate the template repository
        repo = fork_repository(
            user=request.user, template=template.repo, repository=repository
        )

        # The article repo was created!
        if repo:

            # Generate the webhook
            secret = str(uuid.uuid4())
            webhook = create_webhook(request.user, repo, secret)

            # namespace defaults to library
            article = Article.objects.create(
                name=term,
                owner=request.user,
                secret=secret,
                webhook=webhook,
                repo=repo,
                summary=summary,
            )

            # Run the first task
            res = django_rq.enqueue(update_article, article_uuid=article.uuid)

            messages.info(
                request,
                "%s has been created! Refresh the page for updated content." % term,
            )
            return redirect("article_details", args=(article.name,))

        # if we get here, there was an error
        messages.warning(request, "There was an error creating %s" % repository)

    # Request is GET, or POST has error
    if not request.user.has_github_create():
        messages.warning(
            request,
            "%s does not have appropriate GitHub permissions to create a knowledge repository."
            % request.user.username,
        )

    # username/orgs that the user has permission to create
    namespaces = get_namespaces(request.user)

    context = {"templates": TemplateRepository.objects.all(), "namespaces": namespaces}
    return render(request, "articles/new_article.html", context)
