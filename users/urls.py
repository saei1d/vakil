from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('send-code/', send_code, name='send_code'),
    path('verify-code/', verify_code, name='verify_code'),
    path('logout/', logout_view, name='logout'),
    path('check-login/', check_login, name='check_login'),
    path('dashboard/',dashboard,name='dashboard'),
    path('test/',test,name='test'),

]
