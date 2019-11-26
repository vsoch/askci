"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import Http404
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, Tag, TemplateRepository
from askci.apps.main.utils import lowercase_cleaned_name
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block
from askci.apps.main.github import get_namespaces, fork_repository, create_webhook

import os
import uuid

## Article Actions

## TODO: an edit function should trigger the repository_dispatch event to
# create a new branch and open a PR. https://developer.github.com/v3/repos/#create-a-repository-dispatch-event
## The page should have some way to display PRs in progress, so a user can see
## previous submissions.


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
            return redirect("article_details", args=(article.uuid,))

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
