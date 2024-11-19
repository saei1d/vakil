import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from service.models import FreeForm
from users.models import Client
from django.contrib.auth import logout ,login ,authenticate
import random
from django.utils.timezone import now ,make_aware
from datetime import datetime,timedelta


def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone")

            if not phone:
                return JsonResponse({"success": False, "error": "Phone number is missing."})

            # بررسی محدودیت زمانی
            last_sent = request.session.get("last_otp_sent")
            if last_sent:
                last_sent_time = make_aware(datetime.fromtimestamp(last_sent))  # تبدیل به offset-aware
                if now() < last_sent_time + timedelta(minutes=2):
                    return JsonResponse({
                        "success": False,
                        "error": "You can request another OTP after 2 minutes."
                    })

            # تولید و ارسال OTP
            otp = "1234"  # در اینجا یک کد نمونه قرار داده شده است
            request.session["otp"] = otp
            request.session["phone"] = phone
            request.session["last_otp_sent"] = now().timestamp()  # ذخیره زمان ارسال

            # کد مربوط به ارسال پیامک را اینجا قرار دهید
            print(f"OTP for {phone}: {otp}")

            return JsonResponse({"success": True, "message": "OTP sent successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone")
            otp = data.get("otp")
            print(otp,phone)
            # بررسی صحت داده‌های ورودی
            if not phone or not otp:
                return JsonResponse({"success": False, "error": "Phone or OTP is missing."})

            # بررسی صحت OTP و شماره تلفن در سشن
            session_otp = request.session.get("otp")
            session_phone = request.session.get("phone")

            if str(session_otp) != str(otp) or session_phone != phone:
                return JsonResponse({"success": False, "error": "Invalid OTP or phone number."})

            # بررسی وجود کاربر
            try:
                user = Client.objects.get(username=phone)
            except ObjectDoesNotExist:
                # ایجاد کاربر جدید در صورت عدم وجود
                user = Client(username=phone)
                user.set_password(otp)
                user.save()

            # احراز هویت کاربر
            user = authenticate(request, username=phone, password=otp)
            if user:
                login(request, user)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Authentication failed."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


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

def Login(request):
    return render(request, 'users/login.html')
