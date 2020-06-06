"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from askci.apps.main.models import Article, Question, Example, PullRequest, Tag
from askci.apps.users.models import User
from askci.apps.main.utils import lowercase_cleaned_name, get_stopwords

from bs4 import BeautifulSoup
from itertools import chain

import markdown
import json
import re
import requests


def remove_language(code):
    """if the code starts with a single term on the first line, assume it's
       a language and remove it. We will need to test this to see if it works
       in practice.
    """
    lines = code.split("\n")
    if len(lines) > 1:
        words = lines[0].split(" ")
        if len(words) == 1:
            lines = lines[1:]
            code = "\n".join(lines)
    return code


def create_webhooks_issues(text, message, provider):
    """given a validated webhook, take some text (topics) and parse for
       unique terms or concepts. If found, and the article exists, open
       a corresponding issue

       Parameters
       ==========
       text: should be a raw string of text to parse for topics. Illegal
               characters (other than -) will be removed, and lowercased
       message: a message to post in the issue. Should be prepared with a url
                from the provider
       provider: the provider that sent the webhook, will be added to the title
    """
    from askci.apps.main.github import open_issue

    # Words to always skip
    skip = get_stopwords()

    # Remove  html tags
    cleaned = [re.sub("<.*?>", " ", x) for x in text.split(" ")]

    # Parse text and look for terms
    cleaned = [
        lowercase_cleaned_name(x.strip()) for x in cleaned if lowercase_cleaned_name(x)
    ]

    cleaned = set([x for x in cleaned if x not in skip])
    print(cleaned)

    for term in cleaned:
        try:
            article = Article.objects.get(name=term)
            if article.webhook_issues:
                print("opening issue for %s" % article)
                title = "Updated content from %s for term %s" % (provider, article.name)
                res = open_issue(article.owner, article, title, summary=message)
                print("Response for issue %s" % res)
        except Article.DoesNotExist:
            pass


def repository_change(article_uuid, action, repo):
    """triggered when a user renames a repository. When a rename happens,
       previous webhooks / other tests are maintained, but we need to 
       update the metadata here. See:

       https://developer.github.com/v3/activity/events/types/#repositoryevent
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        return

    article.repo = json.loads(repo)

    # Not archived
    if action in ["created", "unarchived", "publicized"]:
        article.archived = False
        article.save()

    # Reason for archive
    elif action in ["deleted", "archived", "privatized"]:
        article.archive("the repository was %s. " % action)

    # If repository is renamed, must begin with "askci-term" or is archived
    elif action in ["renamed"]:
        if not repo["name"].startswith("askci-term-"):
            article.archive("the repository name needs to start with askci-term-. ")

    article.update_tags()


def update_pullrequest(article_uuid, number, url, user, action, merged_at):
    """Given a PR action, url, and an article uuid, update a Pull Request object for it.
       https://developer.github.com/v3/activity/events/types/#pullrequestevent
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        return

    # Get the associated user
    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        return

    # Get associated pull request, create object only if newly opened
    try:
        pull_request = article.pullrequest_set.get(number=number)
    except PullRequest.DoesNotExist:
        if action == "opened":
            pull_request, created = PullRequest.objects.get_or_create(
                article=article, owner=user, number=number, url=url
            )
        else:
            return

    if action in ["opened", "edited", "ready_for_review", "reopened"]:
        pull_request.status = "open"

    elif action in ["closed"]:

        # The repository wasn't merged
        if not merged_at:
            pull_request.status = "reject"
        else:
            pull_request.status = "closed"

    elif action in [
        "assigned",
        "unassigned",
        "review_requested",
        "review_request_removed",
        "labeled",
        "unlabeled",
    ]:
        print("No action taken for %s" % action)

    pull_request.save()


def update_tag(article_uuid, tag, event):
    """update tag will obtain an article, and add or delete the tag association.
       If the tag doesn't exist for other repos, it is deleted from the server.
       This function is currently not used because there doesn't appear to
       be an endpoint to receive notification on tags changes.
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        return

    try:
        tag = Tag.objects.get(tag=tag)
    except Tag.DoesNotExist:
        return

    # Create a new tag, add to repository if doesn't exist
    if event == "create":
        if tag not in article.tags.all():
            article.tags.add(tag)
            article.save()

    # Delete a tag (and permanently from AskCI) if removed
    elif event == "delete":
        if tag in article.tags.all():
            article.tags.remove(tag)
            article.save()
        if tag.article_tags.count() == 0:
            tag.delete()


def update_article(article_uuid):
    """take a request and an associated article, and grab
       the latest README to update content on the site.
       If the content isn't valid, we don't update. The same test
       is done when the user submits **and** with a GitHub workflow,
       so this case is unlikely (but maybe possible).
    """
    try:
        article = Article.objects.get(uuid=article_uuid)
    except Article.DoesNotExist:
        return

    # For now just use the first file, we know to feed that into content
    # If there are other templates with multiple files, they could
    # be looped over here.
    filename = "README.md"
    if article.template.files:
        filename = article.template.files.split(" ")[0]

    # Formulate the url for raw github content
    url = "https://raw.githubusercontent.com/%s/master/%s" % (
        article.repo["full_name"],
        filename,
    )
    content = requests.get(url).text

    # Test markdown first - don't continue if not valid
    valid, message = test_markdown(content)
    if not valid:
        print("Markdown is invalid: %s" % message)
        return

    # Parse the content for questions
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, "lxml")

    # Supported span prefixes
    prefixes = ["question", "example"]
    prefix_regex = "^(%s)" % "|".join(prefixes)

    # Keep link to previous questions (and empty article)
    previous = list(chain(article.question_set.all(), article.example_set.all()))
    article.question_set.clear()
    article.example_set.clear()
    [p.delete() for p in previous]

    # Add correctly formatted spans (this is same as testing in repository)
    for span in soup.find_all("span"):

        # The span is required to have an id
        identifier = span.attrs.get("id")
        if not identifier:
            continue

        # The span id must start with a valid prefix
        if not re.search(prefix_regex, identifier):
            continue

        # The span id must have all lowercase, no special characters or spaces
        if re.search("[^A-Za-z0-9-]+", identifier):
            continue

        # If the question is valid, get or create
        if "question" in identifier:
            question, created = Question.objects.get_or_create(text=identifier)
            article.question_set.add(question)

        # Examples are added only if found following code section
        else:
            code = span.find_next("code")
            if code:
                cleaned = remove_language(code.text)
                code.string.replace_with(cleaned)
                example, created = Example.objects.get_or_create(
                    text=identifier, code=cleaned
                )
                article.example_set.add(example)

    article.text = content
    article.save()
    article.update_tags()


def test_markdown(text):
    """Given markdown text from a post, ensure that the spans are correct.
       If not, return to user with an error message.
    """
    html = markdown.markdown(text)

    # Convert to beautiful soup
    soup = BeautifulSoup(html, "lxml")

    # Supported span prefixes
    prefixes = ["question", "example"]
    prefix_regex = "^(%s)" % "|".join(prefixes)

    # Ensure that each span is all lowercase, with no extra characters
    for span in soup.find_all("span"):

        # The span is required to have an id
        identifier = span.attrs.get("id")
        if not identifier:
            return False, "Span %s is missing an identifier." % span

        # The span id must start with a valid prefix
        if not re.search(prefix_regex, identifier):
            return False, "Span %s does not start with %s" % (identifier, prefix_regex)

        # The span id must have all lowercase, no special characters or spaces
        if re.search("[^A-Za-z0-9-]+", identifier):
            return (
                False,
                "Span %s is invalid: can only have lowercase and '-'" % identifier,
            )

    return True, "Valid"
