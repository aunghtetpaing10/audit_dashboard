from django.views.generic import ListView
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from .models import Transaction
from .serializers import TransactionSerializer, TransactionApproveSerializer, TransactionToggleFlagSerializer

class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    permission_classes = [permissions.IsAuthenticated]
    
class TransactionApproveView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionApproveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        instance = serializer.instance
        
        if instance.status == 'failed':
            raise ValidationError("Cannot update a failed transaction.")
        elif instance.status == 'completed':
            raise ValidationError("Cannot update a completed transaction.")
        elif instance.status == 'pending':
            instance.status = 'completed'
            instance.approved_by = self.request.user
        
        serializer.save()
        
class TransactionToggleFlagView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionToggleFlagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        instance = serializer.instance
        
        instance.is_flagged = not instance.is_flagged
        serializer.save()
        

class DashboardView(ListView):
    model = Transaction
    template_name = 'myapp/dashboard.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.all()
        status = self.request.GET.get('status')
        merchant = self.request.GET.get('merchant')

        if status:
            queryset = queryset.filter(status=status)
        if merchant:
            queryset = queryset.filter(merchant__icontains=merchant)

        return queryset

