"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import Http404
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, Tag, TemplateRepository
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block
from askci.apps.main.github import get_namespaces, copy_repository_template

import os

## Article Actions


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def new_article(request):
    """create a new article, only if the user has the appropriate GitHub 
       credential
    """
    if request.method == "POST":
        namespace = request.POST.get("namespace")
        repository = request.POST.get("repository")
        repository = os.path.join(namespace, repository)

        # We only have one template repo to start
        template = TemplateRepository.objects.last()

        # Generate the template repository
        article = copy_respository_template(
            user=user, template=template.repo, repository=repository
        )

        # The article was created!
        if article:
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
