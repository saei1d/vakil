from django.urls import path
from .user_list import *

urlpatterns = [

    path('admin-list/',user_list,name='userlist'),

]
