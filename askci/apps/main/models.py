"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

import markdown
import uuid
import re
import time


class TemplateRepository(models.Model):
    """a template repository serves to provide a starter
       template for creating a documentation file to update the server. 
       Note that it isn't actually a GitHub template - we fork it to ensure
       that the child repository can be updated from the upstream. The
       repository should minimally have a README.md and a testing setup
       to validate tags. See https://github.com/hpsee/askci-template-term.
       Files should be a string of files necessary for the template to
       render, that are added with git add ${FILES}, and are split based on
       spaces to update the article.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repo = models.CharField(max_length=250, blank=False, null=False, unique=True)
    files = models.TextField(blank=False, null=False, default="README.md")

    def __str__(self):
        return "<TemplateRepository:%s>" % self.repo

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        """Return just the repository name <reponame>
        """
        return "/".join(self.repo.split("/")[-1:]).replace(".git", "")

    @property
    def full_name(self):
        """Return the repository full name <username>/<reponame>
        """
        return "/".join(self.repo.split("/")[-2:]).replace(".git", "")

    def get_label(self):
        return "templaterepository"

    class Meta:
        app_label = "main"


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
        return reverse("tag_details", args=[self.tag])

    def get_label(self):
        return "tag"

    class Meta:
        app_label = "main"


class Question(models.Model):
    """One or more questions are associated with a post. A question should
       only be answered by one post - if there is more detail needed, a link
       to a different article can be added. Questions are parsed from
       text in the repository files, and must be provided in all lowercase
       with dashes. See askci.apps.main.tasks.update_article for parsing.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    text = models.TextField(blank=False, null=False)
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return "<Question:%s>" % self.text

    def __repr__(self):
        return self.__str__()

    @property
    def pretty(self, *args, **kwargs):
        """pretty print a question, replacing - with spaces and uppercasing
           each letter of a sentence.
        """
        sentences = self.text.replace("-", " ")

        # Get rid of question prefix
        sentences = re.sub("^question", "", sentences)

        # Pairs of sentences and ending punctuation.
        pairs = [t for t in re.split("(\.|\!|\?)", sentences) if t]
        pairs = [
            " %s" % p.strip().capitalize() if p not in ["!", ".", "?"] else p
            for p in pairs
        ]
        return "%s?" % " ".join(pairs).strip()

    def get_absolute_url(self):
        return "%s#%s" % (
            reverse("article_details", args=[self.article.name]),
            self.text,
        )

    def get_label(self):
        return "question"

    class Meta:
        app_label = "main"
        unique_together = ["article", "text"]


class Example(models.Model):
    """An example corresponds to a block of code to illustrate an idea.
       If a language is provided or detected, we include it. 
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    text = models.TextField(blank=False, null=False)
    code = models.TextField(blank=False, null=False)
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return "<Example:%s>" % self.text

    def __repr__(self):
        return self.__str__()

    def code2html(self):
        """render code to html, usually for a front end view. 
        """
        return markdown.markdown(self.code)

    @property
    def pretty(self):
        """pretty print a question, replacing - with spaces and uppercasing
           each letter of a sentence.
        """
        sentences = self.text.replace("-", " ")

        # Get rid of question prefix
        sentences = re.sub("^example", "", sentences)

        # Pairs of sentences and ending punctuation.
        pairs = [t for t in re.split("(\.|\!|\?)", sentences) if t]
        pairs = [
            " %s" % p.strip().capitalize() if p not in ["!", ".", "?"] else p
            for p in pairs
        ]
        return " ".join(pairs).strip()

    def get_absolute_url(self):
        return "%s#%s" % (
            reverse("article_details", args=[self.article.name]),
            self.text,
        )

    def get_label(self):
        return "example"

    class Meta:
        app_label = "main"
        unique_together = ["article", "text"]


class Article(models.Model):
    """An article is a topic or concept that can be written about. Each
       article is associated with a GitHub repository, meaning that it
       has ownership based on GitHub permissions. By default, we
       store the GitHub metadata (url) with the article, but all articles
       fall under the namespace library/<term>. Spaces and capital
       letters are not allowed.
    """

    secret = models.UUIDField(default=uuid.uuid4)
    archived = models.BooleanField(default=False)
    webhook_issues = models.BooleanField(default=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    namespace = models.CharField(max_length=250, blank=False, default="library")
    name = models.CharField(max_length=250, blank=False, unique=True)
    commit = models.CharField(max_length=250, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    template = models.ForeignKey(
        "TemplateRepository", on_delete=models.SET_NULL, blank=True, null=True
    )

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

    @property
    def html(self):
        if self.text:
            return markdown.markdown(self.text)

    @property
    def pull_requests(self):
        """order pull requests by date their were modified"""
        return self.pullrequest_set.order_by("-modified")

    @property
    def uri(self):
        return "%s/%s" % (self.namespace, self.name)

    def update_tags(self):
        """a function to update article tags.
        """
        from askci.apps.main.github import get_repository_topics

        previous_tags = self.tags.all()
        for tag in get_repository_topics(self.owner, self.repo):
            tag, created = Tag.objects.get_or_create(tag=tag)
            self.tags.add(tag)
        self.save()

        # For any previous tag no longer used, delete
        for tag in previous_tags:
            if tag.article_tags.count() == 0:
                tag.delete()

    def archive(self, reason):
        """At any point when we cannot perform an action, either the repository
           has been archived or otherwise deleted, and we need to send an email
           to the owner after archiving the repository here to let them know.
        """
        from askci.apps.users.email import send_email

        if not self.archived:
            self.archived = True
            self.save()

            # Only send email if respository not archived yet
            if article.owner.email:
                subject = "[AskCI] Term %s Archived" % self.name.capitalize()
                message = """Your term %s has been archived on AskCI because %s
                    If this has been done in error, please respond to
                    this message. <br> Thank you!""" % (
                    self.name,
                    reason,
                )

                send_email(
                    email_to=article.owner.email, message=message, subject=subject
                )

    def lines(self):
        """an iterator for yielding each line (without newlines)
        """
        if self.text:
            for line in self.text.split("\n"):
                yield line

    def save(self, *args, **kwargs):
        """names are enforced as all lowercase to avoid duplication, along
           with removing all special characters except for dashes.
        """
        from askci.apps.main.utils import lowercase_cleaned_name

        if self.pk is None:
            self.tag = lowercase_cleaned_name(self.tag)
        return super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return "<Article:%s>" % self.name

    def __repr__(self):
        return self.__str__()

    def get_absolute_url(self):
        return reverse("article_details", args=[self.name])

    def get_label(self):
        return "article"

    class Meta:
        app_label = "main"


class PullRequest(models.Model):
    """A pull request is an ephemeral object to hold a review request for a term.
       When a user logs in and submits a request, we create the object with status
       "request." When the pull request is opened, the url is updated and the status
       is "open." When the pull request is closed, we delete the object (as we don't
       need it anymore).
    """

    STATUS_OPTIONS = [
        ("pending", "pending"),
        ("closed", "closed"),
        ("reject", "reject"),
        ("open", "open"),
    ]

    number = models.PositiveIntegerField(default=None, blank=True, null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField("date created", auto_now_add=True)
    modified = models.DateTimeField("date modified", auto_now=True)
    url = models.CharField(max_length=500, blank=True, null=True, unique=True)
    status = models.CharField(max_length=32, choices=STATUS_OPTIONS, default="pending")
    article = models.ForeignKey(
        "main.Article", on_delete=models.CASCADE, blank=False, null=False
    )
    owner = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return "<PullRequest:%s>" % self.url

    def __repr__(self):
        return self.__str__()

    def get_label(self):
        return "pullrequest"

    class Meta:
        app_label = "main"
