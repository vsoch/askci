"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from askci.apps.main.github.utils import (
    JsonResponseMessage,
    validate_payload,
    load_body,
)
from askci.apps.main.github import receive_github_hook
from askci.apps.api.models import Webhook
from askci.apps.main.tasks import create_webhooks_issues

import django_rq
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
def receive_webhook(request, provider="discourse"):
    """receive_webhook will parse a validated webhook from an external server.
       for GitHub webhooks assciated with core functionality of the server,
       see receive_hook above.
    """
    if request.method == "POST":

        providers = [x[0] for x in Webhook.WEBHOOK_SERVER_OPTIONS]
        if provider not in providers:
            return JsonResponseMessage(message="Invalid request.")

        # Global checks first
        if request.META["CONTENT_TYPE"] != "application/json":
            return JsonResponseMessage(message="Invalid request.")

        # Currently only support for discourse
        if provider == "discourse":
            if not re.search("Discourse", request.META["HTTP_USER_AGENT"]):
                return JsonResponseMessage(message="Invalid request.")

            headers = [
                "HTTP_X_DISCOURSE_EVENT_ID",
                "HTTP_X_DISCOURSE_EVENT",
                "HTTP_X_DISCOURSE_EVENT_SIGNATURE",
            ]
            for header in headers:
                if header not in request.META:
                    return JsonResponseMessage(message="Invalid request.")

            # Get the webhook based on the discourse instance
            name = request.META.get("HTTP_X_DISCOURSE_INSTANCE", "invalid")
            try:
                webhook = Webhook.objects.get(name=name)
            except Webhook.DoesNotExist:
                return JsonResponseMessage(message="Invalid request.")

            # Get the signature (format sha256=)
            signature = request.META["HTTP_X_DISCOURSE_EVENT_SIGNATURE"]

            # Load the body
            body = load_body(request)

            if not validate_payload(
                secret=str(webhook.secret),
                payload=request.body,
                request_signature=signature,
                algorithm="sha256",
            ):
                return JsonResponseMessage(message="Invalid request.")

            # Ensure correct content in body
            if "post" not in body:
                return JsonResponseMessage(message="Invalid request.")

            required = [
                "topic_title",
                "topic_slug",
                "topic_id",
                "post_number",
                "cooked",
            ]
            for required in required:
                if required not in body["post"]:
                    return JsonResponseMessage(message="Invalid request.")

            # Formulate the discourse url for the topic
            # https://ask.cyberinfrastructure.org/t/what-are-the-names-of-containers/1197/2
            url = "%s/t/%s/%s/%s" % (
                webhook.name,
                body["post"]["topic_slug"],
                body["post"]["topic_id"],
                body["post"]["post_number"],
            )

            message = "%s\n\n[See Full Post](%s)" % (body["post"]["cooked"], url)

            # Parse some text to search for articles, send issue with links
            django_rq.enqueue(
                create_webhooks_issues,
                text="%s %s" % (body["post"]["cooked"], body["post"]["topic_title"]),
                message=message,
                provider=provider,
            )
            return JsonResponseMessage(message="received.", status=200)

        return JsonResponseMessage(message="Invalid Request")
