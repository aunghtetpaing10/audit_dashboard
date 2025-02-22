from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Transaction
from .serializers import TransactionSerializer, TransactionApproveSerializer, TransactionToggleFlagSerializer
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json

class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
class TransactionApproveView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionApproveSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def perform_update(self, serializer):
        instance = self.get_object()
        
        if instance.status == 'failed':
            raise ValidationError("Cannot update a failed transaction.")
        elif instance.status == 'completed':
            raise ValidationError("Cannot update a completed transaction.")
        
        serializer.save(status='completed', approved_by=self.request.user)
        
    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
            # Get the updated instance
            instance = self.get_object()
            # Render just the row HTML with the same ID
            html = render_to_string(request,'myapp/transaction_row.html', {'transaction': instance})
            return Response(html, content_type='text/html')
        except ValidationError as e:
            return Response(str(e), status=400)

class TransactionToggleFlagView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionToggleFlagSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def perform_update(self, serializer):
        instance = self.get_object()
        
        if instance.is_flagged:
            raise ValidationError("Transaction is already flagged.")
        
        serializer.save(is_flagged=True)

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
            # Get the updated instance
            instance = self.get_object()
            # Render just the row HTML with the same ID
            html = render_to_string(request,'myapp/transaction_row.html', {'transaction': instance})
            return Response(html, content_type='text/html')
        except ValidationError as e:
            return Response(str(e), status=400)

class LoginPage(LoginView):
    template_name = 'myapp/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(self.request.user)
        
        # Store tokens in session
        self.request.session['access_token'] = str(refresh.access_token)
        self.request.session['refresh_token'] = str(refresh)
        
        return response

def logout_view(request):
    # Clear JWT tokens from session
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    
    # Logout user
    logout(request)
    return redirect('login')

@method_decorator(login_required(login_url='login'), name='dispatch')
class DashboardView(ListView):
    model = Transaction
    template_name = 'myapp/dashboard.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-timestamp')
        status = self.request.GET.get('status')
        merchant = self.request.GET.get('merchant')

        if status:
            queryset = queryset.filter(status=status)
        if merchant:
            queryset = queryset.filter(merchant__icontains=merchant)

        return queryset

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['myapp/transaction_list.html']
        return [self.template_name]

@csrf_protect
@require_http_methods(["POST"])
def refresh_token(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({'error': 'Refresh token required'}, status=400)
            
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return JsonResponse({
            'access': access_token,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_protect
@require_http_methods(["POST"])
def update_token(request):
    try:
        data = json.loads(request.body)
        access_token = data.get('access')
        
        if not access_token:
            return JsonResponse({'error': 'Access token required'}, status=400)
            
        # Update the session
        request.session['access_token'] = access_token
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

