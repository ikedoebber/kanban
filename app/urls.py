from django.contrib import admin
from django.urls import path, include
from .views import main_dashboard, login_view, logout_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_dashboard, name='main_dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tasks/', include('tasks.urls')),
    path('goals/', include('goals.urls')),
    path('appointments/', include('appointments.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
