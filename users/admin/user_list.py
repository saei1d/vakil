from django.http import JsonResponse
from django.shortcuts import render
from users.models import Client


def user_list(request, pk=None):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)

    if request.method == "GET":
        users = Client.objects.all()  # نمایش تمام کاربران
        return render(request, 'users/userlist.html', {'users': users})

    elif request.method == "POST":
        print(1111111)
        print(pk)
        if not pk:
            return JsonResponse({'error': 'شماره همراه یا نام شخص را وارد کنید'}, status=400)

        users = Client.objects.filter(phone_number__icontains=pk) | Client.objects.filter(name__icontains=pk )

        if not users.exists():
            return JsonResponse({'message': 'کاربری یافت نشد'}, status=404)

        return render(request, 'users/userlist.html', {'users': users})

    return JsonResponse({'error': 'متد پشتیبانی نمی‌شود'}, status=405)
