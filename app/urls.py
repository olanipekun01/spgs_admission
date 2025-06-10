from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import handler404
from django.shortcuts import render

# Define the custom 404 view
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Set the handler for 404 errors
handler404 = custom_404_view


app_name = "app"

urlpatterns = [
    path('accounts/login/', views.Login, name="login"),
    path('accounts/signup/', views.Signup, name="signup"),
    path('accounts/logout/', views.logout, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
                          document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)