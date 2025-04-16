import json
import jdatetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from blog.models import Post, Category
from payment.models import *
from service.models import FreeForm, UserServiceRequest
from users.models import Client
from django.contrib.auth import logout, login, authenticate
import random
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone


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
                        "error": "شمابه تازگی کد دریافت کردید و برای تغییر شماره یا کد مجدد باید 2 دقیقه صبر کنید"
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
                otp = request.session.get("otp")  # دریافت OTP از سشن
                print(otp)
                user = Client(username=phone, otp=otp)  # تنظیم otp
                user.set_password(otp)
                user.save()

            # احراز هویت کاربر
            user = authenticate(request, username=phone, password=otp)
            if user:
                login(request, user)

                next_url = request.GET.get('next', '/')
                print(next_url)
                # بررسی اینکه مسیر ایمن و معتبر است
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
                    return JsonResponse({"success": True, "next_url": next_url})
                else:
                    # مسیر پیش‌فرض در صورت نامعتبر بودن next
                    return JsonResponse({"success": True, "next_url": '/home/'})
            else:
                return JsonResponse({"success": False, "error": "Authentication failed."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


class HomeView(View):
    def get(self, request):
        form_data = request.session.get('form_data', {})
        posts = Post.objects.filter(is_published=True,category=Category.CASES).order_by('published_date')[:3]

        # پس از پردازش داده‌ها، می‌توانید داده‌ها را از سشن پاک کنید
        if 'form_data' in request.session:
            del request.session['form_data']

        return render(request, "users/index.html", {
            'name': form_data.get('name', ''),
            'title': form_data.get('title', ''),
            'department': form_data.get('department', ''),
            'description': form_data.get('description', ''),
            'post': posts,  # ارسال متغیر post به قالب
        })

    def post(self, request):

        # دریافت اطلاعات از فرم
        form_data = {
            'name': request.POST.get('name'),
            'title': request.POST.get('title'),
            'department': request.POST.get('department'),
            'description': request.POST.get('description'),
        }

        # بررسی اینکه آیا کاربر لاگین کرده است
        if not request.user.is_authenticated:
            # ذخیره داده‌ها در سشن
            request.session['form_data'] = form_data
            messages.info(request, 'فرم شما موقتا ذخیره شد، بعد از ثبت نام آن را مجددا ارسال کنید.')
            next_url = request.POST.get('next', '/')
            print(next_url)
            return redirect(f'/login/?next={next_url}')

        # ایجاد FreeForm
        if request.user.is_questioned:
            messages.info(request,
                          'شما قبلا یکبار از این فرم استفاده کرده اید برای خرید سرویس از این صفحه استفاده کنید')
            return render(request, 'services/pricing.html', {'user': request.user})
        else:
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
            messages.info(request,
                          'سوال شما برای وکیل ارسال شد و تا قبل 24 ساعت پاسخ آنرا دریافت خواهید کرد درصورت نیاز و ارتباط سریعتر با وکیل میتونید با تهیه سرویس تماس تلفنی با وکیل در ارتباط باشید')

            return redirect('service:pricing')


def logout_view(request):
    logout(request)
    return redirect('users:home')


@login_required
def dashboard(request, username=None):
    if request.user.is_staff:
        if username is not None:
            user = get_object_or_404(Client, username=username)  # بررسی وجود کاربر
            services = UserServiceRequest.objects.filter(user=user)
            transactions = Payment.objects.filter(user=user)
        else:
            user = request.user
            services = UserServiceRequest.objects.filter(user=user)
            transactions = Payment.objects.filter(user=user)
    else:
        user = request.user
        noww = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=noww.date())

        # فیلتر کردن سرویس‌هایی که تاریخ پایان آن‌ها گذشته است
        expired_services = UserServiceRequest.objects.filter(
            user=request.user,
            end_date__lt=current_date_shamsi.isoformat()  # تبدیل تاریخ شمسی به ISO برای مقایسه
        )
        expired_services.update(is_active=False)
        services = UserServiceRequest.objects.filter(user=user)
        transactions = Payment.objects.filter(user=user)
        


    return render(request, 'users/dashboard.html', {
        'user': user,
        'services': services,
        'transactions': transactions,
    })


def test(request):
    return render(request, 'users/test.html')


def Login(request):
    return render(request, 'users/login.html')


def check_text_service(request):
    if request.user.is_authenticated:
        has_text_service = UserServiceRequest.objects.filter(
            user=request.user,
            service__name='text',
            is_active=True
        ).exists()
        return JsonResponse({'has_text_service': has_text_service})
    else:
        return JsonResponse({'has_text_service': False, 'login_required': True})


def update_name(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            request.user.name = name  # اصلاح دسترسی به نام کاربر
            request.user.save()  # ذخیره تغییرات در کاربر
            messages.success(request, "نام شما با موفقیت به‌روزرسانی شد.")
        else:
            messages.error(request, "لطفا نام خود را وارد کنید.")
    return redirect('users:dashboard')  # اصلاح نام الگو به 'users:dashboard'


def set_nickname (request,username):
    if request.method == "POST":
        nickname = request.POST.get("nickname")
        if nickname:
            user = Client.objects.get(username=username)
            user.last_name = nickname  # ذخیره نام مستعار در فیلد lastname
            user.save()  # ذخیره تغییرات در کاربر
            messages.success(request, "نام مستعار شما با موفقیت به‌روزرسانی شد.")
        else:
            messages.error(request, "لطفا نام مستعار خود را وارد کنید.")
    return redirect('users:dashboard')  # بازگشت به داشبورد کاربر