"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.generic.base import TemplateView
from django.conf.urls import url
import askci.apps.base.views as views

urlpatterns = [
    url(r"^$", views.index_view, name="index"),
    url(r"^about/?$", views.about_view, name="about"),
    url(r"^contact/?$", views.contact_view, name="contact"),
    url(r"^terms/?$", views.terms_view, name="terms"),
    url(r"^privacy-policy/?$", views.privacy_view, name="privacy-policy"),
    url(
        r"^robots\.txt/$",
        TemplateView.as_view(
            template_name="base/robots.txt", content_type="text/plain"
        ),
    ),
]
