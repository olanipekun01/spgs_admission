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
    path('apply/dashboard/', views.dashboard, name="dashboard"),
    path('apply/payment/', views.ApplyPayment, name='applypayment'),
    path('payment_confirm/', views.ApplyPaymentConfirm, name='payment_confirm'),
    path('apply/1/', views.ApplyOne, name="applyone"),
    path('apply/2/', views.ApplyTwo, name="applytwo"),
    path('apply/3/', views.ApplyThree, name="applythree"),

    path('apply/4/', views.ApplyFour, name="applyfour"),
    path('cred/delete/<str:id>/', views.CredDelete, name="cred_delete"),
    path('cred/update/', views.CredUpdate, name="cred_update"),
    
    path('apply/5/', views.ApplyFive, name="applyfive"),
    path('apply/6/', views.ApplySix, name="applysix"),
    path('ref/delete/<str:id>/', views.RefDelete, name="ref_delete"),
    path('ref/update/', views.RefUpdate, name="ref_update"),

    path('apply/7/', views.ApplySeven, name="applyseven"),
    path('apply/8/', views.ApplyEight, name='apply_eight'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('apply/review/', views.application_review, name='application_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
                          document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)