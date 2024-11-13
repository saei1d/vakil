from django.contrib import admin

from service.models import Service, UserServiceRequest
from users.models import Client

# Register your models here.

admin.site.register(Service)
admin.site.register(Client)
admin.site.register(UserServiceRequest)
