"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render
from django.http import HttpResponse
from ratelimit.decorators import ratelimit
from askci.apps.main.models import Article

from askci.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    NODE_URI,
)

from datetime import datetime
import json
import csv


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def export(request):
    """Export articles, or repository listing.
    """
    articles = Article.objects.order_by("-modified")
    return render(request, "export/export_knowledge.html", {"articles": articles})


# Export All (repos or articles)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def download_repos_csv(request):
    """download a csv for all repositories
    """
    response = HttpResponse(content_type="text/csv")

    filename = "%s-repos-%s.csv" % (NODE_URI, datetime.now().strftime("%Y-%m-%d"))
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename
    columns = ["article_name", "article_namespace", "article_repo", "article_commit"]

    writer = csv.writer(response)
    writer.writerow(columns)

    for article in Article.objects.order_by("-modified"):
        repo = "https://github.com/%s" % article.repo["full_name"]
        writer.writerow([article.name, article.namespace, repo, article.commit])

    return response


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def download_articles_json(request, name=None):
    """export a json dump of all current articles
    """
    data = {}
    articles = Article.objects.order_by("-modified")

    # Does the user want a single article?
    if name is not None:
        articles = Article.objects.filter(name=name)

    for article in articles:
        content = {
            "text": article.text,
            "uuid": str(article.uuid),
            "name": article.name,
            "uri": article.uri,
            "created": str(article.created),
            "modified": str(article.modified),
            "commit": article.commit,
            "summary": article.summary,
            "repo": "https://github.com/%s" % article.repo["full_name"],
        }
        data[article.name] = content

    filename = "%s-articles-%s.json" % (NODE_URI, datetime.now().strftime("%Y-%m-%d"))
    response = HttpResponse(json.dumps(data, indent=4), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename
    return response


# Export Single Article


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def download_article_text(request, uuid):
    """download text for a single article
    """
    try:
        article = Article.objects.get(uuid=uuid)
        response = HttpResponse(article.text, content_type="text/plain")
        filename = "%s-article-%s-%s.md" % (
            NODE_URI,
            article.name,
            datetime.now().strftime("%Y-%m-%d"),
        )
        response["Content-Disposition"] = 'attachment; filename="%s"' % filename
        return response
    except Article.DoesNotExist:
        pass
