from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'subcategory', 'is_published', 'image', 'summery',
                  'published_date', 'author', 'price', 'view', 'time_to_read']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
