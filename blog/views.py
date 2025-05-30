from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views import View
from .models import Post, Comment
from .form import *
from django.views.generic import ListView
from django.http import JsonResponse
from django.template.loader import render_to_string

# Create your views here.


def aboutus(request):
    return render(request, 'blog/about.html')


def faq(request):
    return render(request, 'blog/faq.html')


def blog(request):
    blog = Post.objects.filter(is_published=True)
    return render(request, 'blog/blog.html', {'blog': blog})



from django.db.models import F

def blogpage(request, slug):
    blog = get_object_or_404(Post, slug=slug)
    # افزایش تعداد بازدیدها با استفاده از F() برای جلوگیری از race condition
    Post.objects.filter(pk=blog.pk).update(view=F('view') + 1)
    related_posts = Post.objects.filter(category=blog.category, is_published=True).exclude(id=blog.id)[:5]
    
    return render(request, 'blog/blog-page.html', {
        'blog': blog,
        'related_posts': related_posts
    })


def contact(request):
    return render(request, 'blog/contact.html')


def post_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-published_date')        
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent__isnull=True)

    if request.method == "POST":
        form = CommentForm(request.POST)
            
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
                    pass 

            comment.save()



            return redirect(request.META.get('HTTP_REFERER', 'blog:blogpage'))
    else:
        form = CommentForm()
    return render(request, "blog/faq.html", {"post": post, "comments": comments, "form": form})


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
                post.slug = post.title.lower().replace(' ', '-').replace('_', '-').replace('.', '-').strip('-')
                post.save()
                return redirect('blog:blog')
            else:
                print("فرم معتبر نیست. خطاها:")

            
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
                # اضافه کردن فیلدهای views و time_to_read
                post.save()
                print(1)
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


def delete_blog(request,id):
    if request.user.is_staff:
        post = get_object_or_404(Post, id=id)
        post.delete()
        return redirect('admin_blogs')
    else:
        return redirect('users:login')
    
    
def testblog(request):
    return render(request,'blog/bonyadvokala.html')


def load_more_blogs(request):
    if request.method == "GET":
        offset = int(request.GET.get("offset", 0))
        limit = 8
        blogs = Post.objects.filter(is_published=True).order_by('-published_date')[offset:offset+limit]
        html = render_to_string("blog/blog_list_partial.html", {"blogs": blogs})
        has_more = Post.objects.filter(is_published=True).count() > offset + limit
        return JsonResponse({"html": html, "has_more": has_more})
    return JsonResponse({"error": "Invalid request"}, status=400)