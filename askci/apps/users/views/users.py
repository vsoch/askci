"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from askci.apps.users.models import User
from askci.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    NODE_NAME,
)

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.db.models import Q, Sum
from ratelimit.decorators import ratelimit


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_profile(request, username=None):
    """view a user's profile
    """
    message = "You must select a user or be logged in to view a profile."
    if not username:
        if not request.user:
            messages.info(request, message)
            return redirect("collections")
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    context = {"profile": user}
    return render(request, "users/profile.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def delete_account(request):
    """delete a user's account"""
    if not request.user or request.user.is_anonymous:
        messages.info(request, "This action is not prohibited.")
        return redirect("index")

    # Log the user out
    logout(request)
    request.user.is_active = False
    messages.info(request, "Thank you for using %s!" % NODE_NAME)
    return redirect("index")
