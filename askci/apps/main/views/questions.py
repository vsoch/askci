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

from askci.apps.main.models import Article, Question
from askci.apps.main.utils import lowercase_cleaned_name
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

## All Questions view is shown on front page in base -> main/index.html


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def new_question(request, name=None):
    """create a new question associated with an article. This comes down
       to selecting an article (associated with a repository) and then
       opening an issue on the GitHub board.
    """
    article = None

    # If a name is given the user has already chosen an article
    if name is not None:
        try:
            article = Article.objects.get(name=name)
        except Article.DoesNotExist:
            messages.info(request, "We couldn't find article '%s'" % name)

    context = {"article": article, "articles": Article.objects.order_by("-name")}

    if request.method == "POST":
        article = request.POST.get("article")
        summary = request.POST.get("summary")
        title = request.POST.get("title")
        print(article)
        print(summary)
        print(title)

        # TODO open issue on GitHub board here
        messages.info(request, "An issue has been opened with your question!")
    return render(request, "questions/new_question.html", context)
