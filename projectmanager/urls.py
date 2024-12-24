from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import login_redirect, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_redirect, name='home'),  # Redirige vers login ou dashboard
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include('core.urls')),
]