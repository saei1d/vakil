from datetime import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from blog.models import Post
from service.models import UserServiceRequest, Service,FreeForm
from users.models import Client
import logging
from payment.models import Payment



# Set up logging
logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is a superuser or staff"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_userlist(request):

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

        return render(request, 'users/admin_userlist.html', context)

    except Exception as e:
        logger.error(f"Error in user_list view: {str(e)}")
        messages.error(request, "خطایی در نمایش لیست کاربران رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('admin_userlist')


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
        return redirect('admin_userlist')



@login_required
@user_passes_test(is_admin)
def admin_userupdate_service(request, id):

        print(id)
        service = UserServiceRequest.objects.get(id=id)
        print(service)
        if request.method == 'POST':
            print(1111111111111111)
            # Get form data with validation
            title = request.POST.get('title')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == '1'
            is_accepted = request.POST.get('is_accepted') == '1'
            is_paid = request.POST.get('is_paid') == '1'

            # Update service
            service.title = title
            service.start_date = start_date
            service.end_date = end_date
            service.description = description
            service.is_active = is_active
            service.is_accepted = is_accepted
            service.is_paid = is_paid
            service.save()

            messages.success(request, "سرویس با موفقیت به‌روزرسانی شد.")
            return redirect('admin_userinfo', id=service.user.id)

        context = {
            'service': service,
        }
        print(context)
        print(333333333333333)

        return render(request, 'users/admin_userupdate_service.html', context)

    # except Exception as e:
    #     logger.error(f"Error in admin_userupdate_service view for service {id}: {str(e)}")
    #     messages.error(request, "خطایی در به‌روزرسانی سرویس رخ داد. لطفا دوباره تلاش کنید.")
    #     return redirect('admin_userlist')


@login_required
@user_passes_test(is_admin)
def admin_useradd_service(request, username):
    """
    Add a new service for a user.
    Only accessible to admin users.
    """
    try:
        user = get_object_or_404(Client, username=username)
        
        if request.method == 'POST':
            # Get form data
            title = request.POST.get('title')
            service_type = request.POST.get('service_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == '1'
            is_accepted = request.POST.get('is_accepted') == '1'
            is_paid = request.POST.get('is_paid') == '1'
            
            print("=== DEBUG INFO ===")
            print(f"Title: {title}")
            print(f"Service Type: {service_type}")
            print(f"Start Date (raw): {start_date}")
            print(f"End Date (raw): {end_date}")
            print(f"Description: {description}")
            print(f"Is Active: {is_active}")
            print(f"Is Accepted: {is_accepted}")
            print(f"Is Paid: {is_paid}")
            
            # Validate required fields
            if not all([title, service_type, start_date, end_date]):
                print("Missing required fields!")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'لطفا تمام فیلدهای ضروری را پر کنید'
                    })
                messages.error(request, "لطفا تمام فیلدهای ضروری را پر کنید")
                return redirect('admin_userinfo', id=user.id)
            
            try:
                # Get service type object
                print(f"Looking for service with ID: {service_type}")
                service = get_object_or_404(Service, id=service_type)
                print(f"Found service: {service}")
                
                # Parse dates and make them timezone-aware
                from django.utils.dateparse import parse_datetime
                start_date = parse_datetime(start_date)
                end_date = parse_datetime(end_date)
                
                print(f"Start Date (parsed): {start_date}")
                print(f"End Date (parsed): {end_date}")
                
                if not start_date or not end_date:
                    print("Invalid date format!")
                    raise ValueError('Invalid date format')
                
                if not timezone.is_aware(start_date):
                    start_date = timezone.make_aware(start_date)
                if not timezone.is_aware(end_date):
                    end_date = timezone.make_aware(end_date)
                
                print(f"Start Date (aware): {start_date}")
                print(f"End Date (aware): {end_date}")
                
                print("Creating UserServiceRequest with:")
                print(f"User: {user}")
                print(f"Service: {service}")
                print(f"Title: {title}")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                print(f"Description: {description}")
                print(f"Is Active: {is_active}")
                print(f"Is Accepted: {is_accepted}")
                print(f"Is Paid: {is_paid}")
                
                # Create new service request
                new_service = UserServiceRequest.objects.create(
                    user=user,
                    service=service,
                    title=title,
                    start_date=start_date,
                    end_date=end_date,
                    description=description,
                    is_active=is_active,
                    is_accepted=is_accepted,
                    is_paid=is_paid
                )
                print(f"Successfully created service request with ID: {new_service.id}")
                
                messages.success(request, "سرویس با موفقیت اضافه شد")
                return redirect('admin_userinfo', id=user.id)
                
            except Service.DoesNotExist:
                print("Service does not exist!")
                messages.error(request, "نوع سرویس انتخاب شده معتبر نیست")
                return redirect('admin_userinfo', id=user.id)
            except Exception as e:
                print(f"Error creating service: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print("Full traceback:")
                print(traceback.format_exc())
                messages.error(request, f"خطا در ایجاد سرویس: {str(e)}")
                return redirect('admin_userinfo', id=user.id)
            
        context = {
            'user': user,
            'available_services': Service.objects.all()
        }
        
        return render(request, 'users/admin_useradd_service.html', context)
        
    except Exception as e:
        logger.error(f"Error in add_service view for user {username}: {str(e)}")
        messages.error(request, "خطایی در ثبت سرویس رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('admin_userlist')


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
        return redirect('admin_userlist')


def admin_blogs(request):
    
    uncomplete_blogs = Post.objects.filter(is_published=False)
    complete_blogs = Post.objects.filter(is_published=True)
    context = {
        'uncomplete_blogs': uncomplete_blogs,
        'complete_blogs': complete_blogs
    }
    return render(request, 'users/admin_blogs.html', context)



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
        
        return redirect('admin_userinfo', id=user.id)        
        
    except Exception as e:
        logger.error(f"خطا در ارتقای کاربر {username}: {str(e)}")
        messages.error(request, "خطایی در تغییر وضعیت کاربر رخ داد. لطفا دوباره تلاش کنید.")
        return redirect('admin_userlist')
    



def delete_blog(request , id):
    if request.user.is_staff:
        blog = get_object_or_404(Post, id=id)  # فرض بر این است که مدل Blog وجود دارد
        blog.delete()
        messages.success(request, "بلاگ با موفقیت حذف شد.")
    else:
        messages.error(request, "شما مجوز لازم برای حذف بلاگ را ندارید.")
    return redirect('admin_userlist')


def admindashboard(request):
    users = Client.objects.all()
    payments = Payment.objects.all()
    blogs = Post.objects.all()
    services = Service.objects.all()
    UserService = UserServiceRequest.objects.all()

    context = {
        'users': users,
        'payments': payments,
        'blogs': blogs,
        'services': services,
        'UserServiceRequest':UserService,
    }
    
    return render(request, 'users/admin_dashboard.html', context)



@login_required
@user_passes_test(is_admin)
def admin_userinfo(request,id):
    user = get_object_or_404(Client, id=id)
    user_services = UserServiceRequest.objects.filter(user=user)
    payments = Payment.objects.filter(user=user)
    available_services = Service.objects.all()

    context = {
        'user': user,
        'user_services': user_services,
        'payments': payments,
        'available_services': available_services,
    }
    
    return render(request, 'users/admin_userinfo.html', context)


def update_user_info(request,id):
    
    user = get_object_or_404(Client, id=id)
    if request.method == 'POST':
        
        # دریافت داده‌های فرم
        first_name = request.POST.get('name', user.name)
        last_name = request.POST.get('last_name', user.last_name)
        # phone = request.POST.get('phone', user.phone)
        print(first_name,last_name)
        # به‌روزرسانی اطلاعات کاربر
        user.name = first_name
        user.last_name = last_name
        # user.phone = phone
        
        # ذخیره تغییرات
        user.save()
        messages.success(request, 'اطلاعات کاربر با موفقیت به‌روزرسانی شد.')
    else:
        messages.error(request, 'درخواست نامعتبر است.')
    
    return redirect('admin_userinfo', id=user.id)




@login_required
@user_passes_test(is_admin)
def admin_add_payment(request,username):
    user = get_object_or_404(Client, username=username)
    if request.method == 'POST':
        try:
            # دریافت و اعتبارسنجی مقادیر
            service_request_id = request.POST.get('service_request')
            if not service_request_id:
                messages.error(request, 'سرویس نمی‌تواند خالی باشد')
                return redirect('admin_userinfo', id=user.id)
                
            service_request = get_object_or_404(UserServiceRequest, id=service_request_id)
            if service_request.user != user:
                messages.error(request, 'این سرویس متعلق به این کاربر نیست')
                return redirect('admin_userinfo', id=user.id)
            
            amount = request.POST.get('amount')
            if not amount:
                messages.error(request, 'مبلغ نمی‌تواند خالی باشد')
                return redirect('admin_userinfo', id=user.id)
            
            try:
                amount = int(amount)
                if amount <= 0:
                    messages.error(request, 'مبلغ باید بزرگتر از صفر باشد')
                    return redirect('admin_userinfo', id=user.id)
            except ValueError:
                messages.error(request, 'مبلغ باید عدد صحیح باشد')
                return redirect('admin_userinfo', id=user.id)
            
            transaction_type = request.POST.get('transaction_type')
            if transaction_type not in ['deposit', 'withdraw']:
                messages.error(request, 'نوع تراکنش نامعتبر است')
                return redirect('admin_userinfo', id=user.id)
                
            is_paid = request.POST.get('is_paid', False) == 'on'
            
            # ایجاد تراکنش
            Payment.objects.create(
                user=user,
                service_request=service_request,
                amount=amount,
                transaction_type=transaction_type,
                is_paid=is_paid,
                created_at=timezone.now()
            )
            
            messages.success(request, 'تراکنش با موفقیت ایجاد شد')
            return redirect('admin_userinfo', id=user.id)
            
        except Exception as e:
            logger.error(f"Error in admin_add_payment view: {str(e)}")
            messages.error(request, f'خطا در ایجاد تراکنش: {str(e)}')
            return redirect('admin_userinfo', id=user.id)
            
    return redirect('admin_userinfo', id=user.id)


@login_required
@user_passes_test(is_admin)
def admin_services(request):
    services = Service.objects.all()
    context = {
        'services': services,
    }
    return render(request, 'users/admin_services.html', context)


@login_required
@user_passes_test(is_admin)
def admin_add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        
        try:
            price = int(price)
            if price < 0:
                messages.error(request, 'قیمت باید بزرگتر از صفر باشد')
                return redirect('admin_services')
        except ValueError:
            messages.error(request, 'قیمت باید عدد صحیح باشد')
            return redirect('admin_services')
            
        if not name:
            messages.error(request, 'نام سرویس الزامی است')
            return redirect('admin_services')
            
        Service.objects.create(
            name=name,
            description=description,
            price=price
        )
        messages.success(request, 'سرویس با موفقیت ایجاد شد')
        return redirect('admin_services')
        
    return redirect('admin_services')


@login_required
@user_passes_test(is_admin)
def admin_edit_service(request, id):
    service = get_object_or_404(Service, id=id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        
        try:
            price = int(price)
            if price < 0:
                messages.error(request, 'قیمت باید بزرگتر از صفر باشد')
                return redirect('admin_services')
        except ValueError:
            messages.error(request, 'قیمت باید عدد صحیح باشد')
            return redirect('admin_services')
            
        if not name:
            messages.error(request, 'نام سرویس الزامی است')
            return redirect('admin_services')
            
        service.name = name
        service.description = description
        service.price = price
        service.save()
        
        messages.success(request, 'سرویس با موفقیت به‌روزرسانی شد')
        return redirect('admin_services')
        
    context = {
        'service': service,
        'page_title': 'ویرایش سرویس'
    }
    return render(request, 'users/admin_edit_service.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_service(request, id):
    service = get_object_or_404(Service, id=id)
    service.delete()
    messages.success(request, 'سرویس با موفقیت حذف شد')
    return redirect('admin_services')


@login_required
@user_passes_test(is_admin)
def admin_user_services(request):
    # Get all types of user services ordered by creation date (newest first)
    user_services = UserServiceRequest.objects.all().order_by('-created_at')

    free_form_requests = FreeForm.objects.all().order_by('-created_at')

    context = {
        'user_services': user_services,
        'free_form_requests': free_form_requests,
    }
    return render(request, 'users/admin_user_services.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_payments(request):
    # Get all types of user services ordered by creation date (newest first)
    payments = Payment.objects.all().order_by('-created_at')

    context = {
        'payments': payments,
    }
    return render(request, 'users/admin_user_payments.html', context)