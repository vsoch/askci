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

from askci.settings import DOMAIN_NAME
from askci.apps.main.models import Article, Question, TemplateRepository
from askci.apps.main.tasks import update_article
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block
from askci.apps.main.github import open_issue

import os
import uuid

## All Questions view is shown on front page in base -> main/index.html


def get_article(name):
    """a general function to get an article, returns None if doesn't exist
    """
    article = None
    if name is not None:
        try:
            article = Article.objects.get(name=name)
        except Article.DoesNotExist:
            pass
    return article


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def new_question(request, name=None):
    """create a new question associated with an article. This comes down
       to selecting an article (associated with a repository) and then
       opening an issue on the GitHub board.
    """

    # If a name is given the user has already chosen an article
    article = None
    if name is not None:
        article = get_article(name)
        if not article:
            messages.info(request, "We couldn't find article '%s'" % name)

    context = {
        "article": article,
        "articles": Article.objects.order_by("-name"),
        "templates": TemplateRepository.objects.all(),
    }

    if request.method == "POST":

        name = request.POST.get("article")
        summary = request.POST.get("summary")
        title = request.POST.get("title")

        # Add link to the article to the summary
        summary += "<br> %s/%s" % (DOMAIN_NAME.strip("/"), article.get_absolute_url())

        article = get_article(name)
        if not article:
            messages.info(request, "We couldn't find article '%s'" % name)

        # Open an issue with the question on the GitHub issues board
        else:
            response = open_issue(request.user, article, title, summary)
            if response:
                url = response.get("url", "#")
                # Format the url to be a link
                url = "<a href='%s' target='_blank'>your question!</a>" % url
                messages.info(
                    request, "An issue has been opened with your question %s" % url
                )
            else:
                messages.info(
                    request,
                    "There was a problem posting your question, are you authenticated with GitHub?",
                )

    return render(request, "questions/new_question.html", context)
