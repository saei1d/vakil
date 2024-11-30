from django.urls import path, re_path

from .views import *

app_name = 'blog'

urlpatterns = [
    path('about-us/', aboutus, name='about-us'),
    path('faq/', faq, name='faq'),
    path('blog/', blog, name='blog'),
    re_path(r'^blog-page/(?P<slug>.+)/$', blogpage, name='blogpage'),  # Allows any character
    # path('contact/', contact, name='contact'),

]
