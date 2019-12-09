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

from askci.apps.main.models import PullRequest
from askci.apps.main.utils import get_paginated
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

import os


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def all_reviews(request):
    """Show all open reviews, with recently created first
    """
    prs_set = PullRequest.objects.filter(status="open").order_by("-modified")
    prs = get_paginated(request, prs_set)
    return render(request, "reviews/all.html", {"prs": prs})
