from django.urls import path, re_path

from .views import *

app_name = 'blog'

urlpatterns = [
    path('testblog/',testblog,name='testblog'),
    path('load-more-blogs/', load_more_blogs, name='load_more_blogs'),
    path('about-us/', aboutus, name='about-us'),
    path('faq/', faq, name='faq'),
    path('blog/', blog, name='blog'),
    re_path(r'^blog-page/(?P<slug>.+)/$', blogpage, name='blogpage'),  # Allows any character

    path('create-blog/', PostCreate.as_view(), name='create-blog'),

    path('edit-blog/<int:id>/', PostEdit.as_view(), name='PostEdit'),

    path('blog/search/', PostSearchView.as_view(), name='search'),  # مسیر جستجو

    path('post-detail/<int:post_id>/', post_detail, name='post_detail'),

    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    
    path('delete-blog/<int:id>/',delete_blog,name='delete_blog')



    # path('contact/', contact, name='contact'),

]
