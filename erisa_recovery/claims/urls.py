# claims/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.claim_list, name='claim_list'),
    path('claim/<int:claim_id>/detail/', views.claim_detail, name='claim_detail'),
    path('claim/<int:claim_id>/toggle-flag/', views.flag_claim, name='flag_claim'),
    path('claim/<int:claim_id>/save-notes/', views.save_note, name='save_note'),
]
