from django.urls import path
from .user_list import *

urlpatterns = [
    path('admin-list/', user_list, name='userlist'),
    path('admin-service/<str:username>/', service_list, name='servicelist'),
    path('update-service/<int:pk>/', update_service, name='update_service'),
    path('add-service/<str:username>/', add_service, name='add_service'),
    path('delete-service/<int:pk>/', delete_service, name='delete_service'),
]