from django.http import JsonResponse
from django.shortcuts import render
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
