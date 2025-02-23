from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Transaction
from .serializers import TransactionSerializer
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from django.db.models import Sum, Count
import plotly.graph_objects as go

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
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_transaction(request, pk):
    if request.method != 'PUT':
        return HttpResponseForbidden()
        
    try:
        transaction = Transaction.objects.get(pk=pk)
        
        if transaction.status == 'failed':
            return HttpResponse("Cannot update a failed transaction.", status=400)
        elif transaction.status == 'completed':
            return HttpResponse("Cannot update a completed transaction.", status=400)
            
        transaction.status = 'completed'
        transaction.approved_by = request.user
        transaction.save()
        
        html = render_to_string('myapp/transaction_row.html', {
            'transaction': transaction,
            'request': request
        })
        return HttpResponse(html)
    except Transaction.DoesNotExist:
        return HttpResponse("Transaction not found", status=404)
    except Exception as e:
        return HttpResponse(str(e), status=400)

@login_required
def toggle_flag_transaction(request, pk):
    if request.method != 'PUT':
        return HttpResponseForbidden()
        
    try:
        transaction = Transaction.objects.get(pk=pk)
        
        if transaction.is_flagged:
            return HttpResponse("Transaction is already flagged.", status=400)
            
        transaction.is_flagged = True
        transaction.save()
        
        html = render_to_string('myapp/transaction_row.html', {
            'transaction': transaction,
            'request': request
        })
        return HttpResponse(html)
    except Transaction.DoesNotExist:
        return HttpResponse("Transaction not found", status=404)
    except Exception as e:
        return HttpResponse(str(e), status=400)

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
        queryset = Transaction.objects.all()
        status = self.request.GET.get('status')
        merchant = self.request.GET.get('merchant')

        if status:
            queryset = queryset.filter(status=status)
        if merchant:
            queryset = queryset.filter(merchant__icontains=merchant)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get status totals
        status_totals = Transaction.objects.values('status').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('status')
        
        # Get merchant totals
        merchant_totals = Transaction.objects.values('merchant').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('-total_amount')[:10]
        
        # Status Distribution Pie Chart
        status_labels = [item['status'].title() for item in status_totals]
        status_values = [float(item['total_amount']) for item in status_totals]
        status_counts = [item['count'] for item in status_totals]
        
        status_pie = go.Figure(data=[
            go.Pie(
                labels=status_labels,
                values=status_values,
                hole=0.6,
                textinfo='percent',
                hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Count: %{customdata:,}<extra></extra>",
                customdata=status_counts,
                marker=dict(
                    colors=['#FCD34D', '#34D399', '#F87171']  # yellow, green, red
                )
            )
        ])
        status_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=0, b=50, l=0, r=0),
            height=350,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        # Top Merchants Bar Chart
        merchant_bar = go.Figure(data=[
            go.Bar(
                x=[item['merchant'] for item in merchant_totals],
                y=[float(item['total_amount']) for item in merchant_totals],
                marker_color='#60A5FA',
                text=[f"${float(item['total_amount']):,.2f}" for item in merchant_totals],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.2f}<extra></extra>",
            )
        ])
        merchant_bar.update_layout(
            xaxis_title=None,
            yaxis_title='Total Amount ($)',
            margin=dict(t=0, b=80, l=50, r=20),
            height=350,
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                gridcolor='#E5E7EB',
                showgrid=True,
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            bargap=0.3
        )
        
        context.update({
            'status_totals': status_totals,
            'merchant_totals': merchant_totals,
            'status_chart': status_pie.to_json(),
            'merchant_chart': merchant_bar.to_json(),
        })
        
        return context

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