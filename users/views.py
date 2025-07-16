import jdatetime
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.models import Post, Category
from payment.models import *
from service.models import FreeForm, UserServiceRequest
from django.contrib.auth import logout, login, authenticate
from django.utils import timezone
from django.http import JsonResponse
from django.utils.timezone import make_aware, now
from django.contrib.auth import authenticate, login
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Client
import random
from django.db.models import Q
from kavenegar import *
from django.views.decorators.csrf import csrf_exempt


def normalize_phone(phone):
    if phone.startswith('+98'):
        return '0' + phone[3:]
    return phone


def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = normalize_phone(data.get("phone"))
            print(phone)
            if not phone:
                return JsonResponse({
                    "success": False,
                    "swal": {
                        "title": "خطا",
                        "text": "شماره تلفن وارد نشده است.",
                        "icon": "error"
                    }
                })

            last_sent = request.session.get("last_otp_sent")
            # if last_sent:
            #     last_sent_time = make_aware(datetime.fromtimestamp(last_sent))
            #     if now() < last_sent_time + timedelta(minutes=2):
            #         return JsonResponse({
            #             "success": False,
            #             "swal": {
            #                 "title": "صبر کنید",
            #                 "text": "شما به تازگی کد دریافت کرده‌اید. لطفاً ۲ دقیقه صبر کنید.",
            #                 "icon": "warning"
            #             }
            #         })
            otp = random.randint(1000, 9999)
            print(otp)
            send_otp_code(request, phone, otp)
            request.session["otp"] = otp
            request.session["phone"] = phone
            request.session["last_otp_sent"] = now().timestamp()

            return JsonResponse({
                "success": True,
                "swal": {
                    "title": "موفق",
                    "text": "کد تایید با موفقیت ارسال شد.",
                    "icon": "success"
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "swal": {
                    "title": "خطا",
                    "text": "داده‌های ارسالی نامعتبر است.",
                    "icon": "error"
                }
            })
    return JsonResponse({
        "success": False,
        "swal": {
            "title": "خطا",
            "text": "متد درخواست نامعتبر است.",
            "icon": "error"
        }
    })


def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = normalize_phone(data.get("phone"))
            otp = str(data.get("otp"))

            if not phone or not otp:
                return JsonResponse({"success": False, "error": "شماره تلفن یا کد OTP وارد نشده است."})

            # بررسی OTP و شماره تلفن در سشن
            session_otp = str(request.session.get("otp"))
            session_phone = normalize_phone(request.session.get("phone"))

            if not session_otp or not session_phone:
                return JsonResponse({"success": False, "error": "لطفاً ابتدا کد OTP را دریافت کنید."})

            if session_otp != otp or session_phone != phone:
                return JsonResponse({"success": False, "error": "کد OTP یا شماره تلفن نامعتبر است."})

            # بررسی و ایجاد یا بروزرسانی کاربر
            user, created = Client.objects.get_or_create(username=phone)

            # فقط اگر کاربر جدید بود، رمز عبور ست می‌شود
            user.set_password(otp)
            user.save()

            # ورود به سیستم
            user = authenticate(request, username=phone, password=otp)
            if user:
                login(request, user)
                next_url = request.GET.get('next', '/')
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
                    return JsonResponse({"success": True, "next_url": next_url})
                return JsonResponse({"success": True, "next_url": '/home/'})

            return JsonResponse({"success": False, "error": "احراز هویت ناموفق بود."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "داده‌های JSON نامعتبر است."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "متد درخواست نامعتبر است."})


class HomeView(View):
    def get(self, request):
        form_data = request.session.get('form_data', {})

        posts = Post.objects.filter(
            is_published=True
        ).filter(
            Q(category=Category.CASES) | Q(category=Category.ANNOUNCEMENT)
        ).order_by('published_date')

        if 'form_data' in request.session:
            del request.session['form_data']

        return render(request, "users/index.html", {
            'name': form_data.get('name', ''),
            'title': form_data.get('title', ''),
            'department': form_data.get('department', ''),
            'description': form_data.get('description', ''),
            'post': posts,
        })

    def post(self, request):

        # دریافت اطلاعات از فرم
        form_data = {
            'name': request.POST.get('name'),
            'title': request.POST.get('title'),
            'department': request.POST.get('department'),
            'description': request.POST.get('description'),
        }

        if not request.user.is_authenticated:
            request.session['form_data'] = form_data
            messages.info(request, 'فرم شما موقتا ذخیره شد، بعد از ثبت نام آن را مجددا ارسال کنید.')
            next_url = request.POST.get('next', '/')
            return redirect(f'/login/?next={next_url}')

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

            request.user.is_questioned = True
            request.user.name = form_data['name']
            request.user.save()
            messages.info(request,
                          'سوال شما برای وکیل ارسال شد و تا قبل 24 ساعت پاسخ آنرا دریافت خواهید کرد درصورت نیاز و '
                          'ارتباط سریعتر با وکیل میتونید با تهیه سرویس تماس تلفنی با وکیل در ارتباط باشید')

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

        expired_services = UserServiceRequest.objects.filter(
            user=request.user,
            end_date__lt=current_date_shamsi.isoformat()
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
    return render(request, '404.html')


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
            request.user.name = name
            request.user.save()
            messages.success(request, "نام شما با موفقیت به‌روزرسانی شد.")
        else:
            messages.error(request, "لطفا نام خود را وارد کنید.")
    return redirect('users:dashboard')


def set_nickname(request, username):
    if request.method == "POST":
        nickname = request.POST.get("nickname")
        if nickname:
            user = Client.objects.get(username=username)
            user.last_name = nickname
            user.save()
            messages.success(request, "نام مستعار شما با موفقیت به‌روزرسانی شد.")
        else:
            messages.error(request, "لطفا نام مستعار خود را وارد کنید.")
    return redirect('users:dashboard')


from django.http import HttpResponse


def robots_txt(request):
    content = """
    
User-agent: *
Disallow: /adminpanel/
Disallow: /dashboard/

Sitemap: http://avahagh.ir/sitemap.xml
"""

    return HttpResponse(content, content_type="text/plain")


def send_otp_code(request, phone_number, code):
    try:
        api = KavenegarAPI('3063366B4A7055574C7152554774354F48366B4D444E33786532446D63376A7035714A2F38314C64664C633D')
        params = {
            'receptor': phone_number,
            'template': 'verifycode',
            'token': code,
            'type': 'sms'
        }
        response = api.verify_lookup(params)
        print(response)
    except APIException as e:
        print('APIException:', e)
    except HTTPException as e:
        print('HTTPException:', e)
