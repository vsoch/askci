"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib import admin
from askci.apps.api.models import Webhook


class WebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "secret", "app_from", "created", "modified")


admin.site.register(Webhook, WebhookAdmin)
