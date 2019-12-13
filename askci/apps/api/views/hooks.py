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
       this function is explicitly for GitHub for the main operations of the
       site. For general webhooks, see reveive_webhook below.
    """
    if request.method == "POST":

        # Has to have Github-Hookshot
        if re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]) is not None:
            return receive_github_hook(request)

    return JsonResponseMessage(message="Invalid request.")


@csrf_exempt
def receive_webhook(request):
    """receive_webhook will parse a validated webhook from an external server.
       for GitHub webhooks assciated with core functionality of the server,
       see receive_hook above.
    """
    if request.method == "POST":

        print(request.META)
        print(request.POST)
        print(request.body)

    return JsonResponseMessage(message="received.", status=200)
