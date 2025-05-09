from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'subcategory', 'is_published', 'image', 'summery',
                  'published_date', 'author','price','view','time_to_read']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان مقاله'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'summery': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'published_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'view': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_to_read': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'عنوان مقاله',
            'content': 'محتوا',
            'category': 'دسته‌بندی',
            'subcategory': 'زیردسته‌بندی',
            'is_published': 'منتشر شده',
            'image': 'تصویر شاخص',
            'summery': 'چکیده',
            'published_date': 'تاریخ انتشار',
            'author': 'نویسنده',
            'price': 'قیمت',
            'view': 'تعداد بازدید',
            'time_to_read': 'زمان مطالعه (دقیقه)',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
