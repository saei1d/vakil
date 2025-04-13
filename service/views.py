from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta, time
from django.utils import timezone
import jdatetime
from django.http import JsonResponse
from service.models import UserServiceRequest
from django.contrib import messages
import os
from .models import Service, UserServiceRequest  # فرضی
from payment.models import Payment
from zarinpal import ZarinPal
from django.conf import settings


class Pricing(View):
    def get(self, request):
        return render(request, 'services/pricing.html')

class ServiceHandler:
    @staticmethod
    def validate_date(jalali_date, current_date_shamsi):
        if jalali_date < current_date_shamsi:
            print("error1")
            return False
        return True

    @staticmethod
    def create_service_request(user, service_id, title, is_accepted, description, start_date, end_date, attachment=None):
        return UserServiceRequest.objects.create(
            user=user,
            service_id=service_id,
            title=title,
            is_accepted=is_accepted,
            description=description,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            attachment=attachment
        )

@login_required
def Call(request):
    if request.method == 'POST':
        tarikh = request.POST['date']
        saat = request.POST['clock']
        moddat = request.POST['duration']

        jalali_date = jdatetime.datetime.strptime(tarikh,'%Y/%m/%d').date()
        print(f"jalalidate: {jalali_date}")
        now = timezone.localtime(timezone.now())

        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())
        print(f"تاریخ شمسی فعلی: {current_date_shamsi}")
        
        current_time_shamsi = jdatetime.datetime.fromgregorian(datetime=now).time().replace(microsecond=0)
        print(f"زمان شمسی فعلی: {current_time_shamsi}")
        
        future_time = (now + timedelta(minutes=45)).time().replace(microsecond=0)
        
        start_time, end_time = time(8, 0), time(22, 0)

        if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
            messages.error(request, 'تاریخ انتخاب شده معتبر نیست. لطفا تاریخ آینده را انتخاب کنید.')
            return render(request, "services/pricing.html")
        saat_time = datetime.strptime(saat, '%H:%M:%S').time()
        if not (start_time <= saat_time <= end_time):
            messages.error(request, 'زمان انتخاب شده خارج از ساعات کاری است. لطفا بین ساعت ۸ صبح تا ۱۰ شب انتخاب کنید.')
            return render(request, "services/pricing.html")
        if jalali_date == current_date_shamsi and (datetime.strptime(saat, '%H:%M:%S').time() < current_time_shamsi or datetime.strptime(saat, '%H:%M:%S').time() < future_time):
            messages.error(request, 'زمان انتخاب شده معتبر نیست. لطفا زمان آینده را انتخاب کنید.')
            return render(request, "services/pricing.html")

        end_service = jalali_date + timedelta(days=1)

        service = Service.objects.get(id=1)
        service_request = ServiceHandler.create_service_request(
            request.user, 1, "تماس تلفنی", True,
            {f'در زمان {saat} و به مدت {moddat} ساعت با شما تماس خواهیم گرفت'},
            jalali_date, end_service
        )

        if service.price == 0:
            service_request.is_paid = True
            service_request.save()
            return redirect('users:dashboard')
        else:
            zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
            amount = service.price
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                service=service
            )

            result = zarinpal.request({
                'amount': amount,
                'callback_url': settings.ZARINPAL_CALLBACK_URL,
                'description': f'پرداخت برای تماس تلفنی - {moddat} ساعت',
            })

            if result.data.code == 100:
                payment.authority = result.data.authority
                payment.save()
                return redirect(zarinpal.get_payment_link(result.data.authority))
            else:
                return render(request, 'error.html', {'message': result.data.message})

@login_required
def Payam(request):
    if request.method == 'POST':
        tarikh_chat = request.POST['date']
        moddat_chat = int(request.POST['duration'])
        jalali_date = jdatetime.datetime.strptime(tarikh_chat, '%Y/%m/%d').date()

        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
            return render(request, "services/pricing.html")

        service = Service.objects.get(id=2)
        end_service = jalali_date + timedelta(days=moddat_chat)

        service_request = UserServiceRequest.objects.create(
            user=request.user,
            service=service,
            start_date=jalali_date.isoformat(),
            end_date=end_service.isoformat(),
            description=f'{moddat_chat} روز مشاوره چت',
            is_paid=False
        )

        if service.price == 0:
            service_request.is_paid = True
            service_request.save()
            return redirect('users:dashboard')
        else:
            zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
            amount = service.price
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                service=service
            )

            result = zarinpal.request({
                'amount': amount,
                'callback_url': settings.ZARINPAL_CALLBACK_URL,
                'description': f'پرداخت برای مشاوره چت - {moddat_chat} روز',
            })

            if result.data.code == 100:
                payment.authority = result.data.authority
                payment.save()
                return redirect(zarinpal.get_payment_link(result.data.authority))
            else:
                return render(request, 'error.html', {'message': result.data.message})

@login_required
def Shekaiatname(request):
    if request.method == 'POST':
        pending_request = UserServiceRequest.objects.filter(
            user=request.user,
            is_accepted=False
        ).exists()
        
        if pending_request:
            messages.error(request, 'شما یک درخواست در حال انتظار دارید. لطفا تا تایید یا رد درخواست قبلی صبر کنید.')
            return redirect('users:dashboard')
            
        title = request.POST['title']
        description = request.POST['description']
        group = request.POST['group']
        attachment = request.FILES.get('attachment')
        
        if attachment:
            allowed_extensions = ['.pdf', '.zip', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            max_size = 40 * 1024 * 1024
            
            file_extension = os.path.splitext(attachment.name)[1].lower()
            if file_extension not in allowed_extensions:
                messages.error(request, 'فرمت فایل مجاز نیست. لطفا از فرمت‌های PDF, ZIP, JPG, PNG, DOC, DOCX استفاده کنید.')
                return redirect('service:pricing')
            
            if attachment.size > max_size:
                messages.error(request, 'حجم فایل بیشتر از 40 مگابایت است. لطفا فایل کوچکتری ارسال کنید.')
                return redirect('service:pricing')

        group_map = {
            "1": "تنظیم لایحه",
            "2": "تنظیم دادخواست", 
            "3": "تنظیم شکواییه",
            "4": "تنظیم اظهارنامه"
        }
        group = group_map.get(group, "")

        jalali_date = jdatetime.datetime.now()
        end_service = jalali_date + timedelta(days=5)

        service = Service.objects.get(id=3)
        service_request = ServiceHandler.create_service_request(
            request.user, 3, f"{group}", False,
            f'{title}--{description}',
            jalali_date, end_service,
            attachment=attachment
        )

        if service.price == 0:
            service_request.is_paid = True
            service_request.save()
            messages.success(request, 'درخواست شما با موفقیت ثبت شد.')
            return redirect('users:dashboard')
        else:
            zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
            amount = service.price
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                service=service
            )

            result = zarinpal.request({
                'amount': amount,
                'callback_url': settings.ZARINPAL_CALLBACK_URL,
                'description': f'پرداخت برای تنظیم {group}',
            })

            if result.data.code == 100:
                payment.authority = result.data.authority
                payment.save()
                return redirect(zarinpal.get_payment_link(result.data.authority))
            else:
                return render(request, 'error.html', {'message': result.data.message})

@login_required
def Ekhtesasi(request):
    if request.method == 'POST':
        tarikh_ekhtesasi = request.POST['date']
        moddat_ekhtesasi = request.POST['duration']
        jalali_date = jdatetime.datetime.strptime(tarikh_ekhtesasi, '%Y/%m/%d').date()
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
            return render(request, "services/pricing.html")

        moddat_ekhtesasi = int(moddat_ekhtesasi)
        end_service = jalali_date + timedelta(days=moddat_ekhtesasi)

        service = Service.objects.get(id=4)
        service_request = ServiceHandler.create_service_request(
            request.user, 4, "وکیل اختصاصی", False,
            {''},
            jalali_date, end_service
        )

        if service.price == 0:
            service_request.is_paid = True
def check_authentication(request):
    return JsonResponse({'authenticated': request.user.is_authenticated})



def payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    payment = Payment.objects.get(authority=authority)

    if status == 'OK':
        zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
        result = zarinpal.verify({
            'amount': payment.amount,
            'authority': authority,
        })

        if result.data.code == 100:
            payment.is_paid = True
            payment.save()

            # فعال‌سازی سرویس
            service_request = payment.service_request
            service_request.is_paid = True
            service_request.save()

            return render(request, 'payment/success.html', {'ref_id': result.data.ref_id})
        else:
            return render(request, 'error.html', {'message': result.data.message})
    else:
        return render(request, 'error.html', {'message': 'پرداخت توسط کاربر لغو شد.'})
