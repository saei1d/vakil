from django.urls import path

from .views import *

app_name = 'blog'

urlpatterns = [
    path('about-us/', aboutus, name='about-us'),
    path('faq/', faq, name='faq'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),

]