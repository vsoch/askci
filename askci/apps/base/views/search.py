"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db.models import Q
from django.shortcuts import render
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Article, Question, Tag
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

from itertools import chain


# General Search ###############################################################


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def search_view(request, query=None):
    """this is the base search view if the user goes to the page 
       without having made a query, or having given a term
       to the url.
    """
    context = {"submit_result": "anything"}

    # First go, see if the user added a query variable as a GET request
    if query is None:
        query = request.GET.get("q")

    query_type = request.GET.get("type")

    if query is not None:
        results = askci_query(query, query_type, request=request)
        context["results"] = results
    return render(request, "search/search.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def run_search(request):
    """The driver to show results for a general search.
    """
    if request.method == "POST":
        q = request.POST.get("q")
    else:
        q = request.GET.get("q")

    if q is not None:
        results = askci_query(q, request=request)
        context = {"results": results, "submit_result": "anything"}
        return render(request, "search/result.html", context)


# Search Function ##############################################################


def articles_query(q):
    """specific search for articles
    """
    return Article.objects.filter(
        Q(name__icontains=q)
        | Q(namespace__icontains=q)
        | Q(text__icontains=q)
        | Q(tags__tag__icontains=q)
        | Q(summary__icontains=q)
    ).distinct()


def questions_query(q):
    """specific search for questions
    """
    return Question.objects.filter(Q(text__icontains=q)).distinct()


def tags_query(q):
    """specific search for tags
    """
    return Tag.objects.filter(Q(tag__icontains=q)).distinct()


def askci_query(q, query_types=None, request=None):
    """run a general query across questions, articles, and tags.
    """
    searches = {
        "articles": articles_query,
        "questions": questions_query,
        "tags": tags_query,
    }

    # If the user doesn't provide one or more types, search all
    if not query_types:
        query_types = list(searches.keys())
    else:
        query_types = query_types.split(",")

    skips = []

    results = []
    for query_type in query_types:
        if query_type in searches and query_type not in skips:
            results = list(chain(results, searches[query_type](q)))

    return results
