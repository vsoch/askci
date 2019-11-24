"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url, include
import askci.apps.users.views as views
from social_django import urls as social_urls

urlpatterns = [
    # Twitter, and social auth
    url(r"^login/$", views.login, name="login"),
    url(r"^accounts/login/$", views.login),
    url(r"^logout/$", views.logout, name="logout"),
    url("", include(social_urls, namespace="social")),
    url(r"^terms/agree", views.agree_terms, name="agree_terms"),
    url(r"^u/delete$", views.delete_account, name="delete_account"),  # delete account
    url(r"^u/profile", views.view_profile, name="profile"),
    # We don't currently have a reason for one user to see another user's account
    # url(r'^(?P<username>[A-Za-z0-9@/./+/-/_]+)/$',views.view_profile,name="profile"),
]
