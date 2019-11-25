"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os

# AUTHENTICATION
# GitHub is default with or without private

# Which social auths do you want to use?
ENABLE_GLOBUS_AUTH = False
ENABLE_GOOGLE_AUTH = False
ENABLE_ORCID_AUTH = False
ENABLE_ORCID_AUTH_SANDBOX = False
ENABLE_TWITTER_AUTH = False
ENABLE_GITLAB_AUTH = False
ENABLE_BITBUCKET_AUTH = False

# NOTE you will need to set authentication methods up.
# Configuration goes into secrets.py
# See https://vsoch.github.io/freegenes/docs/development/setup#settings

# See below for additional authentication module, e.g. LDAP that are
# available, and configured, as plugins.

GOOGLE_ANALYTICS_ID = None

# SendGrid

SENDGRID_API_KEY = None

# DOMAIN NAMES
## IMPORTANT: if/when you switch to https, you need to change "DOMAIN_NAME"
# to have https, otherwise some functionality will not work

DOMAIN_NAME = "http://127.0.0.1"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = DOMAIN_NAME

ADMINS = (("vsochat", "vsochat@gmail.com"),)
MANAGERS = ADMINS

# AskCI Parameters

HELP_CONTACT_EMAIL = os.environ.get("HELP_CONTACT_EMAIL", "vsochat@stanford.edu").strip(
    '"'
)
HELP_INSTITUTION_SITE = os.environ.get(
    "HELP_INSTITUTION_SITE", "https://srcc.stanford.edu"
).strip('"')
NODE_INSTITUTION = os.environ.get("NODE_INSTITUTION", "Stanford University").strip('"')
NODE_URI = os.environ.get("NODE_URI", "askci-server").strip('"')
NODE_NAME = os.environ.get("NODE_NAME", "AskCI").strip('"')
NODE_TWITTER = os.environ.get("NODE_TWITTER", "askcyberinfra").strip('"')

# Repository Templates
REPO_TEMPLATES = ["https://github.com/hpsee/askci-template-term"]

# Permissions and Views

# DATABASE

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "HOST": "db",
        "PORT": "5432",
    }
}

# Rate Limits

VIEW_RATE_LIMIT = (
    "50/1d"
)  # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
VIEW_RATE_LIMIT_BLOCK = (
    True
)  # Given that someone goes over, are they blocked for the period?

# Plugins
# Add the name of a plugin under askci.plugins here to enable it
# Available Plugins:

# - ldap_auth: Allows sregistry to authenitcate against an LDAP directory
# - pam_auth: Allow users from (docker) host to log in
# - saml_auth: authentication with SAML

PLUGINS_ENABLED = [
    #    'ldap_auth',
    #    'pam_auth',
    #    'saml_auth'
]
