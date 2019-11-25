"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import redirect, render

from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from social_core.backends.github import GithubOAuth2

from ratelimit.decorators import ratelimit
from askci.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block


################################################################################
# AUTHENTICATION
################################################################################


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def agree_terms(request):
    """ajax view for the user to agree"""
    if request.method == "POST":
        request.user.agree_terms = True
        request.user.agree_terms_date = timezone.now()
        request.user.save()
        response_data = {"status": request.user.agree_terms}
        return JsonResponse(response_data)

    return JsonResponse(
        {"Unicorn poop cookies...": "I will never understand the allure."}
    )


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def login(request, message=None):
    """login is bootstrapped here to show the user a usage agreement first, in the
       case that he or she has not agreed to the terms.
    """
    if message is not None:
        messages.info(request, message)

    context = None
    if request.user.is_authenticated:
        if not request.user.agree_terms:
            return render(request, "terms/usage_agreement_login.html", context)
    return render(request, "social/login.html", context)


@login_required
def logout(request):
    """log the user out, first trying to remove the user_id in the request session
       skip if it doesn't exist
    """
    try:
        del request.session["user_id"]
    except KeyError:
        pass
    auth_logout(request)

    return redirect("/")


################################################################################
# SOCIAL AUTH
################################################################################


def redirect_if_no_refresh_token(backend, response, social, *args, **kwargs):
    """http://python-social-auth.readthedocs.io/en/latest/use_cases.html#re-prompt-google-oauth2-users-to-refresh-the-refresh-token
    """
    if (
        backend.name == "google-oauth2"
        and social
        and response.get("refresh_token") is None
        and social.extra_data.get("refresh_token") is None
    ):
        return redirect("/login/google-oauth2?approval_prompt=force")


# GitHub Read only (no repos)
class GithubReadOnlyOAuth2(GithubOAuth2):
    name = "github-readonly"


def get_credentials(user, provider):
    """return one or more credentials, or None"""
    credential = None
    if not user.is_anonymous:
        try:
            # Case 1: one credential
            credential = user.social_auth.get(provider=provider)
            return credential

        # Credential doesn't exist
        except user.social_auth.model.DoesNotExist:
            return credential

        except:
            # Case 2: more than one credential for the provider
            credential = user.social_auth.filter(provider=provider)
            if len(credential) > 0:
                return credential.last()


## Ensure equivalent email across accounts


def social_user(backend, uid, user=None, *args, **kwargs):
    """OVERRIDED: It will give the user an error message if the
       account is already associated with a username."""
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)

    if social:
        if user and social.user != user:
            msg = "This {0} account is already in use.".format(provider)
            return login(request=backend.strategy.request, message=msg)
            # raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user

    return {
        "social": social,
        "user": user,
        "is_new": user is None,
        "new_association": social is None,
    }
