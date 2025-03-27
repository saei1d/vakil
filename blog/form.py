from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'subcategory', 'is_published', 'image', 'slug', 'summery',
                  'published_date', 'author','price']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
