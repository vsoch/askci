"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from askci.apps.main.github.utils import JsonResponseMessage
from askci.apps.main.github import receive_github_hook


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

        # Validate from GitHub

        # lookup article based on id

        # retrieve pull request based on requesting user, article, owner

        # change status of PR to be open (should render on page with link)

        # update PullRequest with url

        # Has to have Github-Hookshot
        if re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]) is not None:
            return receive_github_hook(request)

    return JsonResponseMessage(message="Invalid request.")
