"""

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand, CommandError

from askci.apps.users.models import User
from askci.settings import NODE_NAME

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """remove staff will remove staff privileges for a user
    """

    def add_arguments(self, parser):
        parser.add_argument(dest="username", nargs=1, type=str)

    help = "Removes staff priviledges for %s." % NODE_NAME

    def handle(self, *args, **options):
        if options["username"] is None:
            raise CommandError("Please provide a username with --username")

        logger.debug("Username: %s" % options["username"])

        try:
            user = User.objects.get(username=options["username"][0])
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        if user.is_staff is False:
            raise CommandError("This user is already not staff.")
        else:
            user.is_staff = False
            user.save()
            print("%s is not longer staff." % (user.username))
