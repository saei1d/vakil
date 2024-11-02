from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from service.models import FreeForm
from users.models import Client
from django.contrib.auth import logout


# from django.contrib.auth import get_user_model


def send_code(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        print(phone_number)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# User = get_user_model()


def verify_code(request):
    phone_number = request.POST.get('phone_number')
    sms_code = request.POST.get('sms_code')
    print(phone_number, sms_code)

    if sms_code == '0000':  # Demo mode

        # Try to authenticate the user
        user = authenticate(request, username=phone_number, password=phone_number)

        if user is not None:
            # User exists, log them in
            login(request, user)
            print("loggedin")
            return JsonResponse({'success': True})
        else:
            # Check if user with phone number already exists
            if Client.objects.filter(phone_number=phone_number).exists():
                # User exists but failed to authenticate; handle this case if needed
                return JsonResponse({'success': False, 'error': 'User already exists but could not authenticate.'})
            else:
                # Create a new user
                user = Client.objects.create(username=phone_number, phone_number=phone_number)
                user.set_password(phone_number)  # Set the password to the phone number
                user.save()
                login(request, user)
                print("registered and logged in")
                return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'کد نامعتبر است'})


class HomeView(View):
    def get(self, request):
        return render(request, 'users/index.html', {'user': request.user})

    @method_decorator(login_required)
    def post(self, request):
        if request.user.is_questioned:
            return render(request, 'services/services.html', {'user': request.user})
        else:
            # دریافت اطلاعات از فرم
            form_data = {
                'name': request.POST.get('name'),
                'title': request.POST.get('title'),
                'department': request.POST.get('department'),
                'description': request.POST.get('description'),
            }

            # ایجاد FreeForm
            free_form = FreeForm.objects.create(
                user=request.user,
                title=form_data['title'],
                department=form_data['department'],
                description=form_data['description']
            )

            # به‌روزرسانی وضعیت is_questioned و نام کاربر
            request.user.is_questioned = True
            request.user.name = form_data['name']
            request.user.save()

            return redirect('services:services')


def check_login(request):
    if request.user.is_authenticated:
        return JsonResponse({'is_logged_in': True})
    return JsonResponse({'is_logged_in': False})


def logout_view(request):
    logout(request)
    return redirect('users:home')


def dashboard(request):
    return render(request, 'users/dashboard.html', {'user': request.user})


def test(request):
    return render(request, 'users/test.html')
