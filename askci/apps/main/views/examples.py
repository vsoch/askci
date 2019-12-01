"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render
from ratelimit.decorators import ratelimit

from askci.apps.main.models import Example
from askci.apps.main.utils import get_paginated
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

import os
import uuid


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def all_examples(request):
    """Show all examples, ordered by most recent
    """
    example_set = Example.objects.order_by("-modified")
    examples = get_paginated(request, example_set)
    return render(request, "examples/all.html", {"examples": examples})
