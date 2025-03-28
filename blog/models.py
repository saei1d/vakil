from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator
from users.models import Client


class Category(models.TextChoices):
    ANNOUNCEMENT = "announcement", "اطلاعیه و اخبار"
    LAW = "law", "قانون"
    EDUCATIONAL = "educational", "آموزشی"
    CASES = "cases", "پرونده‌های جذاب"


class SubCategory(models.TextChoices):
    CRIMINAL = "criminal", "کیفری"
    CIVIL = "civil", "حقوقی"
    FAMILY = "family", "خانواده"
    sabt = "sabt", "امور ثبتی"
    vaghf = "vaghf", "وقف و موقوفات"
    OTHER = "other", "سایر"


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()
    image = models.ImageField(upload_to="blog/posts")
    category = models.CharField(max_length=50, choices=Category.choices)
    subcategory = models.CharField(max_length=50, choices=SubCategory.choices, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True)
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    published_date = models.DateField(default=now)
    is_published = models.BooleanField(default=False)
    price = models.CharField(max_length=100, null=True, blank=True)
    summery = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True, related_name="reply")

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
