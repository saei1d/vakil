from django.contrib.sitemaps import Sitemap
from service.models import Service
from django.urls import reverse
from blog.models import Post


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['users:home', 'blog:about-us', 'service','blog:faq']  # اسم viewهایی که URL دارن و ثابتن

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Service.objects.all()

    def location(self, obj):
        # حالا باید از اسم URLهای موجود برای هر سرویس استفاده کنیم
        if obj.name == 'call':
            return reverse('service:call')
        elif obj.name == 'payam':
            return reverse('service:payam')
        elif obj.name == 'shekaiatname':
            return reverse('service:shekaiatname')
        elif obj.name == 'ekhtesasi':
            return reverse('service:ekhtesasi')
        else:
            return reverse('service:pricing')  # مسیر پیش‌فرض

    

class PostSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return Post.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('blog:blogpage', kwargs={'slug': obj.slug})
