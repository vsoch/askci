"""

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_user_agents",
    "askci.apps.api",
    "askci.apps.base",
    "askci.apps.main",
    "askci.apps.users",
]

THIRD_PARTY_APPS = [
    "social_django",
    "crispy_forms",
    "django_rq",
    "django_gravatar",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_swagger",
]


INSTALLED_APPS += THIRD_PARTY_APPS
