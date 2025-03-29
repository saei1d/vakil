from django.urls import path
from .views import *

app_name = 'users'

from django.shortcuts import redirect


def redirect_to_home(request):
    return redirect('home/')


urlpatterns = [
    path('', redirect_to_home),
    path("66041575.txt", serve_enamad_file),

    path('home/', HomeView.as_view(), name='home'),

    path('send-otp/', send_otp, name='send_code'),
    path('verify-otp/', verify_otp, name='verify_code'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/<str:username>/', dashboard, name='dashboard_with_username'),  # داشبورد برای کاربر خاص
    path('test/', test, name='test'),
    path('login/', Login, name='login'),
    path('check-text-service/', check_text_service, name='check_text_service'),

]
