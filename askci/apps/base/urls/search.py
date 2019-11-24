"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import askci.apps.base.views as views

urlpatterns = [
    url(r"^search/?$", views.search_view, name="search"),
    url(r"^searching/?$", views.run_search, name="running_search"),
    url(r"^search/(?P<query>.+?)/?$", views.search_view, name="search_query"),
]
