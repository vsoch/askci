"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db import models
import uuid as uuidf


class Webhook(models.Model):
    """an ImageFile is a Singularity container pushed directly.
    """

    WEBHOOK_SERVER_OPTIONS = [("discourse", "discourse")]

    uuid = models.UUIDField(primary_key=True, default=uuidf.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    name = models.TextField(null=False, blank=False, unique=True)
    secret = models.UUIDField(default=uuidf.uuid4)
    app_from = models.CharField(
        choices=WEBHOOK_SERVER_OPTIONS,
        max_length=50,
        blank=False,
        null=False,
        default="discourse",
    )

    def get_label(self):
        return "webhook"

    class Meta:
        app_label = "api"
