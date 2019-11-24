"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework.authtoken.models import Token


def get_user(uid):
    """ get a user based on id

       Parameters
       ==========
       uid: the id of the user
    """
    from askci.apps.users.models import User

    keyargs = {"id": uid}
    try:
        user = User.objects.get(**keyargs)
    except User.DoesNotExist:
        user = None
    else:
        return user


def get_usertoken(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    return token.key
