"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from askci.apps.main.github.utils import JsonResponseMessage
from askci.apps.main.github import receive_github_hook

import uuid
import re


@csrf_exempt
def receive_hook(request):
    """receive_hook will parse a valid GitHub hook, otherwise ignore it.
    """
    if request.method == "POST":

        # Has to have Github-Hookshot
        if re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]) is not None:
            return receive_github_hook(request)

    return JsonResponseMessage(message="Invalid request.")
