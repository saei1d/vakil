from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views import View
from .models import Post, Comment
from .form import *


# Create your views here.


def aboutus(request):
    return render(request, 'blog/about.html')


def faq(request):
    return render(request, 'blog/faq.html')


def blog(request):
    blog = Post.objects.all()
    for post in blog:
        print(post.id)
        print(post.published_date)
    return render(request, 'blog/blog.html', {'blog': blog})


def blogpage(request, slug):
    blog = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/blog-page.html', {'blog': blog})


def contact(request):
    return render(request, 'blog/contact.html')


def post_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_date')
    for post in posts:
        print(post.id)

    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    comments = post.comments.filter(is_approved=True, parent=None)
    if request.method == "POST":
        user = request.POST.get("user")
        content = request.POST.get("content")
        if user and content:
            Comment.objects.create(post=post, user=user, content=content)
            return redirect("post_detail", slug=slug)
    return render(
        request, "blog/post_detail.html", {"post": post, "comments": comments}
    )


@login_required
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff:  # فقط ادمین
        comment.is_approved = True
        comment.save()
    return redirect("post_detail", slug=comment.post.slug)


@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff:  # فقط ادمین
        if request.method == "POST":
            content = request.POST.get("content")
            if content:
                Comment.objects.create(
                    post=parent_comment.post,
                    user=request.user.username,  # نام ادمین به عنوان نویسنده
                    content=content,
                    parent=parent_comment,
                    is_approved=True,
                )
                return redirect("post_detail", slug=parent_comment.post.slug)
        return render(request, "blog/reply_comment.html", {"comment": parent_comment})
    return redirect("post_detail", slug=parent_comment.post.slug)


class PostCreate(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'blog/post_form.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:blog')
        return render(request, 'blog/post_form.html', {"form": form})
