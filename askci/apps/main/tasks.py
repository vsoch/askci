"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from askci.apps.main.models import Article, Question

from bs4 import BeautifulSoup

import markdown
import os
import re
import requests
import sys


def update_article(article_uuid):
    """take a request and an associated article, and grab
       the latest README to update content on the site.
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        pass

    # Formulate the url for raw github content
    url = (
        "https://raw.githubusercontent.com/%s/master/README.md"
        % article.repo["full_name"]
    )
    content = requests.get(url).text
    html = markdown.markdown(content)

    # Parse the content for questions
    soup = BeautifulSoup(html, "lxml")

    # Supported span prefixes
    prefixes = ["question"]
    prefix_regex = "^(%s)" % "|".join(prefixes)

    # Keep link to previous questions (and empty article)
    previous = article.question_set.all()
    article.question_set.clear()
    [p.delete() for p in previous]

    # Add correctly formatted spans (this is same as testing in repository)
    for span in soup.find_all("span"):

        # The span is required to have an id
        identifier = span.attrs.get("id")
        if not identifier:
            continue

        # The span id must start with a valid prefix
        if not re.search(prefix_regex, identifier):
            continue

        # The span id must have all lowercase, no special characters or spaces
        if re.search("[^A-Za-z0-9-]+", identifier):
            continue

        # If the question is valid, get or create
        question, created = Question.objects.get_or_create(text=identifier)
        article.question_set.add(question)

    article.text = content
    article.save()
