from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('checkin/', views.checkin_view, name='checkin'),
    path('scan/', views.scan_qr_code_view, name='scan_qr'),
    
]
