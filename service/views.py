from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta, time
from django.utils import timezone
import jdatetime

from service.models import UserServiceRequest


# Create your views here.


class Services(View):
    def get(self, request):
        return render(request, 'services/services.html')


class Pricing(View):
    def get(self, request):
        return render(request, 'services/pricing.html')


@login_required
def Call(request):
    if request.method == 'POST':
        tarikh = request.POST['date']
        saat = request.POST['clock']
        moddat = request.POST['duration']

        # تبدیل تاریخ ورودی به جلالی
        jalali_date = jdatetime.datetime.strptime(tarikh, '%Y/%m/%d').date()

        # دریافت زمان محلی
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())
        current_time_shamsi = jdatetime.datetime.fromgregorian(datetime=now).time().replace(microsecond=0)

        # تبدیل saat به نوع time
        saat = datetime.strptime(saat, '%H:%M:%S').time()
        future_time = (now + timedelta(minutes=45)).time().replace(microsecond=0)

        # تعریف محدوده زمانی مجاز (۸ صبح تا ۱۰ شب)
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(22, 0)  # 10:00 PM

        if jalali_date < current_date_shamsi:
            print("error1")
            return render(request, "services/pricing.html")
        elif not (start_time <= saat <= end_time):
            print("error15")
            return render(request, "services/pricing.html")

        elif jalali_date == current_date_shamsi and saat < current_time_shamsi:
            print("error2")
            return render(request, "services/pricing.html")
        elif jalali_date == current_date_shamsi and saat < future_time:
            print("error3")

        else:
            end_service = jalali_date + timedelta(days=1)

            # Convert to ISO format
            start_date_iso = jalali_date.isoformat()
            end_date_iso = end_service.isoformat()

            user_service_call = UserServiceRequest.objects.create(
                user=request.user,
                service_id=1,
                title="تماس تلفنی",
                is_accepted=True,
                description={f'  در زمان {saat} و به مدت {moddat} ساعت با شما تماس خواهیم گرفت '},
                start_date=start_date_iso,  # Set start_date in ISO format
                end_date=end_date_iso  # Set end_date in ISO format
            )
            return redirect('users:dashboard')  # 'dashboard' نام URL مربوط به داشبورد شماست


@login_required
def Payam(request):
    if request.method == 'POST':
        tarikh_chat = request.POST['date']
        moddat_chat = request.POST['duration']

        # تبدیل تاریخ ورودی به جلالی
        jalali_date = jdatetime.datetime.strptime(tarikh_chat, '%Y/%m/%d').date()

        # دریافت زمان محلی
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        # تبدیل saat به نوع time

        # تعریف محدوده زمانی مجاز (۸ صبح تا ۱۰ شب)

        if jalali_date < current_date_shamsi:
            print("error1")
            return render(request, "services/pricing.html")
        else:
            moddat_chat = int(moddat_chat)
            end_service = jalali_date + timedelta(days=int(moddat_chat))  # Convert to integer if necessary

            # Convert to ISO format
            start_date_iso = jalali_date.isoformat()
            end_date_iso = end_service.isoformat()

            user_service_payam = UserServiceRequest.objects.create(
                user=request.user,
                service_id=2,
                title="چت",
                is_accepted=True,
                description={f'{moddat_chat} روز '},
                start_date=start_date_iso,  # Set start_date in ISO format
                end_date=end_date_iso  # Set end_date in ISO format
            )
            return redirect('users:dashboard')  # 'dashboard' نام URL مربوط به داشبورد شماست


@login_required
def Shekaiatname(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        group = request.POST['group']
        if group == "1":
            group = "تنظیم لایحه"
        elif group == "2":
            group = "تنظیم دادخواست"
        elif group == "3":
            group = "تنظیم شکواییه"
        elif group == "4":
            group = "تنظیم اظهارنامه"

        jalali_date = jdatetime.datetime.now()

        end_service = jalali_date + timedelta(days=30)  # Convert to integer if necessary

        start_date_iso = jalali_date.isoformat()
        end_date_iso = end_service.isoformat()

        user_service_shekaiat = UserServiceRequest.objects.create(
            user=request.user,
            service_id=3,
            title=f"{group}",
            is_accepted=False,
            description=f'{title}--{description}',
            start_date=start_date_iso,  # Set start_date in ISO format
            end_date=end_date_iso  # Set end_date in ISO format
        )

        end_service2 = jalali_date + timedelta(days=2)  # Convert to integer if necessary
        end_date_iso2 = end_service2.isoformat()

        user_service_payam = UserServiceRequest.objects.create(
            user=request.user,
            service_id=2,
            title="چت مختص تنظیم اوراق قضایی",
            is_accepted=False,
            description={f'یک روز'},
            start_date=start_date_iso,  # Set start_date in ISO format
            end_date=end_date_iso2  # Set end_date in ISO format
        )

        return redirect('users:dashboard')  # 'dashboard' نام URL مربوط به داشبورد شماست


@login_required
def Ekhtesasi(request):
    if request.method == 'POST':
        tarikh_ekhtesasi = request.POST['date']
        moddat_ekhtesasi = request.POST['duration']

        # تبدیل تاریخ ورودی به جلالی
        jalali_date = jdatetime.datetime.strptime(tarikh_ekhtesasi, '%Y/%m/%d').date()

        # دریافت زمان محلی
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        # تبدیل saat به نوع time

        # تعریف محدوده زمانی مجاز (۸ صبح تا ۱۰ شب)

        if jalali_date < current_date_shamsi:
            print("error1")
            return render(request, "services/pricing.html")
        else:
            moddat_ekhtesasi = int(moddat_ekhtesasi)
            end_service = jalali_date + timedelta(days=int(moddat_ekhtesasi))  # Convert to integer if necessary

            # Convert to ISO format
            start_date_iso = jalali_date.isoformat()
            end_date_iso = end_service.isoformat()

            user_service_payam = UserServiceRequest.objects.create(
                user=request.user,
                service_id=4,
                title="وکیل اختصاصی",
                is_accepted=False,
                description={f''},
                start_date=start_date_iso,  # Set start_date in ISO format
                end_date=end_date_iso  # Set end_date in ISO format
            )
            return redirect('users:dashboard')  # 'dashboard' نام URL مربوط به داشبورد شماست


from django.http import JsonResponse


def check_authentication(request):
    return JsonResponse({'authenticated': request.user.is_authenticated})
