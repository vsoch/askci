"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url, include
import rest_framework.authtoken.views as authviews
from rest_framework import routers
from askci.apps.api.urls.serializers import ArticleViewSet, QuestionViewSet, TagViewSet


router = routers.DefaultRouter()
router.register(r"^articles", ArticleViewSet, base_name="article")
router.register(r"^questions", QuestionViewSet, base_name="question")
router.register(r"^tags", TagViewSet, base_name="tag")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^api-token-auth/", authviews.obtain_auth_token),
]
