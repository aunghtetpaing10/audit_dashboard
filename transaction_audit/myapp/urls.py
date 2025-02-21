from django.urls import path
from . import views

urlpatterns = [
    path('api/transactions/', views.TransactionListView.as_view(), name='transaction-list')
]