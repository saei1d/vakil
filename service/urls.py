from django.urls import path

from .views import *

app_name = 'service'

urlpatterns = [
    path('service/', Pricing.as_view(), name='pricing'),
    path('call/', Call, name='call'),
    path('payam/', Payam, name='payam'),
    path('shekaiatname/', Shekaiatname, name='shekaiatname'),
    path('ekhtesasi/', Ekhtesasi, name='ekhtesasi'),
    path('check-auth/', check_authentication, name='check-authentication'),
    path('verify/', payment_verify, name='verify'),


]


