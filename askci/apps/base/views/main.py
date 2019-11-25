"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render

from ratelimit.decorators import ratelimit
from askci.apps.main.models import Article, Question, Tag
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def about_view(request):
    return render(request, "main/about.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def terms_view(request):
    return render(request, "terms/usage_agreement_fullwidth.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def privacy_view(request):
    return render(request, "terms/privacy_agreement.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index_view(request):
    """Show new questions and articles.
    """
    context = {}

    # Counts go into the bar chart, should be scaled similarity
    context["counts"] = {
        "questions": Question.objects.count(),
        "articles": Article.objects.count(),
        "tags": Tag.objects.count(),
    }
    return render(request, "main/index.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def contact_view(request):
    return render(request, "main/contact.html")
