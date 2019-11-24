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


def get_instance(request, uuid, Model):
    """a helper to get an instance of a particular type based on its uuid. If
       we find the instance, we return it's details page. If not, 
       we return a 404.
    """
    try:
        instance = Model.objects.get(uuid=uuid)
        template = "details/%s_details.html" % instance.get_label()
        return render(request, template, context={"instance": instance})
    except Model.DoesNotExist:
        raise Http404


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def article_details(request, uuid):
    return get_instance(request, uuid, Article)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def tag_details(request, uuid):
    return get_instance(request, uuid, Tag)
