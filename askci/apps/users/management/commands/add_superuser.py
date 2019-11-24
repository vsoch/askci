"""

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand, CommandError

from askci.apps.users.models import User

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """add a superuser to the server
    """

    def add_arguments(self, parser):
        parser.add_argument(dest="username", nargs=1, type=str)

    help = "Generates a superuser"

    def handle(self, *args, **options):
        if options["username"] is None:
            raise CommandError("Please provide a username.")

        logger.debug("Username: %s" % options["username"][0])

        try:
            user = User.objects.get(username=options["username"][0])
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        if user.is_superuser is True:
            raise CommandError("This user is already a superuser.")
        else:
            user = User.objects.add_superuser(user)
            print("%s is now a superuser." % (user.username))
