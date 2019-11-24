"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

import uuid
import re
import time


class Tag(models.Model):
    """tags are ways to organize the different categories they are associated with. 
       As an example, we may tag a plasmid part as conferring ampicillin 
       resistance, so it would include the tag resistance:ampicillin. 
       That same part could also be tagged as an essential_gene.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=250, blank=False, null=False, unique=True)

    def __str__(self):
        return "<Tag:%s>" % self.tag

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        """tags are enforced as all lowercase to avoid duplication, along
           with removing all special characters except for dashes and :.
           Dashes and : are allowed. 
        """
        if self.pk is None:
            self.tag = self.tag.replace(" ", "-")  # replace space with -
            self.tag = re.sub("[^A-Za-z0-9:-]+", "", self.tag).lower()
        return super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tag_details", args=[self.uuid])

    def get_label(self):
        return "tag"

    class Meta:
        app_label = "main"


class Question(models.Model):
    """One or more questions are associated with a post. A question should
       only be answered by one post - if there is more detail needed, a link
       to a different article can be added. Questions are parsed from
       text in the repository files, and must be provided in all lowercase
       with dashes.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    text = models.TextField(blank=False, null=False, unique=True)
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return "<Question:%s>" % self.tag

    def __repr__(self):
        return self.__str__()

    @property
    def pretty(self, *args, **kwargs):
        """pretty print a question, replacing - with spaces and uppercasing
           each letter of a sentence.
        """
        sentences = self.text.replace("-", "")

        # Pairs of sentences and ending punctuation.
        pairs = [t for t in re.split("(\.|\!|\?)", text) if t]
        pairs = [
            " %s" % p.strip().capitalize() if p not in ["!", ".", "?"] else p
            for p in pairs
        ]
        return "".join(pairs).strip()

    def get_absolute_url(self):
        return reverse("tag_details", args=[self.uuid])

    def get_label(self):
        return "question"

    class Meta:
        app_label = "main"


class Article(models.Model):
    """An article is a topic or concept that can be written about. Each
       article is associated with a GitHub repository, meaning that it
       has ownership based on GitHub permissions. By default, we
       store the GitHub metadata (url) with the article, but all articles
       fall under the namespace library/<term>. Spaces and capital
       letters are not allowed.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    namespace = models.CharField(
        max_length=250, blank=False, unique=True, default="library"
    )
    name = models.CharField(max_length=250, blank=False, unique=True)
    commit = models.CharField(max_length=50, blank=False, null=False, unique=True)
    summary = models.TextField(blank=True, null=True)

    # Don't delete article if owner deletes account, set null
    owner = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, blank=True, null=True
    )

    # Repository metadata
    repo = JSONField(default=dict)
    webhook = JSONField(default=dict)

    # Tags are additional terms to describe an article
    tags = models.ManyToManyField(
        "main.Tag",
        blank=True,
        default=None,
        related_name="article_tags",
        related_query_name="article_tags",
    )

    def save(self, *args, **kwargs):
        """names are enforced as all lowercase to avoid duplication, along
           with removing all special characters except for dashes.
        """
        if self.pk is None:
            self.tag = self.tag.replace(" ", "-")  # replace space with -
            self.tag = re.sub("[^A-Za-z0-9-]+", "", self.tag).lower()
        return super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return "<Article:%s>" % self.name

    def __repr__(self):
        return self.__str__()

    def get_absolute_url(self):
        return reverse("article_details", args=[self.uuid])

    def get_label(self):
        return "article"

    class Meta:
        app_label = "main"
