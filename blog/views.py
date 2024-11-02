from django.shortcuts import render


# Create your views here.


def aboutus(request):
    return render(request, 'blog/about.html')


def faq(request):
    return render(request, 'blog/faq.html')


def blog(request):
    return render(request, 'blog/blog.html')


def contact(request):
    return render(request, 'blog/contact.html')
