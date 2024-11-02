
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request):
    user = request.user
    if user.status_vakil == 'inactive':
        return render(request, 'chat/chat.html')
    else:
        return redirect('account_inactive')
