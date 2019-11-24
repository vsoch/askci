"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import Http404
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, Question, Tag
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

import os


## Catalogs

# TODO: make these templates
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def catalog_view(request):
    return render(request, "catalogs/catalog.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def articles_catalog_view(request):
    context = {"articles": Article.objects.all()}
    return render(request, "catalogs/articles.html", context=context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def questions_catalog_view(request):
    context = {"questions": Question.objects.all()}
    return render(request, "catalogs/questions.html", context=context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def tags_catalog_view(request):
    context = {"tags": Tag.objects.all()}
    return render(request, "catalogs/tags.html", context=context)
