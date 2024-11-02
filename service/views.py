from django.shortcuts import render
from django.views import View


# Create your views here.


class Services(View):
    def get(self, request):
        return render(request, 'services/services.html')





class Pricing(View):
    def get(self, request):
        return render(request, 'services/pricing.html')
