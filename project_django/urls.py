"""project_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, logout_view, dashboard_view, get_csrf_token, profil_view, get_security_question, verify_security_answer, change_password, get_sidebar_role, check_role_dashboard
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/buatAkun/', include('buatAkun.urls')),
    path('api/daftarAkun/', include('daftarAkun.urls')),
    path('', login_view, name="login"), # Ini akan menangani root URL tanpa /api/
    path('api/accounts/', include('accounts.urls')),
    path('api/', login_view, name="login"), # Ini akan menangani /api/ sebagai login page
    path('api/get-security-question/', get_security_question, name='get_security_question'),
    path('api/verify-security-answer/', verify_security_answer, name='verify_security_answer'),
    path('api/change-password/', change_password, name='change_password'),
    path('api/profil/', profil_view, name="profil"),
    path('api/login/', login_view, name="login"), # Duplikasi? Pertimbangkan untuk menghapusnya jika path '/' atau '/api/' sudah cukup.
    path('api/logout/', logout_view, name="logout"),
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('api/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('api/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('api/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('api/survei/',include('survei.urls')),
    path('api/klien/', include('klien.urls')), # <<< INI SUDAH BENAR & PENTING!
    path('api/survei-status/', include('tracker_survei.urls')),
    path('api/dokumen_pendukung/', include('dokumen_pendukung.urls')), # Pastikan tidak tumpang tindih dengan klien/urls
    path('api/souvenir/', include('souvenir.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/daftarDokumen/', include('daftarDokumen.urls')), # Pastikan tidak tumpang tindih dengan klien/urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)