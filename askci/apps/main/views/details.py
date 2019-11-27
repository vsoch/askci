"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render
from django.http import Http404
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, Tag
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

import os

## Detail Pages


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
        print(markdown)

    return render(request, "details/article_details.html", {"instance": article})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def tag_details(request, tag):
    try:
        instance = Tag.objects.get(tag=tag)
        return render(
            request, "details/tag_details.html", context={"instance": instance}
        )
    except Tag.DoesNotExist:
        raise Http404
