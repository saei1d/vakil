from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.timezone import now
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import RegexValidator
from users.models import Client


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=255, unique=True)
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    homepage = models.BooleanField(default=False)
    published_date = models.DateField(default=now)
    is_published = models.BooleanField(default=False)
    price = models.CharField(max_length=100, null=True, blank=True)
    summery = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [('can_view_post', 'Can view post')]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(Client, on_delete=models.CASCADE)  # یا مدل User اگر نیاز به احراز هویت باشد
    content = models.TextField()
    created_date = models.DateTimeField(default=now)
    is_approved = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"
