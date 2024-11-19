from django.urls import path
from .views import *

app_name = 'users'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('send-otp/', send_otp, name='send_code'),
    path('verify-otp/', verify_otp, name='verify_code'),
    path('logout/', logout_view, name='logout'),
    path('check-login/', check_login, name='check_login'),
    path('dashboard/',dashboard,name='dashboard'),
    path('test/',test,name='test'),
    path('login/',Login,name='login'),

]
