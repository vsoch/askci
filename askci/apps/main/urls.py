"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import askci.apps.main.views as views

urlpatterns = [
    url(r"^articles/?$", views.all_articles, name="all_articles"),
    url(r"^examples/?$", views.all_examples, name="all_examples"),
    url(r"^export/?$", views.export, name="export"),
    url(r"^update/templates/?$", views.update_templates, name="update_templates"),
    url(r"^e/article/(?P<name>.+)/?$", views.article_details, name="article_details"),
    url(r"^article/(?P<name>.+)/delete/?$", views.delete_article, name="delete_article"),
    url(r"^tag/(?P<tag>.+)/?$", views.tag_details, name="tag_details"),
    url(r"^article/new/?$", views.new_article, name="new_article"),
    url(r"^article/import/?$", views.import_article, name="import_article"),
    url(r"^question/new/?$", views.new_question, name="new_question"),
    url(r"^question/new/(?P<name>.+)/?$", views.new_question, name="new_question"),
    url(r"^download/repos/csv/?$", views.download_repos_csv, name="download_repos_csv"),
    url(
        r"^download/article/txt/(?P<name>.+)/?$",
        views.download_article_text,
        name="download_article_text",
    ),
    url(
        r"^download/articles/json/?$",
        views.download_articles_json,
        name="download_articles_json",
    ),
    url(
        r"^download/articles/json/(?P<name>.+)/?$",
        views.download_articles_json,
        name="download_articles_json",
    ),
]
