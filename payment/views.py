from django.shortcuts import render

from django.shortcuts import redirect, render
from django.conf import settings
from .models import Payment
from zarinpal import ZarinPal


def payment_request(request):
    print(request.user)
    amount = 10000
    zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)

    payment = Payment.objects.create(amount=amount, user=request.user)

    result = zarinpal.request({'amount': amount,'callback_url': settings.ZARINPAL_CALLBACK_URL,'description': 'خرید تستی از سایت',})

    if result.data.code == 100:
        payment.authority = result.data.authority
        payment.save()
        return redirect(zarinpal.get_payment_link(result.data.authority))
    else:
        return render(request, 'error.html', {
            'message': result.data.message if hasattr(result, 'data') else 'خطای نامشخص'
        })


def payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    payment = Payment.objects.get(authority=authority)

    if status == 'OK':
        zarinpal = ZarinPal(merchant_id=settings.ZARINPAL_MERCHANT_ID)
        result = zarinpal.payment_verification(
            amount=payment.amount,
            authority=authority,
        )

        if result['status'] == 100:
            payment.is_paid = True
            payment.save()
            return render(request, 'success.html', {'ref_id': result['ref_id']})
        else:
            return render(request, 'error.html', {'message': result['error']})
    else:
        return render(request, 'error.html', {'message': 'پرداخت توسط کاربر لغو شد.'})
