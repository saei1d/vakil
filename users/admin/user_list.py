from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from blog.models import Post
from service.models import UserServiceRequest, Service
from users.models import Client
import logging

# Set up logging
logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is a superuser or staff"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """
    Display a list of users with search and pagination functionality.
    Only accessible to admin users.
    """

    try:
        # Search functionality
        search_query = request.POST.get('pk', '') if request.method == "POST" else request.GET.get('search', '')

        if search_query:
            users = Client.objects.filter(
                Q(username__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query)
            ).order_by('-date_joined')
        else:
            users = Client.objects.all().order_by('-date_joined')  # Sort by newest first

        # Pagination
        page_number = request.GET.get('page', 1)
        items_per_page = 25  # Number of users per page

        paginator = Paginator(users, items_per_page)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'total_users': users.count(),
        }

        return render(request, 'users/userlist.html', context)

    except Exception as e:
        logger.error(f"Error in user_list view: {str(e)}")
        messages.error(request, "خطایی در نمایش لیست کاربران رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')


@login_required
@user_passes_test(is_admin)
def service(request):
    """
    مدیریت کامل سرویس‌ها شامل ایجاد، ویرایش، حذف و نمایش لیست سرویس‌ها
    فقط برای مدیران قابل دسترسی است.
    """
    try:
        if request.method == 'POST':
            # ایجاد سرویس جدید
            if 'add_service' in request.POST:
                name = request.POST.get('name')
                price = request.POST.get('price')
                
                if not name or not price:
                    messages.error(request, "لطفا تمام فیلدها را پر کنید")
                    return redirect('service')
                
                Service.objects.create(name=name, price=price)
                messages.success(request, "سرویس با موفقیت ایجاد شد")
                return redirect('service')
            
            # حذف سرویس
            elif 'delete_service' in request.POST:
                service_id = request.POST.get('service_id')
                service = get_object_or_404(Service, id=service_id)
                service.delete()
                messages.success(request, "سرویس با موفقیت حذف شد")
                return redirect('service')
            
            # ویرایش سرویس
            elif 'edit_service' in request.POST:
                service_id = request.POST.get('service_id')
                service = get_object_or_404(Service, id=service_id)
                service.name = request.POST.get('name')
                service.price = request.POST.get('price')
                service.save()
                messages.success(request, "سرویس با موفقیت ویرایش شد")
                return redirect('service')
        
        # نمایش لیست سرویس‌ها
        services = Service.objects.all()
        context = {
            'services': services,
            'SERVICE_CHOICES': Service.SERVICE_CHOICES,
        }
        return render(request, 'users/admin_service.html', context)
    
    except Exception as e:
        logger.error(f"خطا در مدیریت سرویس‌ها: {str(e)}")
        messages.error(request, "خطایی در مدیریت سرویس‌ها رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')

@login_required
@user_passes_test(is_admin)
def service_list(request, username):
    """
    Display a list of services for a specific user.
    Only accessible to admin users.
    """
    try:
        user = get_object_or_404(Client, username=username)
        services = UserServiceRequest.objects.filter(user=user).order_by('-start_date')
        available_services = Service.objects.all()

        context = {
            'services': services,
            'user': user,
            'available_services': available_services,
        }

        return render(request, 'users/servicelist.html', context)

    except Exception as e:
        logger.error(f"Error in service_list view for user {username}: {str(e)}")
        messages.error(request, "خطایی در نمایش لیست سرویس‌ها رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')


@login_required
@user_passes_test(is_admin)
def update_service(request, pk):
    """
    Update a service for a user.
    Only accessible to admin users.
    """
    try:
        service = get_object_or_404(UserServiceRequest, id=pk)

        if request.method == 'POST':
            # Get form data with validation
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            is_active = request.POST.get('is_active') == '1'
            is_accepted = request.POST.get('is_accepted') == '1'
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')

            # Update service
            service.start_date = start_date
            service.end_date = end_date
            service.is_active = is_active
            service.is_accepted = is_accepted
            service.title = title
            service.description = description

            service.save()

            messages.success(request, "سرویس با موفقیت به‌روزرسانی شد.")
            return redirect('servicelist', username=service.user.username)

        context = {
            'service': service,
        }

        return render(request, 'users/update_service.html', context)

    except Exception as e:
        logger.error(f"Error in update_service view for service {pk}: {str(e)}")
        messages.error(request, "خطایی در به‌روزرسانی سرویس رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')


@login_required
@user_passes_test(is_admin)
def add_service(request, username):
    """
    Add a new service for a user.
    Only accessible to admin users.
    """
    try:
        user = get_object_or_404(Client, username=username)
        available_services = Service.objects.all()

        if request.method == 'POST':
            service_id = request.POST.get('service')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')

            service_type = get_object_or_404(Service, id=service_id)

            # Create new service
            new_service = UserServiceRequest(
                user=user,
                service=service_type,
                start_date=start_date,
                end_date=end_date,
                title=title,
                description=description,
                is_active=True,
                is_accepted=True
            )

            new_service.save()

            messages.success(request, "سرویس جدید با موفقیت اضافه شد.")
            return redirect('servicelist', username=username)

        context = {
            'user': user,
            'available_services': available_services,
        }

        return render(request, 'users/add_service.html', context)

    except Exception as e:
        logger.error(f"Error in add_service view for user {username}: {str(e)}")
        messages.error(request, "خطایی در افزودن سرویس جدید رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('servicelist', username=username)


@login_required
@user_passes_test(is_admin)
def delete_service(request, pk):
    """
    Delete a service.
    Only accessible to admin users.
    """
    try:
        service = get_object_or_404(UserServiceRequest, id=pk)
        username = service.user.username

        service.delete()

        messages.success(request, "سرویس با موفقیت حذف شد.")
        return redirect('servicelist', username=username)

    except Exception as e:
        logger.error(f"Error in delete_service view for service {pk}: {str(e)}")
        messages.error(request, "خطایی در حذف سرویس رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')


def uncomplete_blog(request):
    if request.user.is_staff:
        blogs = Post.objects.filter(is_published=False)
        return render(request, 'users/blog_uncomplete.html', {'blogs': blogs})
    else:
        return redirect('users:login')



@login_required
@user_passes_test(is_admin)
def promote_user(request, username):
    """
    ارتقای کاربر به وضعیت کارمند، سوپر یوزر یا برگرداندن به کاربر عادی.
    فقط برای مدیران قابل دسترسی است.
    """
    print(username)
    try:
        user = get_object_or_404(Client, username=username)
        print(user)
        
        # چرخه ارتقا: کاربر عادی -> کارمند -> سوپر یوزر -> کاربر عادی
        if not user.is_staff and not user.is_superuser:
            # کاربر عادی به کارمند تبدیل می‌شود
            user.is_staff = True
            user.is_superuser = False
            status_message = "ارتقا یافت به کارمند"
        elif user.is_staff and not user.is_superuser:
            # کارمند به سوپر یوزر تبدیل می‌شود
            user.is_staff = True
            user.is_superuser = True
            status_message = "ارتقا یافت به سوپر یوزر"
        else:
            # سوپر یوزر به کاربر عادی تبدیل می‌شود
            user.is_staff = False
            user.is_superuser = False
            status_message = "به کاربر عادی تبدیل شد"
        
        user.save()
        
        messages.success(request, f"کاربر {user.username} با موفقیت {status_message}.")
        
        return redirect('userlist')
        
    except Exception as e:
        logger.error(f"خطا در ارتقای کاربر {username}: {str(e)}")
        messages.error(request, "خطایی در تغییر وضعیت کاربر رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('userlist')
    



def delete_blog(request , id):
    if request.user.is_staff:
        blog = get_object_or_404(Post, id=id)  # فرض بر این است که مدل Blog وجود دارد
        blog.delete()
        messages.success(request, "بلاگ با موفقیت حذف شد.")
    else:
        messages.error(request, "شما مجوز لازم برای حذف بلاگ را ندارید.")
    return redirect('userlist')