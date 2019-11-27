"""

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from importlib import import_module
from django.urls import path
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap, index
from askci.apps.api import urls as api_urls
from askci.apps.base import urls as base_urls
from askci.apps.main import urls as main_urls
from askci.apps.users import urls as user_urls
from askci.settings import NODE_NAME
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

# Customize admin title, headers
admin.site.site_header = "%s administration" % NODE_NAME
admin.site.site_title = "%s Admin" % NODE_NAME
admin.site.index_title = "%s administration" % NODE_NAME

# Documentation URL
API_TITLE = "%s API" % NODE_NAME
API_DESCRIPTION = "%s Resource API" % NODE_NAME
schema_view = get_schema_view(title=API_TITLE)

# Configure custom error pages
handler404 = "askci.apps.base.views.handler404"
handler500 = "askci.apps.base.views.handler500"

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^", include(base_urls)),
    url(r"^api/", include(api_urls)),
    url(r"^api/schema/$", schema_view, name="api-schema"),
    url(r"^api/docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    url(r"^", include(main_urls)),
    url(r"^", include(user_urls)),
    path("editor/", include("django_summernote.urls")),
    url(r"^django-rq/", include("django_rq.urls")),
]

# Load URLs for any enabled plugins
for plugin in settings.PLUGINS_ENABLED:
    urls_module = "askci.plugins." + plugin + ".urls"
    plugin_urls = import_module(urls_module)
    url_regex = "^" + plugin + "/"
    urlpatterns.append(url(url_regex, include(plugin_urls)))
