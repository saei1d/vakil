from django.contrib import admin

from blog.models import *


# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'status', 'content', 'published_date')


admin.site.register(Post)
