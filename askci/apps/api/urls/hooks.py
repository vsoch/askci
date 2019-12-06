"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import askci.apps.api.views as views

urlpatterns = [
    # Receives push, deploy, pull_request
    url(r"^hook/push/?$", views.receive_hook, name="receive_hook"),
    url(
        r"^hook/receive_pr_request/?$",
        views.receive_pr_request,
        name="receive_pr_request",
    ),
]
