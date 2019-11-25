"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib import admin
from askci.apps.main.models import Article, Question, Tag, TemplateRepository


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("name", "namespace", "owner", "created", "modified", "summary")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "article", "created", "modified")


class TagAdmin(admin.ModelAdmin):
    list_display = ("tag",)


class TemplateRepositoryAdmin(admin.ModelAdmin):
    list_display = ("repo",)


admin.site.register(TemplateRepository, TemplateRepositoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
