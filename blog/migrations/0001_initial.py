# Generated by Django 5.1.7 on 2025-04-11 11:05

import ckeditor.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', ckeditor.fields.RichTextField()),
                ('image', models.ImageField(upload_to='blog/posts')),
                ('category', models.CharField(choices=[('announcement', 'اطلاعیه و اخبار'), ('law', 'قانون'), ('educational', 'آموزشی'), ('cases', 'پرونده\u200cهای جذاب')], max_length=50)),
                ('subcategory', models.CharField(blank=True, choices=[('criminal', 'کیفری'), ('civil', 'حقوقی'), ('family', 'خانواده'), ('sabt', 'امور ثبتی'), ('vaghf', 'وقف و موقوفات'), ('other', 'سایر')], max_length=50, null=True)),
                ('slug', models.CharField(max_length=255, unique=True)),
                ('published_date', models.DateField(default=django.utils.timezone.now)),
                ('is_published', models.BooleanField(default=False)),
                ('price', models.CharField(blank=True, max_length=100, null=True)),
                ('summery', models.CharField(blank=True, max_length=150, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply', to='blog.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.post')),
            ],
        ),
    ]
