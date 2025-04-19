from django.urls import path
from .admin_panel import *


urlpatterns = [
    path('dashboard/',admindashboard,name='admindashboard'),

    path('admin-list/', admin_list, name='admin_list'),

    
    path('admin-service/<str:username>/', service_list, name='servicelist'),
    path('update-service/<int:pk>/', update_service, name='update_service'),
    path('add-service/<str:username>/', add_service, name='add_service'),
    path('delete-service/<int:pk>/', delete_service, name='delete_service'),
    path('blog-uncomplete/',uncomplete_blog, name='uncomplete_blog'),
    path('promote-user/<str:username>/',promote_user,name='promote_user'),
    path('delete-blog/<int:id>',delete_blog, name='delete_blog'),
    path('admin-service/', service, name='service'),
    
]