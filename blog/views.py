from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views import View
from .models import Post, Comment
from .form import *
from django.views.generic import ListView
from slugify import slugify


# Create your views here.


def aboutus(request):
    return render(request, 'blog/about.html')


def faq(request):
    return render(request, 'blog/faq.html')


def blog(request):
    blog = Post.objects.filter(is_published=True)
    return render(request, 'blog/blog.html', {'blog': blog})


def blogpage(request, slug):
    blog = get_object_or_404(Post, slug=slug)
    posts = Post.objects.filter(is_published=True)

    return render(request, 'blog/blog-page.html', {'blog': blog,'post':posts})


def contact(request):
    return render(request, 'blog/contact.html')


def post_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_date')
    for post in posts:
        print(post.id)

    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent__isnull=True)

    if request.method == "POST":
        form = CommentForm(request.POST)
        for field, value in request.POST.items():
            print(f"{field}: {value}")
            
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # دریافت مقدار parent از فرم
            parent_id = request.POST.get("parent")
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass  # اگر parent نامعتبر بود، مقدار آن را تغییر نده

            comment.save()

            # چاپ اطلاعات کامنت جدید
            print(f"کامنت جدید ایجاد شد - شناسه: {comment.id}")
            print(f"محتوای کامنت: {comment.content}")
            print(f"نویسنده: {comment.author}")
            print(f"تاریخ ایجاد: {comment.created_at}")
            print(f"پاسخ به کامنت دیگر: {comment.parent}")

            return redirect("blog:blog-page", post_id=post.id)
    else:
        form = CommentForm()
    return render(request, "blog/post_detail.html", {"post": post, "comments": comments, "form": form})


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


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff:  # فقط ادمین
        comment.delete()    
    return redirect("blog:blogpage", slug=comment.post.slug)


class PostCreate(View):
    def get(self, request):
        if request.user.is_staff:
            form = PostForm()
            return render(request, 'blog/post_form.html', {'form': form})
        else:
            return redirect('users:login')

    def post(self, request):
        if request.user.is_staff:
            # ایجاد یک نسخه از فرم با داده‌های ارسالی
            form = PostForm(request.POST, request.FILES)
            
            if form.is_valid():
                post = form.save(commit=False)
                post.slug = slugify(post.title, to_lower=True, separator="-")
                post.save()
                print(f"پست با موفقیت ذخیره شد - شناسه: {post.id}")
                return redirect('blog:blog')
            else:
                print("فرم معتبر نیست. خطاها:")
                for field, errors in form.errors.items():
                    print(f"{field}: {errors}")
            
            return render(request, 'blog/post_form.html', {"form": form})
        else:
            return redirect('users:login')


class PostEdit(View):
    def get(self, request, id):

        if request.user.is_staff:
            post = get_object_or_404(Post, id=id)
            form = PostForm(instance=post)
            return render(request, 'blog/post_form.html', {'form': form, 'post': post})
        else:
            return redirect('users:login')

    def post(self, request, id):

        if request.user.is_staff:

            post = get_object_or_404(Post, id=id)
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.slug = slugify(post.title)
                post.save()
                return redirect('blog:blog')
            return render(request, 'blog/post_form.html', {'form': form, 'post': post})
        else:
            return redirect('users:login')


class PostSearchView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # جستجو در عنوان و محتوا
            return Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query),
                is_published=True
            ).order_by('-published_date')
        return Post.objects.none()
