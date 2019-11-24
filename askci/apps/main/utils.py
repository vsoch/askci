"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management import call_command
import django_rq
import hashlib
import json
import shutil
import os


def backup_db():
    """backup_db is a task intended to be run by django_rq
    """
    if not os.path.exists("/code/backup"):
        os.mkdir("/code/backup")

    tables = ["users", "main"]

    # Save each table individually
    for table in tables:
        output_file = "/code/backup/%s.json" % table

        # Save each one day back (e.g., main1.json)
        if os.path.exists(output_file):
            shutil.move(output_file, output_file.replace(".json", "1.json"))

        with open(output_file, "w") as output:
            print("Dumping tables for module %s" % table)
            call_command("dumpdata", table, format="json", indent=3, stdout=output)

    # All models in one file, for loading with loaddata
    with open("/code/backup/models.json", "w") as output:
        print("Dumping tables for all modules")
        call_command("dumpdata", *tables, format="json", indent=3, stdout=output)

    # Everything
    with open("/code/backup/db.json", "w") as output:
        print("Dumping tables for entire database")
        call_command("dumpdata", format="json", indent=3, stdout=output)


def generate_sha256(content):
    """Generate a sha256 hex digest for a string or dictionary. If it's a 
       dictionary, we dump as a string (with sorted keys) and encode for utf-8.
       The intended use is for a Schema Hash

       Parameters
       ==========
       content: a string or dict to be hashed.
    """
    if isinstance(content, dict):
        content = json.dumps(content, sort_keys=True).encode("utf-8")
    return "sha256:%s" % hashlib.sha256().hexdigest()


def save_json(input_dict, output_file):
    """save dictionary to file as json. Returns the output file written.

       Parameters
       ==========
       content: the dictionary to save
       output_file: the output_file to save to
    """
    with open(output_file, "w") as filey:
        filey.writelines(json.dumps(input_dict, indent=4))
    return output_file


def load_json(input_file):
    """load json from a filename.

       Parameters
       ==========
       input_file: the input file to load
    """
    with open(input_file, "r") as filey:
        content = json.loads(filey.read())
    return content
