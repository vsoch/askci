"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from askci.apps.main.github.utils import JsonResponseMessage
from askci.apps.main.github import receive_github_hook
from askci.apps.main.github.utils import JsonResponseMessage
from askci.settings import DISABLE_WEBHOOKS
from askci.apps.users.models import User
from askci.apps.main.models import PullRequest, Article


@csrf_exempt
def receive_hook(request):
    """receive_hook will parse a valid GitHub hook, otherwise ignore it.
    """
    if request.method == "POST":

        # Has to have Github-Hookshot
        if re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]) is not None:
            return receive_github_hook(request)

        # TODO: this function also needs an indicator if it came from a closed PR
        # If so, get the pull request object, delete.

    return JsonResponseMessage(message="Invalid request.")


@csrf_exempt
def receive_pr_request(request):
    """receive_pr_request to update a PullRequest object associated with an article
       and user.
       
       TODO:

         Article Page
         1. Render questions as anchor/links on article page
         2. Render associated Pull Request objects to encourage review participation     

         Webhook Receive
         Run same function to update README.

         Request Review Hook
         1. create model to hold PR url and user identifier, status should be request, open, closed
         2. parse request here (once online) to get github markers to validate
         3. from request.POST we should get pr_id
         4. relevant variables for model

            echo $URL
            echo $ARTICLE
            echo $BRANCH
            echo $TITLE
            echo $PR_ID
            echo $REQUEST_USER
            echo $OWNER

            https://api.github.com/repos/manbat/askci-term-singularity/pulls/4
            xxxx-xxxx-xxxx-xxxx
            update/term-manbat-2019-11-27
            Request for Term Update Review
            xxxx-xxxx-xxxx-xxxx
            manbat
            manbat
    """
    if request.method == "POST":

        print(request.META)

        if DISABLE_WEBHOOKS:
            return JsonResponseMessage(message="Webhooks disabled")

        if not re.search("AskCI", request.META["HTTP_USER_AGENT"]):
            return JsonResponseMessage(message="Agent not allowed")

        # Only allow application/json content type
        if request.META["CONTENT_TYPE"] != "application/json":
            return JsonResponseMessage(message="Incorrect content type")

        # TODO check that coming from GitHub server

        # Parse the body
        payload = load_body(request)
        print(payload)

        article = payload.get("article")
        branch = payload.get("branch")
        title = payload.get("title")
        owner = payload.get("owner")
        user = payload.get("user")
        url = payload.get("url")

        for var in [article, branch, title, owner, user, url]:
            if not var:
                return JsonResponseMessage(message="Malformed request")

        # Only allow master
        if branch != "master":
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

        # Check header for pr_id

        # Retrieve the article (need to test this)
        try:
            article = Article.objects.get(repo__full_name=repo["full_name"])
        except Article.DoesNotExist:
            return JsonResponseMessage(message="Article not found", status=404)

        # Get the pull request
        try:
            pr = PullRequest.objects.get(article=article, status="pending", owner=user)
        except PullRequest.DoesNotExist:
            return JsonResponseMessage(message="Invalid request")

        if pr.pr_id not in request.META["Authorization"]:
            return JsonResponseMessage(message="Invalid request")

        if pr.article.owner != owner:
            return JsonResponseMessage(message="Invalid request")

        # Update pull request to be open
        pr.status = "open"
        pr.pr_id = None
        pr.url = url
        pr.save()

        return JsonResponseMessage(
            message="Pull Request updated.", status=200, status_message="Received"
        )

    return JsonResponseMessage(message="Invalid request.")
