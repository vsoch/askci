"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from ratelimit.decorators import ratelimit
from askci.apps.main.models import Article, Question, Tag
from askci.apps.main.utils import get_paginated
from askci.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    HELP_CONTACT_EMAIL,
)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def about_view(request):
    return render(request, "main/about.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def terms_view(request):
    return render(request, "terms/usage_agreement_fullwidth.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def privacy_view(request):
    return render(request, "terms/privacy_agreement.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index_view(request):
    """Show new questions with their associated articles. We use
       a paginator here so the user can scroll indefinitely.
    """
    question_set = Question.objects.order_by("-modified")
    questions = get_paginated(request, question_set)
    context = {"questions": questions}
    return render(request, "main/index.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def contact_view(request):
    if request.method == "POST":
        from askci.apps.users.email import send_email

        name = request.POST.get("name")
        email = request.POST.get("_reply_to")
        message = request.POST.get("message")
        message = message.replace("\n", "<br>")
        send_email(
            email_to=HELP_CONTACT_EMAIL,
            from_email=email,
            message=message,
            subject="[AskCI] Message",
        )
        messages.info(request, "Thank you for your message!")
    return render(request, "main/contact.html")
