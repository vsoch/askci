"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand
from askci.apps.main.utils import init_template_repos


class Command(BaseCommand):
    """Add the default template repository to AskCI. An admin can add
       additional repositories via the admin interface.
    """

    help = "Initialize template repositories"

    def handle(self, *args, **options):
        init_template_repos()
