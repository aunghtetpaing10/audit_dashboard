from django.views.generic import ListView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

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

