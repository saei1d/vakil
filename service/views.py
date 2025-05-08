from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect , reverse
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
import requests


class Pricing(View):
    def get(self, request):
        services = Service.objects.all()
        return render(request, 'services/pricing.html',{'services':services})

class ServiceHandler:
    @staticmethod
    def validate_date(jalali_date, current_date_shamsi):
        if jalali_date < current_date_shamsi:
            print("error1")
            return False
        return True

    @staticmethod
    def create_service_request(user, service, title, is_accepted, description, start_date, end_date, attachment=None,):
        return UserServiceRequest.objects.create(
            user=user,
            service=service,
            title=title,
            is_accepted=is_accepted,
            description=description,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            attachment=attachment,
            
        )
    @staticmethod
    def payment_request(user, service,amount, description):
        try:
            zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
            

            payment = Payment.objects.create(
                user=user,
                service_request=service,  # چون service در اینجا همون service_request هست
                amount=amount,          
                transaction_type='deposit'
            )


            result = zarinpal.request({
                'amount': amount,
                'callback_url': settings.ZARINPAL_CALLBACK_URL,
                'description': description,
            })

            if result.data.code == 100:
                payment.authority = result.data.authority
                payment.save()
                return payment, result.data.authority
            else:
                payment.delete()
                return None, result.data.message

        except Exception as e:
            return None, str(e)



def payment_verify(request):
    try:
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        if not authority or not status:
            return redirect('service:pricing')

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

                service_request = payment.service_request
                service_request.is_paid = True
                service_request.save()

                return redirect('users:dashboard')

            else:
                return redirect('service:pricing')

        else:
            return redirect('service:pricing')

    except Payment.DoesNotExist:
        return redirect('service:pricing')
    except Exception as e:
        return redirect('service:pricing')




@login_required
def Call(request):
    try:
        if request.method == 'POST':
            tarikh = request.POST.get('date')
            saat = request.POST.get('clock')
            moddat = request.POST.get('duration')

            if not all([tarikh, saat, moddat]):
                messages.error(request, 'لطفا تمام فیلدها را پر کنید')
                return redirect('service:pricing')

            jalali_date = jdatetime.datetime.strptime(tarikh, '%Y/%m/%d').date()
            now = timezone.localtime(timezone.now())
            current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())
            current_time_shamsi = jdatetime.datetime.fromgregorian(datetime=now).time().replace(microsecond=0)
            future_time = (now + timedelta(minutes=45)).time().replace(microsecond=0)
            start_time, end_time = time(8, 0), time(22, 0)

            if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
                messages.error(request, 'تاریخ انتخاب شده معتبر نیست')
                return redirect('service:pricing')

            try:
                saat_time = datetime.strptime(saat, '%H:%M:%S').time()
                if not (start_time <= saat_time <= end_time):
                    messages.error(request, 'زمان انتخاب شده خارج از ساعات کاری است')
                    return redirect('service:pricing')

                if jalali_date == current_date_shamsi and (saat_time < current_time_shamsi or saat_time < future_time):
                    messages.error(request, 'زمان انتخاب شده معتبر نیست')
                    return redirect('service:pricing')

            except ValueError:
                messages.error(request, 'فرمت زمان نامعتبر است')
                return redirect('service:pricing')

            end_service = jalali_date + timedelta(days=1)
            service = Service.objects.get(id=1)

            print(moddat)
            moddat = int(moddat)
            mablagh = service.price * moddat
            print(mablagh)
            service_request = ServiceHandler.create_service_request(
                request.user, service, "تماس تلفنی", True,
                f'در زمان {saat} و به مدت {moddat} ساعت با شما تماس خواهیم گرفت',
                jalali_date, end_service,
            )

            if service.price == 0:
                service_request.is_paid = True
                service_request.save()
                messages.success(request, 'درخواست با موفقیت ثبت شد')
                return redirect('users:dashboard')


            
            # درخواست پرداخت
            payment, authority_or_error = ServiceHandler.payment_request(
                request.user,
                service_request,
                mablagh,
                f'پرداخت برای تماس تلفنی - {moddat} ساعت'
            )

            if payment:
                return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority_or_error}")
            else:
                messages.error(request, authority_or_error)
                return redirect('service:pricing')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('service:pricing')

@login_required
def Payam(request):
    if request.method == 'POST':
        tarikh_chat = request.POST['date']
        moddat_chat = int(request.POST['duration'])
        jalali_date = jdatetime.datetime.strptime(tarikh_chat, '%Y/%m/%d').date()
        
        print(tarikh_chat,moddat_chat,jalali_date)
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
            messages.error(request, 'تاریخ انتخاب شده معتبر نیست')
            return redirect('service:pricing')

        end_service = jalali_date + timedelta(days=moddat_chat)
        service = Service.objects.get(id=2)

        service_request = ServiceHandler.create_service_request(
            request.user, service, "مشاوره چت", False,
            f'{moddat_chat} روز مشاوره چت',
            jalali_date, end_service
        )

        if service.price == 0:
            service_request.is_paid = True
            service_request.save()
            return redirect('users:dashboard')
        
        print(moddat_chat)
        mablagh = service.price * moddat_chat
        
        
        payment, authority_or_error = ServiceHandler.payment_request(
            request.user,
            service_request,
            mablagh,
            f'پرداخت برای مشاوره چت - {moddat_chat} روز'
        )

        if payment:
            return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority_or_error}")
        else:
            messages.error(request, authority_or_error)
            return redirect('service:pricing')


@login_required
def Shekaiatname(request):
    if request.method == 'POST':
        turnstile_response = request.POST.get("cf-turnstile-response")
        secret_key = '0x4AAAAAABOXzQoGG9cbDjMlFN66fS6lmT4'
        verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        
        resp = requests.post(verify_url, data={
            'secret': secret_key,
            'response': turnstile_response,
            'remoteip': request.META.get('REMOTE_ADDR')
        })
        result = resp.json()
        if result.get("success"):
            pending_request = UserServiceRequest.objects.filter(user=request.user, is_accepted=False).exists()
            if pending_request:
                messages.error(request, 'درخواست قبلی شما هنوز بررسی نشده است.')
                return redirect('users:dashboard')

            title = request.POST['title']
            description = request.POST['description']
            group = request.POST['group']
            attachment = request.FILES.get('attachment')

            allowed_extensions = ['.pdf', '.zip', '.jpg', '.jpeg', '.webp', '.doc', '.docx']
            max_size = 5 * 1024 * 1024  # محدودیت حجم فایل به 5 مگابایت

            if attachment:
                ext = os.path.splitext(attachment.name)[1].lower()
                if ext not in allowed_extensions or attachment.size > max_size:
                    messages.error(request, 'فرمت یا حجم فایل نامعتبر است')
                    return redirect('service:pricing')

            group_map = {
                "1": "تنظیم لایحه",
                "2": "تنظیم دادخواست", 
                "3": "تنظیم شکواییه",
                "4": "تنظیم اظهارنامه"
            }
            group_title = group_map.get(group, "")
            jalali_date = jdatetime.datetime.now().date()
            end_service = jalali_date + timedelta(days=5)

            service = Service.objects.get(id=3)
            service_request = ServiceHandler.create_service_request(
                request.user, service, group_title, False,
                f'{title}--{description}',
                jalali_date, end_service,
                attachment=attachment
            )

            if service.price == 0:
                service_request.is_paid = True
                service_request.save()
                messages.success(request, 'درخواست با موفقیت ثبت شد')
                return redirect('users:dashboard')

            payment, authority_or_error = ServiceHandler.payment_request(
                request.user,
                service_request,
                f'پرداخت برای تنظیم {group_title}'
            )

            if payment:
                return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority_or_error}")
            else:
                messages.error(request, authority_or_error)
                return redirect('service:pricing')
        else:
            # خطا در کپچا
            messages.info(request, 'کپچا تأیید نشد!')
            return redirect('service:pricing')
@login_required
def Ekhtesasi(request):
    if request.method == 'POST':
        tarikh_ekhtesasi = request.POST['date']
        moddat_ekhtesasi = int(request.POST['duration'])

        jalali_date = jdatetime.datetime.strptime(tarikh_ekhtesasi, '%Y/%m/%d').date()
        now = timezone.localtime(timezone.now())
        current_date_shamsi = jdatetime.date.fromgregorian(date=now.date())

        if not ServiceHandler.validate_date(jalali_date, current_date_shamsi):
            messages.error(request, 'تاریخ انتخاب شده معتبر نیست')
            return redirect('service:pricing')

        end_service = jalali_date + timedelta(days=moddat_ekhtesasi)
        service = Service.objects.get(id=4)

        service_request = ServiceHandler.create_service_request(
            request.user, service, "وکیل اختصاصی", False,
            f'{moddat_ekhtesasi} روز همراهی وکیل اختصاصی',
            jalali_date, end_service
        )

        if service.price == 0:
            service_request.is_paid = True
            service_request.save()
            return redirect('users:dashboard')

        payment, authority_or_error = ServiceHandler.payment_request(
            request.user,
            service_request,
            f'پرداخت برای وکیل اختصاصی - {moddat_ekhtesasi} روز'
        )

        if payment:
            return redirect(f"https://www.zarinpal.com/pg/StartPay/{authority_or_error}")
        else:
            messages.error(request, authority_or_error)
            return redirect('service:pricing')


def check_authentication(request):
    return JsonResponse({'authenticated': request.user.is_authenticated})


