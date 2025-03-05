from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('api/transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('api/transactions/<int:pk>/approve/', views.approve_transaction, name='approve-transaction'),
    path('api/transactions/<int:pk>/toggle/', views.toggle_flag_transaction, name='toggle-flag'),
    path('api/transactions/<int:pk>/history/', views.transaction_history, name='transaction-history'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='get-token'),
    path('api/token/refresh/', views.refresh_token, name='refresh-token'),
    path('api/token/update/', views.update_token, name='update-token'),
    
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout')
]