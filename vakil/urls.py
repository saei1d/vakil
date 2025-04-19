from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from users.views import robots_txt



from django.contrib.sitemaps.views import sitemap
from users.sitemap import StaticViewSitemap, ServiceSitemap , PostSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'posts': PostSitemap,
}



urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),  # مسیر چت را اضافه کنید

    path('', include('users.urls')),
    path('adminpanel/', include('users.admin.urls')),
    path('', include('service.urls')),
    path('', include('blog.urls')),

    path('payment/', include('payment.urls')),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('robots.txt', robots_txt, name='robots_txt'),

    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="sitemap"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
