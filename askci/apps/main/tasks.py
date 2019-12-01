"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from askci.apps.main.models import Article, Question, Example

from bs4 import BeautifulSoup
from itertools import chain

import markdown
import os
import re
import requests
import sys


def remove_language(code):
    """if the code starts with a single term on the first line, assume it's
       a language and remove it. We will need to test this to see if it works
       in practice.
    """
    lines = code.split("\n")
    if len(lines) > 1:
        words = lines[0].split(" ")
        if len(words) == 1:
            lines = lines[1:]
            code = "\n".join(lines)
    return code


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
    prefixes = ["question", "example"]
    prefix_regex = "^(%s)" % "|".join(prefixes)

    # Keep link to previous questions (and empty article)
    previous = list(chain(article.question_set.all(), article.example_set.all()))
    article.question_set.clear()
    article.example_set.clear()
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
        if "question" in identifier:
            question, created = Question.objects.get_or_create(text=identifier)
            article.question_set.add(question)

        # Examples are added only if found following code section
        else:
            code = span.find_next("code")
            if code:
                cleaned = remove_language(code.text)
                code.string.replace_with(cleaned)
                example, created = Example.objects.get_or_create(
                    text=identifier, code=cleaned
                )
                article.example_set.add(example)

    article.text = content
    article.save()
