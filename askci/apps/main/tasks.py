"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from askci.apps.main.models import Article, Question
from dateutil.parser import parse
import os
import re


def parse_hook(article_uuid):
    """parse hook will take a request and an associated article, and grab
       the latest README to update content on the site.
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        pass

    # TODO write me - how to update an article?
