"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import askci.apps.main.views as views

urlpatterns = [
    # Details (e corresponds for entity)
    url(r"^e/article/(?P<name>.+)/?$", views.article_details, name="article_details"),
    url(r"^e/tag/(?P<tag>.+)/?$", views.tag_details, name="tag_details"),
    # Articles
    url(r"a/new/?$", views.new_article, name="new_article"),
    # Catalog views
    url(r"c/?$", views.catalog_view, name="catalog_view"),
    url(r"c/articles/?$", views.articles_catalog_view, name="articles_catalog_view"),
    url(r"c/questions/?$", views.questions_catalog_view, name="questions_catalog_view"),
    url(r"c/tags/?$", views.tags_catalog_view, name="tags_catalog_view"),
    # Download
    url(
        r"^download/repos/csv/(?P<uuid>.+)/?$",
        views.download_repos_csv,
        name="download_repos_csv",
    ),
    url(
        r"^download/articles/json/(?P<uuid>.+)/?$",
        views.download_articles_json,
        name="download_articles_json",
    ),
]
