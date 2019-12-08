"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db.models import Count
from django.shortcuts import render
from django.http import Http404
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Tag
from askci.apps.main.utils import get_paginated
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

import os


## Tag Details


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def all_tags(request):
    """Show all tags, with recently created first
    """
    tags_set = (
        Tag.objects.order_by("-modified")
        .annotate(count=Count("article_tags"))
        .order_by("count")
    )
    tags = get_paginated(request, tags_set)
    return render(request, "tags/all.html", {"tags": tags})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def tag_details(request, tag):
    """Show details for a tag"""
    try:
        instance = Tag.objects.get(tag=tag)
        return render(request, "tags/tag_details.html", context={"instance": instance})
    except Tag.DoesNotExist:
        raise Http404
