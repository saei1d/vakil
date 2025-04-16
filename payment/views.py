from django.shortcuts import render

from django.shortcuts import redirect, render
from django.conf import settings
from .models import Payment
from zarinpal import ZarinPal


# def payment_request(request):
#     # چاپ کاربر فعلی برای دیباگ
#     print(request.user)
    
#     # تعیین مبلغ ثابت 10000 تومان
#     amount = 10000
    
#     # ایجاد نمونه از کلاس ZarinPal با استفاده از merchant_id از تنظیمات
#     zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)

#     # ایجاد رکورد پرداخت جدید در دیتابیس
#     payment = Payment.objects.create(amount=amount, user=request.user)

#     # ارسال درخواست پرداخت به زرین‌پال
#     result = zarinpal.request({
#         'amount': amount,
#         'callback_url': settings.ZARINPAL_CALLBACK_URL,
#         'description': 'خرید تستی از سایت',
#     })

#     # بررسی نتیجه درخواست
#     if result.data.code == 100:
#         # ذخیره authority در رکورد پرداخت
#         payment.authority = result.data.authority
#         payment.save()
#         # هدایت کاربر به صفحه پرداخت زرین‌پال
#         return redirect(zarinpal.get_payment_link(result.data.authority))
#     else:
#         # نمایش خطا در صورت عدم موفقیت
#         return render(request, 'error.html', {
#             'message': result.data.message if hasattr(result, 'data') else 'خطای نامشخص'
#         })


# def payment_verify(request):
#     # دریافت پارامترهای ارسالی از زرین‌پال
#     authority = request.GET.get('Authority')
#     status = request.GET.get('Status')
    
#     # دریافت رکورد پرداخت مربوطه
#     payment = Payment.objects.get(authority=authority)

#     # بررسی وضعیت پرداخت
#     if status == 'OK':
#         # ایجاد نمونه از کلاس ZarinPal
#         zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
        
#         # درخواست تایید پرداخت با فرمت صحیح
#         result = zarinpal.verify(
#             {
#                 'amount': payment.amount,
#                 'authority': authority,
#             }
#         )

#         # بررسی نتیجه تایید پرداخت
#         if result.data.code == 100:
#             # بروزرسانی وضعیت پرداخت به موفق
#             payment.is_paid = True
#             payment.save()
#             # نمایش صفحه موفقیت با کد پیگیری
#             return render(request, 'payment/success.html', {'ref_id': result.data.ref_id})
#         else:
#             # نمایش خطا در صورت عدم موفقیت
#             return render(request, 'error.html', {'message': result.data.message})
#     else:
#         # نمایش خطا در صورت لغو پرداخت توسط کاربر
#         return render(request, 'error.html', {'message': 'پرداخت توسط کاربر لغو شد.'})
