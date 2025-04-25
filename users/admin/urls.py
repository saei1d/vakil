from django.urls import path
from .admin_panel import *


urlpatterns = [
    path('dashboard/',admindashboard,name='admindashboard'),

    path('admin-userlist/', admin_userlist, name='admin_userlist'),

    path('admin-userinfo/<int:id>/',admin_userinfo,name='admin_userinfo'),
    
    path('update-user-info/<int:id>/',update_user_info,name='update_user_info'),
    
    path('admin-userupdate-service/<int:id>/', admin_userupdate_service, name='admin_userupdate_service'),
    
    path('admin-useradd-service/<str:username>/', admin_useradd_service, name='admin_useradd_service'),
    
    path('admin-add-payment/<str:username>/', admin_add_payment, name='admin_add_payment'),
  
    path('promote-user/<str:username>/',promote_user,name='promote_user'),
    
    path('admin-blogs/', admin_blogs, name='admin_blogs'),
    path('delete-blog/<int:id>',delete_blog, name='delete_blog'),



    path('admin-services/', admin_services, name='admin_services'),
    path('admin-service/add/', admin_add_service, name='admin_add_service'),
    path('admin-service/edit/<int:id>/', admin_edit_service, name='admin_edit_service'),
    path('admin-service/delete/<int:id>/', admin_delete_service, name='admin_delete_service'),
    
    
    
    path('admin-user-services/', admin_user_services, name='admin_user_services'),
    
    path('admin-user-payments/', admin_user_payments, name='admin_user_payments'),
]