"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.urls import reverse

from askci.apps.main.models import Article, Question, Tag
from .permissions import IsStaffOrSuperUser, AllowAnyGet
from rest_framework import generics, mixins, serializers, viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound

from rest_framework.response import Response
from rest_framework.views import APIView


class ArticleSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), required=False, many=True
    )
    label = serializers.SerializerMethodField("get_label")

    def get_label(self, instance):
        return instance.get_label()

    class Meta:
        model = Article
        fields = (
            "uuid",
            "namespace",
            "name",
            "repo",
            "summary",
            "commit",
            "text",
            "tags",
            "label",
            "created",
            "modified",
        )


class ArticleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article.objects.all()

    serializer_class = ArticleSerializer


class QuestionSerializer(serializers.ModelSerializer):

    label = serializers.SerializerMethodField("get_label")
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), required=False
    )

    def get_label(self, instance):
        return instance.get_label()

    class Meta:
        model = Question
        fields = ("uuid", "text", "article", "label", "created", "modified")


class QuestionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Question.objects.all()

    serializer_class = QuestionSerializer


# Tags


class TagSerializer(serializers.ModelSerializer):

    label = serializers.SerializerMethodField("get_label")

    def get_label(self, instance):
        return instance.get_label()

    class Meta:
        model = Tag
        fields = ("uuid", "tag", "label")


class TagViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Tag.objects.all()

    serializer_class = TagSerializer
