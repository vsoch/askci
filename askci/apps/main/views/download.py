"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

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
def download_repos_csv(request):
    """download a csv for all repositories
    """
    response = HttpResponse(content_type="text/csv")
    filename = "%s-repos-%s.csv" % (NODE_URI, datetime.now().strftime("%Y-%m-%d"))
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename

    # TODO need to write this with real data
    columns = ["article_name", "article_namespace", "article_repo", "article_commit"]

    writer = csv.writer(response)
    writer.writerow(columns)

    for article in Article.objects.all():
        writer.writerow(
            [article.name, article.namespace, article.repo["full_name"], article.commit]
        )

    return response


# Json Export


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def download_articles_json(request):
    """export a json dump of all current articles
    """
    # TODO write export of articles here
    data = {}
    response = HttpResponse(json.dumps(data, indent=4), content_type=content_type)
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename
    return response
