from django.urls import path
from django.shortcuts import redirect
from django.urls import path
from .views import support_click_notification
from .views import *

app_name = 'users'


def redirect_to_home(request):
    return redirect('home/')


urlpatterns = [
    path('', redirect_to_home),

    path('home/', HomeView.as_view(), name='home'),

    path('send-otp/', send_otp, name='send_code'),
    path('verify-otp/', verify_otp, name='verify_code'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/<str:username>/', dashboard, name='dashboard_with_username'),  # داشبورد برای کاربر خاص
    path('test/', test, name='test'),
    path('login/', Login, name='login'),
    path('check-text-service/', check_text_service, name='check_text_service'),
    path('update-name/', update_name, name='update_name'),
    path('set-nickname/<str:username>/', set_nickname, name='set_nickname'),
    path('send_otp_code/<str:phone_number>/<int:code>/', send_otp_code, name='send_otp_code'),
    path('support-click/', support_click_notification, name='support_click'),

]
