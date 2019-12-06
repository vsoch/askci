"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from askci.apps.main.github.utils import JsonResponseMessage, load_body
from askci.apps.main.github import receive_github_hook
from askci.apps.main.github.utils import JsonResponseMessage
from askci.settings import DISABLE_WEBHOOKS
from askci.apps.users.models import User
from askci.apps.main.models import PullRequest, Article

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


@csrf_exempt
def receive_pr_request(request):
    """receive_pr_request to update a PullRequest object associated with an article
       and user.      
    """
    if request.method == "POST":

        if DISABLE_WEBHOOKS:
            return JsonResponseMessage(message="Webhooks disabled")

        if not re.search("AskCI", request.META["HTTP_USER_AGENT"]):
            return JsonResponseMessage(message="Agent not allowed")

        if request.META["CONTENT_TYPE"] not in [
            "application/json",
            "application/x-www-form-urlencoded",
        ]:
            return JsonResponseMessage(message="Incorrect content type")

        article = payload.get("article")
        branch = payload.get("branch")
        title = payload.get("title")
        owner = payload.get("owner")
        user = payload.get("user")
        url = payload.get("url")

        # The number is the last part of the url
        number = int(url.split("/")[-1])

        for var in [article, branch, title, owner, user, url]:
            if not var:
                return JsonResponseMessage(message="Malformed request")

        # Only allow master
        if not branch.startswith('update/term'):
            return JsonResponseMessage(message="Invalid request")

        # Get the article
        try:
            article = Article.objects.get(uuid=article)
        except Article.DoesNotExist:
            return JsonResponseMessage(message="Invalid request")

        # Get the user and owner
        try:
            user = User.objects.get(username=user)
            owner = User.objects.get(username=owner)
        except User.DoesNotExist:
            return JsonResponseMessage(message="Invalid request")

        # Get the pull request
        try:
            pr = PullRequest.objects.get(article=article, status="pending", owner=user)
        except PullRequest.DoesNotExist:
            return JsonResponseMessage(message="Invalid request")

        # Ensure that the pr_id is provided in the header, can only be used once
        if pr.pr_id not in request.META["Authorization"]:
            return JsonResponseMessage(message="Invalid request")

        if pr.article.owner != owner:
            return JsonResponseMessage(message="Invalid request")

        # Update pull request to be open
        pr.status = "open"
        pr.number = number
        pr.pr_id = uuid.uuid4()
        pr.url = url
        pr.save()

        return JsonResponseMessage(
            message="Pull Request updated.", status=200, status_message="Received"
        )

    return JsonResponseMessage(message="Invalid request.")
