from django.urls import path
from . import views

app_name = 'billetapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_billet, name='create_billet'),
    path('scan/<int:pk>/', views.scan_billet, name='scan_billet'),
    path('billets/', views.liste_billets, name='liste_billets'),
    path('billet/<int:billet_id>/pdf/', views.telecharger_billet_pdf, name='telecharger_billet_pdf'),
]
