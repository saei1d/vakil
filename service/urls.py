from django.urls import path

from .views import *

app_name = 'blog'

urlpatterns = [
    path('service/', Services.as_view(), name='blog'),
    path('pricing/', Pricing.as_view(), name='pricing'),

]


