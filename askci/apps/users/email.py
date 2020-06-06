"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from askci.settings import SENDGRID_API_KEY, HELP_CONTACT_EMAIL

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
)

import base64
import os


def send_email(
    email_to,
    message,
    subject,
    from_email=None,
    attachment=None,
    filetype="application/pdf",
    filename=None,
):
    """given an email, a message, and an attachment, and a SendGrid API key is defined in
       settings, send an attachment to the user

       Parameters
       ==========
       email_to: the email to send the message to
       from_email: if not set, use HELP_CONTACT_EMAIL
       message: the html content for the body
       subject: the email subject
       attachment: the attachment file on the server
    """
    if not SENDGRID_API_KEY or not HELP_CONTACT_EMAIL:
        print("SENDGRID_API_KEY or HELP_CONTACT_EMAIL are missing.")
        return

    if from_email is None:
        from_email = HELP_CONTACT_EMAIL

    message = Mail(
        from_email=from_email, to_emails=email_to, subject=subject, html_content=message
    )

    # If the user has provided an attachment, add it
    if attachment:
        message.attachment = generate_attachment(
            filepath=attachment, filetype=filetype, filename=filename
        )

    try:
        client = SendGridAPIClient(SENDGRID_API_KEY)
        response = client.send(message)
        print(response.status_code)
        print(response.headers)
    except Exception as e:
        print(e.message)


def generate_attachment(filepath, filetype="application/pdf", filename=None):
    """given a filepath, generate an attachment object for SendGrid by reading
       it in and encoding in base64.
 
       Parameters
       ==========
       filepath: the file path to attach on the server.
       filetype: MIME content type (defaults to application/pdf)
       filename: a filename for the attachment (defaults to basename provided)
    """
    if not os.path.exists(filepath):
        return

    # Read in the attachment, base64 encode it
    with open(filepath, "rb") as filey:
        data = filey.read()

    # The filename can be provided, or the basename of actual file
    if not filename:
        filename = os.path.basename(filepath)

    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType(filetype)
    attachment.file_name = FileName(filename)
    attachment.disposition = Disposition("attachment")
    return attachment
