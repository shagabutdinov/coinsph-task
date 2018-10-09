from django.urls import path
from payments import views

urlpatterns = [
    path('v1/accounts', views.accounts, name='accounts'),
    path('v1/payments', views.payments, name='payments'),
]
