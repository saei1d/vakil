from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from service.models import UserServiceRequest
from users.models import Client
from django.core.paginator import Paginator


def user_list(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)

    # جستجو
    search_query = request.POST.get('pk', '') if request.method == "POST" else request.GET.get('search', '')

    if search_query:
        users = Client.objects.filter(username__icontains=search_query) | Client.objects.filter(
            name__icontains=search_query)
    else:
        users = Client.objects.all()  # نمایش تمام کاربران

    # پیجینیشن
    paginator = Paginator(users, 25)  # 25 کاربر در هر صفحه
    page_number = request.GET.get('page')  # شماره صفحه از URL
    page_obj = paginator.get_page(page_number)  # دریافت صفحه مورد نظر

    return render(request, 'users/userlist.html', {
        'page_obj': page_obj,
        'search_query': search_query  # ارسال کوئری جستجو به قالب
    })


def service_list(request, username):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)
    user = Client.objects.get(username=username)
    services = UserServiceRequest.objects.filter(user=user)
    return render(request, 'users/servicelist.html', {'services': services})


def update_service(request, pk):
    service = get_object_or_404(UserServiceRequest, id=pk)

    if request.method == 'POST':
        service.start_date = request.POST.get('start_date')
        service.is_active = request.POST.get('is_active') == '1'
        service.description = request.POST.get('description')
        service.is_accepted = request.POST.get('is_accepted') == '1'
        service.title = request.POST.get('title')
        service.end_date = request.POST.get('end_date')

        service.save()  # ذخیره تغییرات در دیتابیس
        return redirect('userlist')  # به صفحه لیست سرویس‌ها بروید

    return render(request, 'users/servicelist.html', {'service': service})
