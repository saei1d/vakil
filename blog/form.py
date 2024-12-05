from django import forms
from .models import Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ['title', 'content', 'published_date', 'author', 'homepage', 'is_published','slug','price','summery']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }
